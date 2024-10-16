import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import bt_hive_app.helper_methods as help
from pydub import AudioSegment
import time


class FileInfoCharacteristic(Characteristic):
    """
    This class holds the charactersitics code for pulling info from audio and video files.
    Pulls data such as file size and RMS level.

    """
    def __init__(self, service, uuid, file_path, file_type):
        """
        init function

        Args:
            service: Service this characteristic is under
            uuid (str): uuid for this characteristic
            file_path (str): Path of the file we are reading info from
            file_type (str): Either 'audio' or 'video'.
        
        """
        super().__init__(
            uuid,
            ['read'],
            service)
        self.file_path = file_path
        self.file_type = file_type


    def ReadValue(self, options):
        """
        Function responsible for reading information from file at file_path

        Args:
            options: 

        """
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
        """
        Function used to calculate the rms level of the audio recording and determine if it is silent

        Args:
            audio_segment: audio segment taken from the read .wav file
        
        """
        rms_level = audio_segment.rms
        print('RMS Level: {}'.format(rms_level))
        
        # Define a suitable threshold based on your requirements
        silence_threshold = 100
        silence_detected = rms_level < silence_threshold
        print('Silence detected' if silence_detected else 'Sound detected')

        return rms_level, silence_detected


class ResetOffsetCharacteristic(Characteristic):
    """
    Used to reset the byte offset for the file transfer process.


    """
    def __init__(self, service, uuid, file_transfer_characteristic):
        """
        init function

        Args:
            service: Service this characteristic is under
            uuid (str): uuid of the characteristic
            file_transfer_characteristic (characteristic): Characteristic we are accessing the offset in

        """
        Characteristic.__init__(
            self, uuid,
            ['write'], service)
        self.file_transfer_characteristic = file_transfer_characteristic
        print(f"ResetOffsetCharacteristic initialized with UUID: {uuid}")


    def WriteValue(self, value, options):
        """
        Function used to recieve call from the application which then proceeds to reset the offset

        Args:
            value (str): Value recieved from the application.
            options:

        """
        print("ResetOffsetCharacteristic WriteValue called with value:", value)
        try:
            self.file_transfer_characteristic.reset_offset()
            print("Offset reset")
        except Exception as e:
            print(f"Error resetting offset: {e}")
        return dbus.Array([], signature='y')  # Return an empty byte array with proper D-Bus signature 


