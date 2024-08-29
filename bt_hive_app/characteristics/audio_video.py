import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import bt_hive_app.helper_methods as help
from pydub import AudioSegment
import time


class FileInfoCharacteristic(Characteristic):
    def __init__(self, service, uuid, file_path, file_type):
        super().__init__(
            uuid,
            ['read'],
            service)
        self.file_path = file_path
        self.file_type = file_type

    def ReadValue(self, options):
        temp_file_path = self.file_path

        if self.file_type == 'audio':
            temp_file_path = help.get_most_recent_audio_file(temp_file_path)
        elif self.file_type == 'video':
            temp_file_path = help.get_most_recent_video_file(temp_file_path)

        
        print("FILE PATH: ", temp_file_path)

        file_size_wav = os.path.getsize(temp_file_path)

        if temp_file_path.endswith('.wav'):
            audio = AudioSegment.from_wav(temp_file_path)
            mp3_file_name = os.path.basename(temp_file_path).replace('.wav', '.mp3')
            mp3_file_path = os.path.join('/home/bee/GATT_server', mp3_file_name)
            audio.export(mp3_file_path, format='mp3')
            file_size_mp3 = os.path.getsize(mp3_file_path)
            os.remove(mp3_file_path)

            rms_level, silence_detected = self.calculate_rms_and_check_silence(audio)
        else:
            file_size_mp3 = 0
            rms_level = 0
            silence_detected = False

        file_info = (f"{temp_file_path}, File Size: {file_size_wav} bytes, File Size: {file_size_mp3} bytes, "
                     f"RMS Level: {rms_level}, Silence Detected: {'Yes' if silence_detected else 'No'}")
        print('FileInfoCharacteristic Read: {}'.format(file_info))

        return [dbus.Byte(c) for c in file_info.encode()]
    

    def calculate_rms_and_check_silence(self, audio_segment):
        rms_level = audio_segment.rms
        print('RMS Level: {}'.format(rms_level))
        
        # Define a suitable threshold based on your requirements
        silence_threshold = 100
        silence_detected = rms_level < silence_threshold
        print('Silence detected' if silence_detected else 'Sound detected')

        return rms_level, silence_detected

# ---------------- Tab 2: Audio + Video Characteristics ---------------------- #
"""
    Reads the file size of file located at given path.
"""
'''
class FileInfoCharacteristic(Characteristic):
    def __init__(self, service, uuid, file_path, file_type):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.file_path = file_path
        self.file_type = file_type
        

    def ReadValue(self, options):
        temp_file_path = self.file_path
        if self.file_type == 'audio':
            temp_file_path = help.get_most_recent_audio_file(temp_file_path)
        if self.file_type == 'video':
            temp_file_path = help.get_most_recent_video_file(temp_file_path)
            print("FILE PATH: ", temp_file_path)

        file_size = os.path.getsize(temp_file_path)
        file_info = f"{temp_file_path}, File Size: {file_size} bytes"
        print('FileInfoCharacteristic Read: {}'.format(file_info))
        return [dbus.Byte(c) for c in file_info.encode()]
    
    
    def get_most_recent_video_file(self):
        print("Getting most recent file")
        base_path = self.file_path
        # List all directories in the base path
        entries = os.listdir(base_path)
        
        # Filter out possible non directory entries or directories which dont match the data format
        date_dirs = []
        for entry in entries:
            entry_path = os.path.join(base_path, entry)
            if os.path.isdir(entry_path):
                try:
                    # Try to parse the directory name as a date
                    date = datetime.strptime(entry, "%Y-%m-%d")
                    date_dirs.append((entry, date))
                except ValueError:
                    # Skip directories that don't match the date format
                    pass
        if not date_dirs:
            return None

        # Find most recent date
        most_recent_dir = max(date_dirs, key=lambda x: x[1])[0]
        full_path = os.path.join(base_path, most_recent_dir)

        # List files in this directory
        files = []
        most_recent_file = '';
        for file in os.listdir(full_path):
            if file.endswith('.h264'):
                files.append(file)
                if most_recent_file == '':
                    most_recent_file = file
                else:
                    split_file = (file.split('@')[-1].split('.')[0].split('-'))
                    split_mr_file = (most_recent_file.split('@')[-1].split('.')[0].split('-'))
                    
                    if split_file[0] > split_mr_file[0]:
                        most_recent_file = file
                    elif split_file[0] == split_mr_file[0] and split_file[1] > split_mr_file[1]:
                        most_recent_file = file

        if (len(files) < 1):
            raise ValueError(f"No files in the directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return (full_path + '/' + most_recent_file)
    '''


