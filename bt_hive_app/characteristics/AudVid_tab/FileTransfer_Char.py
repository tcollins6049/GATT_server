import dbus, os, subprocess
from service import Characteristic
import bt_hive_app.helper_methods as help


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
            # self.capturePicture()
            print("FILE_PATH: ", self.file_path)
            result = self.ReadStaticFile(self.file_path)
            # help.delete_file(self.file_path)
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
                        if (self.file_type == 'other'):
                            help.delete_file(base_path)
                    else:
                        self.offset += len(chunk)

                    # print(f"Chunk: {chunk}")
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