class FileTransferCharacteristic(Characteristic):
    """
    Class containing the characteristic responsible for transferring a file from the pi to the application

    """
    def __init__(self, service, uuid, file_path, file_type):
        """
        init function

        Args:
            service: Service the characteristic will be located under
            uuid (str): This characteristic's UUID
            file_path (str): Path of the file which needs to be transferred
            file_type (str): Either 'video', 'audio', 'sensor', or 'other'.

        """
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
        """
        Function called by the application. Calls read based off of file_type.

        Args:
            options:

        """
        if self.file_type == 'video':
            return self.ReadVideoFile()
        elif self.file_type == 'audio':
            return self.readWaveformFile()
        elif self.file_type == 'other':
            print("WITHIN OTHER SECTION")
            # self.capturePicture()
            result = self.ReadStaticFile()
            # help.delete_file(self.image_path)
            return result
        elif self.file_type == 'sensor':
            print("---------------------------------------------------------------------------------------------")
            print(f"Original Base Path: {self.file_path}")
            base_path = help.get_most_recent_sensor_file(self.file_path)
            return self.ReadStaticFile(base_path)
    

    def capturePicture(self):
        """
        Function responsible for taking a picture using camera connected to the Pi

        """
        try:
            # Run the command to capture picture using libcamera-still
            command = 'libcamera-still -q 10 -o picture.jpg'
            subprocess.run(command, shell=True, check=True)
            print('Picture captured successfully.')
        except subprocess.CalledProcessError as e:
            print(f'Error capturing picture: {e}')
        

    def ReadStaticFile(self, base_path):
        """
        Function responsible for reading a file straight from the file_path

        Returns:
            list: Contains chunk of data read from file if successful, empty otherwise.

        """
        try:
            mtu = 512
            # self.image_path = self.file_path
            
            if self.offset == 0:
                print("IMAGE PATH: ", base_path)
                print("IMAGE SIZE: ", os.path.getsize(base_path))
            
            print(f"OFFSET: {self.offset}")

            if os.path.exists(base_path):
                with open(base_path, 'rb') as file:
                    file.seek(self.offset)
                    chunk = file.read(mtu)
                    
                    print(f"Read {len(chunk)} bytes from file starting at offset {self.offset}")
                    if len(chunk) < mtu:
                        self.offset = 0  # Reset for next read if this is the last chunk
                        # help.delete_file(self.image_path)
                    else:
                        self.offset += len(chunk)

                    print(f"Chunk: {chunk}")
                    # help.delete_file(image_path)
                    return [dbus.Byte(b) for b in chunk]
            else:
                print("No file exists for picture")
            

        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    

    def ReadVideoFile(self):
        """
        Function responisble for retrieving and reading data from a frame from the most recent video recording

        Returns:
            list: Contains chunk of data if read was successful, empty otherwise.

        """
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
        """
        Function responsible for retrieving and reading a waveform image file.

        Returns:
            list: Contains chunk of bytes from file if successful, empty otherwise.

        """
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
    

    #def send_picture(self):
        """
        Function responsible for running command to take picture using the Pi camera.

        """
    #    result = subprocess.run(['libcamera ,-still, -o /home/bee/GATT_server/test_picture.jpg'])


    def reset_offset(self):
        """
        Function used to reset the offset, ensures the file transfer starts at the beginning of the file.

        """
        self.offset = 0
        print("FileTransferCharacteristic offset reset to 0")



class VideoReadLineByLineCharacteristic(Characteristic):
    """
    Characteristic responsible for reading a video file line by line

    """
    def __init__(self, service, uuid, base_path):
        """
        init function

        Args:
            service: Service the characteristic is located under
            uuid (str): Characteristic's UUID
            base_path (str): Full path up to where get_most_recent_file() needs to be called.

        """
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = base_path
        self.line_offset = 0
        print(f"Characteristic initialized with UUID: {uuid}")
    

    def get_most_recent_file(self, base_path):
        """
        Function used to get most recent file from the base_path. Ensures were pulling the most up to date info from the Pi.

        Args:
            base_path (str): Path of directory we are pulling most recent file from.

        Returns:
            Full path of the most recent file in the base_path directory if successful, None otherwise.

        Raises:
            ValueError: If no files are found in the directory.

        """
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
        """
        Function responsible for reading line from specified file.

        Args:
            options:

        Returns:
            list: Contains line of data if successful, empty otherwise.

        """
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
        """
        Function responsible for resetting the offset, ensures we start reading from the beginning of the file.

        """
        self.line_offset = 0
        self.file_path = None
        self.lines = []
        print("Resetting characteristic state")


class VideoResetLineOffsetCharacteristic(Characteristic):
    """
    Characteristic used to reset the line offset of the VideoLineByLineCharacteristic.

    """
    def __init__(self, service, uuid, read_line_by_line_characteristic):
        """
        init function

        Args:
            service: Service the characteristic is located under
            uuid (str): Characteristic's UUID
            read_line_by_line_characteristic (characteristic): Characteristic who's offset is being reset.

        """
        Characteristic.__init__(
            self,
            uuid,
            ['write'],
            service)
        self.read_line_by_line_characteristic = read_line_by_line_characteristic


    def WriteValue(self, value, options):
        """
        Function responsible for recieving call from the application which then proceeds to reset the offset.

        Args:
            value (str): Value recieved from the application
            options:
            
        """
        print("WriteValue called")
        command = bytes(value).decode('utf-8')
        if command == 'reset':
            self.read_line_by_line_characteristic.reset()
            print("Offset reset command received")