class ResetOffsetCharacteristic(Characteristic):
    def __init__(self, service, uuid, file_transfer_characteristic):
        Characteristic.__init__(
            self, uuid,
            ['write'], service)
        self.file_transfer_characteristic = file_transfer_characteristic
        print(f"ResetOffsetCharacteristic initialized with UUID: {uuid}")


    def WriteValue(self, value, options):
        print("ResetOffsetCharacteristic WriteValue called with value:", value)
        try:
            self.file_transfer_characteristic.reset_offset()
            print("Offset reset")
        except Exception as e:
            print(f"Error resetting offset: {e}")
        return dbus.Array([], signature='y')  # Return an empty byte array with proper D-Bus signature 


class FileTransferCharacteristic(Characteristic):
    def __init__(self, service, uuid, file_path, file_type):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.file_type = file_type
        self.file_path = file_path
        self.offset = 0
        print(f"FileTransferCharacteristic initialized with UUID: {uuid}")
    

    def ReadValue(self, options):
        if self.file_type == 'video':
            return self.ReadVideoFile()
        elif self.file_type == 'audio':
            return self.readWaveformFile()
        elif self.file_type == 'other':
            return self.ReadStaticFile()
        elif self.file_type == 'sensor':
            self.file_path = help.get_most_recent_sensor_file(self.file_path)
            return self.ReadStaticFile()
    

    def capturePicture(self):
        try:
            # Run the command to capture picture using libcamera-still
            command = 'libcamera-still -o /home/bee/GATT_server/picture.jpg'
            subprocess.run(command, shell=True, check=True)
            print('Picture captured successfully.')
        except subprocess.CalledProcessError as e:
            print(f'Error capturing picture: {e}')
        

    def ReadStaticFile(self):
        try:
            mtu = 512
            self.image_path = self.file_path
            
            if self.offset == 0:
                print("IMAGE PATH: ", self.image_path)
                print("IMAGE SIZE: ", os.path.getsize(self.image_path))

            if os.path.exists(self.image_path):
                with open(self.image_path, 'rb') as file:
                    file.seek(self.offset)
                    chunk = file.read(mtu)
                    
                    print(f"Read {len(chunk)} bytes from file starting at offset {self.offset}")
                    if len(chunk) < mtu:
                        self.offset = 0  # Reset for next read if this is the last chunk
                        help.delete_file(self.image_path)
                    else:
                        self.offset += len(chunk)

                    # help.delete_file(image_path)
                    return [dbus.Byte(b) for b in chunk]
            else:
                print("No file exists for picture")
            

        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    

    def ReadVideoFile(self):
        try:
            base_path = help.get_most_recent_video_file(self.file_path)

            mtu = 512

            image_path = help.extract_frame(base_path, 100, '/home/bee/GATT_server/output_frame.jpg')

            with open(image_path, 'rb') as file:
                file.seek(self.offset)
                chunk = file.read(mtu)
                
                print(f"Read {len(chunk)} bytes from file starting at offset {self.offset}")
                if len(chunk) < mtu:
                    self.offset = 0  # Reset for next read if this is the last chunk
                else:
                    self.offset += len(chunk)

                help.delete_file(image_path)
                return [dbus.Byte(b) for b in chunk]
                
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    

    def readWaveformFile(self):
        try:
            mtu = 512
            base_path = help.get_most_recent_audio_file(self.file_path)
            
            if self.offset == 0:
                self.image_path = help.create_waveform_file(base_path)
                print("IMAGE PATH: ", self.image_path)
                print("IMAGE SIZE: ", os.path.getsize(self.image_path))

            
            with open(self.image_path, 'rb') as file:
                file.seek(self.offset)
                chunk = file.read(mtu)
                
                print(f"Read {len(chunk)} bytes from file starting at offset {self.offset}")
                if len(chunk) < mtu:
                    self.offset = 0  # Reset for next read if this is the last chunk
                    help.delete_file(self.image_path)
                else:
                    self.offset += len(chunk)

                # help.delete_file(image_path)
                return [dbus.Byte(b) for b in chunk]
            

        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    

    def send_picture(self):
        result = subprocess.run(['libcamera ,-still, -o /home/bee/GATT_server/test_picture.jpg'])


    def reset_offset(self):
        self.offset = 0
        print("FileTransferCharacteristic offset reset to 0")


