import dbus, os, subprocess
from service import Characteristic
import bt_hive_app.helper_methods as help


class FileTransferCharacteristic(Characteristic):
    """
    The following characteristic transfers a file from the pi to the application.

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
        file_path (str): Path of the file being transferred
        file_type (str): Either 'video', audio', 'sensor', or 'other'
    
    Methods:
        ReadValue(): Passes file to other read method based on file_type.
        ReadStaticFile(): Reads file directly from file path.
        ReadVideoFile(): Reads frame from most recent video file.
        ReadWaveformFile(): Reads waveform image from
        reset_offset(): Resets offset to 0
    """
    def __init__(self, service, uuid, file_path, file_type):
        """
        Initialize the class

        Args:
            service (): Service the characteristic will be located under
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
        # print(f"FileTransferCharacteristic initialized with UUID: {uuid}")
    

    def ReadValue(self, options):
        """
        Function called by the application. Calls read method based off of file_type.

        Returns:

        """
        if self.file_type == 'video':
            return self.ReadVideoFile()
        elif self.file_type == 'audio':
            return self.readWaveformFile()
        elif self.file_type == 'other':
            result = self.ReadStaticFile(self.file_path)
            return result
        elif self.file_type == 'sensor':
            base_path = help.get_most_recent_sensor_file(self.file_path)
            return self.ReadStaticFile(base_path)


    def ReadStaticFile(self, base_path):
        """
        Function responsible for reading a file straight from the file_path

        Args:
            base_path (str): Path of file being transferred

        Returns:
            list: Contains chunk of data read from file if successful, empty otherwise.
        """
        try:
            mtu = 512
            
            # If at beginning of file
            if self.offset == 0:
                print("IMAGE PATH: ", base_path)
                print("IMAGE SIZE: ", os.path.getsize(base_path))

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


    def reset_offset(self):
        """
        Function used to reset the offset, ensures the file transfer starts at the beginning of the file.
        """
        self.offset = 0


class ResetOffsetCharacteristic(Characteristic):
    """
    The following characteristic is used to reset the file transfer offset

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
        file_transfer_characteristic (Characteristic): Characteristic where reset_offset is being called

    Methods:
        WriteValue(value, options): Resets offset to 0
    """
    def __init__(self, service, uuid, file_transfer_characteristic):
        """
        Initialize the class

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
            options ():
        """
        # print("ResetOffsetCharacteristic WriteValue called with value:", value)
        try:
            self.file_transfer_characteristic.reset_offset()
            print("Offset reset")
        except Exception as e:
            print(f"Error resetting offset: {e}")
        return dbus.Array([], signature='y')  # Return an empty byte array with proper D-Bus signature 
