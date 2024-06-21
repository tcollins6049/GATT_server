import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help

# ---------------- Tab 2: Audio + Video Characteristics ---------------------- #
"""
    Reads the file size of file located at given path.
    !! Need to change file path to be a parameter !!
"""
class FileInfoCharacteristic(Characteristic):
    def __init__(self, service, uuid):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.file_path = '/home/bee/appmais/bee_tmp/audio/2024-05-29/rpi4-60@2024-05-29@14-20-00.wav'

    def ReadValue(self, options):
        file_size = os.path.getsize(self.file_path)
        file_info = f"File Size: {file_size} bytes"
        print('FileInfoCharacteristic Read: {}'.format(file_info))
        return [dbus.Byte(c) for c in file_info.encode()]


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


"""
    This class is responsible for pulling a file from the passed in file path

    !! This is just test right now, not currently working !!
    /home/bee/appmais/bee_tmp/audio/2024-05-29/rpi4-60@2024-05-29@14-20-00.wav
    /home/bee/appmais/bee_tmp/video/2024-06-13/rpi4-60@2024-06-13@14-40-00.h264
"""
class FileTransferCharacteristic(Characteristic):
    def __init__(self, service, uuid, file_path):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.file_path = file_path
        self.offset = 0
        print(f"FileTransferCharacteristic initialized with UUID: {uuid}")
    

    def get_most_recent_file(self, base_path):
        print("Getting most recent file")
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
        
    
    def extract_frame(self, video_file, frame_number, output_file):
        # Open the video file
        cap = cv2.VideoCapture(video_file)

        # Check if the video file was opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open video file '{video_file}'")
            return

        # Get total number of frames in the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # print(f"Total frames in the video: {total_frames}")

        # Set the desired frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame
        ret, frame = cap.read()

        if ret:
            # Save the frame as an image file
            cv2.imwrite(output_file, frame)
            print(f"Frame {frame_number} saved as {output_file}")

            # Get size of the saved image file
            file_size = os.path.getsize(output_file)
            # print(f"Size of {output_file}: {file_size} bytes")

            cap.release()
            return output_file
        else:
            print(f"Error: Could not read frame {frame_number} from video")
            cap.release()
            return None


    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            # print(f"Deleted file: {file_path}")
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
        except PermissionError:
            print(f"Error: Permission denied to delete file '{file_path}'")
        except Exception as e:
            print(f"Error: {e}")
        
    
    def ReadValue(self, options):
        try:
            base_path = self.get_most_recent_file(self.file_path)

            mtu = 512

            image_path = self.extract_frame(base_path, 100, '/home/tcollins6049/GATT_server/output_frame.jpg')

            with open(image_path, 'rb') as file:
                file.seek(self.offset)
                chunk = file.read(mtu)
                
                print(f"Read {len(chunk)} bytes from file starting at offset {self.offset}")
                if len(chunk) < mtu:
                    self.offset = 0  # Reset for next read if this is the last chunk
                else:
                    self.offset += len(chunk)

                self.delete_file(image_path)
                return [dbus.Byte(b) for b in chunk]
                
        except Exception as e:
            print(f"Error reading file: {e}")
            return []


    def reset_offset(self):
        self.offset = 0
        print("FileTransferCharacteristic offset reset to 0")
     