'''
This method is being used for testing, this will be used to read one line at a time throughout a file
'''
class VideoReadLineByLineCharacteristic(Characteristic):
    def __init__(self, service, uuid, base_path):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = base_path
        self.line_offset = 0
        print(f"Characteristic initialized with UUID: {uuid}")
    

    def get_most_recent_file(self, base_path):
        # List all directories in the base path
        entries = os.listdir(base_path)
        
        # Filter out possible non directory entries or directories which dont match the data format
        date_dirs = []
        for entry in entries:
            entry_path = os.path.join(base_path, entry)
            if os.path.isdir(entry_path):
                try:
                    # Try to parse the directory name as a date
                    date = datetime.strptime(entry, "%Y-%m-%d")
                    date_dirs.append((entry, date))
                except ValueError:
                    # Skip directories that don't match the date format
                    pass
        if not date_dirs:
            return None

        # Find most recent date
        most_recent_dir = max(date_dirs, key=lambda x: x[1])[0]
        full_path = os.path.join(base_path, most_recent_dir)

        # List files in this directory
        files = []
        most_recent_file = '';
        for file in os.listdir(full_path):
            if file.endswith('.csv'):
                files.append(file)
                most_recent_file = file

        if (len(files) < 1):
            raise ValueError(f"No files in the directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return (full_path + '/' + most_recent_file)


    def ReadValue(self, options):
        print("ReadValue called")
        self.file_path = self.get_most_recent_file(self.folder_path)

        if self.file_path is not None:
            try:
                with open(self.file_path, 'r') as file:
                    lines = file.readlines()
                    all_data = ''.join(lines)
                    # print(f"Returning data: {all_data}")
                    if (self.line_offset >= len(lines)):
                        self.line_offset = 0
                        return [dbus.Byte(b) for b in 'EOF'.encode()]
                    
                    self.line_offset += 1
                    return [dbus.Byte(b) for b in lines[self.line_offset].encode()]
            except Exception as e:
                # print(f"Error occurred while reading the file: {e}")
                return []
        else:
            # print("No file found")
            return []
        

    def reset(self):
        self.line_offset = 0
        self.file_path = None
        self.lines = []
        print("Resetting characteristic state")


class VideoResetLineOffsetCharacteristic(Characteristic):
    def __init__(self, service, uuid, read_line_by_line_characteristic):
        Characteristic.__init__(
            self,
            uuid,
            ['write'],
            service)
        self.read_line_by_line_characteristic = read_line_by_line_characteristic

    def WriteValue(self, value, options):
        print("WriteValue called")
        command = bytes(value).decode('utf-8')
        if command == 'reset':
            self.read_line_by_line_characteristic.reset()
            print("Offset reset command received")
