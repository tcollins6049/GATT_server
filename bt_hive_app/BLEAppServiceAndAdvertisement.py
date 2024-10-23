#!/usr/bin/python3
import socket
from advertisement import Advertisement
from service import Service

# Characteristic Imports
from bt_hive_app.characteristics.Modifications_tab.Config_rw_Char import Config_rw_Characteristic
from bt_hive_app.characteristics.AudVid_tab.FileInfo_Char import FileInfoCharacteristic
from bt_hive_app.characteristics.AudVid_tab.FileTransfer_Char import FileTransferCharacteristic, ResetOffsetCharacteristic

from bt_hive_app.characteristics.audio_video import VideoReadLineByLineCharacteristic
from bt_hive_app.characteristics.file_sensor_data import CPUFileReadCharacteristic, CPUFileReadAllCharacteristic, CPUReadLineByLineCharacteristic, ResetLineOffsetCharacteristic
from bt_hive_app.characteristics.sensor_states import SensorStateCharacteristic
from bt_hive_app.characteristics.commands import CommandCharacteristic, CommandCharacteristicWResponse
from bt_hive_app.characteristics.sensor_readings import TempCharacteristic, UnitCharacteristic, TempHumidityCharacteristic
from bt_hive_app.characteristics.password_char import PasswordVerificationCharacteristic


BLE_SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

class BLEAdvertisement(Advertisement):
    """
    Advertisment class for the project service
    """
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_service_uuid(BLE_SVC_UUID)
        self.include_tx_power = True
        # self.add_local_name("") # Uncomment to add a local name to the advertisment
        system_name = socket.gethostname()
        self.add_local_name(system_name)
        print(f"Local name set to: {system_name}")


class BLEService(Service):
    """
    Class responsible for adding all characteristics for the BLE application to the service.
    """
    def __init__(self, index):
        # Initialize the temperature unit to Fahrenheit
        self.farenheit = True

        # Initialize the base Service class with the service UUID
        Service.__init__(self, index, BLE_SVC_UUID, True)

        self.add_modification_tab_characteristics()
        self.add_audio_video_characteristics()
        self.add_sensor_data_characteristics()
        self.add_sensor_characteristics()
        self.add_command_characteristics()
        self.add_sensor_reading_characteristics()

        # Password Verification
        self.add_characteristic(PasswordVerificationCharacteristic(self, '00000601-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/GATT_server/password.txt'))


    def add_modification_tab_characteristics(self):
        """
        Function adds characteristics used in the modifications tab of the application

        Args:
            self: 
        """
        # Adding file-related variable change characteristics
        self.add_characteristic(Config_rw_Characteristic(self, '00000101-710e-4a5b-8d75-3e5b444bc3cf', 'global','capture_window_start_time'))
        self.add_characteristic(Config_rw_Characteristic(self, '00000102-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_window_end_time'))
        self.add_characteristic(Config_rw_Characteristic(self, '00000103-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_duration_seconds'))
        self.add_characteristic(Config_rw_Characteristic(self, '00000104-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_interval_seconds'))

        # Adding file-related variable change characteristics for video
        self.add_characteristic(Config_rw_Characteristic(self, '00000105-710e-4a5b-8d75-3e5b444bc3cf', 'video','capture_window_start_time'))
        self.add_characteristic(Config_rw_Characteristic(self, '00000106-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_window_end_time'))
        self.add_characteristic(Config_rw_Characteristic(self, '00000107-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_duration_seconds'))
        self.add_characteristic(Config_rw_Characteristic(self, '00000108-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_interval_seconds'))


    def add_audio_video_characteristics(self):
        """
        Function adds characteristics for the audio and video tabs

        """
        # Adding a characteristic for file information (e.g., file size)
        self.add_characteristic(FileInfoCharacteristic(self, '00000201-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/audio/', 'audio'));
        self.add_characteristic(FileInfoCharacteristic(self, '00000202-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/video/', 'video'));

        # Adding a characteristic for pulling a video file. File pulled in chunks.
        video_file_transfer_characteristic = (FileTransferCharacteristic(self, '00000203-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/video/', 'video'))
        self.add_characteristic(video_file_transfer_characteristic)
        self.add_characteristic(ResetOffsetCharacteristic(self, '00000204-710e-4a5b-8d75-3e5b444bc3cf', video_file_transfer_characteristic))

        # Characteristic for pulling 'picture.jpg' file. File pulled in chunks.
        static_file_transfer_characteristic = (FileTransferCharacteristic(self, '00000207-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/GATT_server/picture.jpg', 'other'))
        self.add_characteristic(static_file_transfer_characteristic)
        self.add_characteristic(ResetOffsetCharacteristic(self, '00000208-710e-4a5b-8d75-3e5b444bc3cf', static_file_transfer_characteristic))

        # Needed characteristics for reading the humidity + temp csv file line by line.
        read_line_by_line_characteristic = VideoReadLineByLineCharacteristic(self, '00000209-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/video/')
        self.add_characteristic(read_line_by_line_characteristic)
        self.add_characteristic(ResetOffsetCharacteristic(self, '00000210-710e-4a5b-8d75-3e5b444bc3cf', read_line_by_line_characteristic))

        # audio_file_transfer_characteristic = (FileTransferCharacteristic(self, '00000205-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/audio/', 'audio'))
        # self.add_characteristic(audio_file_transfer_characteristic)
        # self.add_characteristic(ResetOffsetCharacteristic(self, '00000206-710e-4a5b-8d75-3e5b444bc3cf', audio_file_transfer_characteristic))

        # Characteristics for pulling sensor file data. Data files collected in the appmais directory.
        self.add_characteristic(FileTransferCharacteristic(self, '00000211-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/cpu/', 'sensor'))
        self.add_characteristic(FileTransferCharacteristic(self, '00000212-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/temp/', 'sensor'))



    def add_sensor_data_characteristics(self):
        """
        Function for adding characteristics for pulling sensor data

        Args:
            self: 
        """
        # Adding a characterisitc for cpu file data
        self.add_characteristic(CPUFileReadCharacteristic(self, '00000301-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/cpu/'))
        self.add_characteristic(CPUFileReadAllCharacteristic(self, '00000303-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/cpu/'))
        self.add_characteristic(CPUFileReadCharacteristic(self, '00000302-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/temp/'))

        # Needed characteristics for reading the cpu temp csv file line by line.
        read_line_by_line_characteristic = CPUReadLineByLineCharacteristic(self, '00000304-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/cpu/')
        reset_offset_characteristic = ResetLineOffsetCharacteristic(self, '00000305-710e-4a5b-8d75-3e5b444bc3cf', read_line_by_line_characteristic)
        self.add_characteristic(read_line_by_line_characteristic)
        self.add_characteristic(reset_offset_characteristic)

        # Needed characteristics for reading the humidity + temp csv file line by line.
        read_line_by_line_characteristic = CPUReadLineByLineCharacteristic(self, '00000306-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/temp/')
        reset_offset_characteristic = ResetLineOffsetCharacteristic(self, '00000307-710e-4a5b-8d75-3e5b444bc3cf', read_line_by_line_characteristic)
        self.add_characteristic(read_line_by_line_characteristic)
        self.add_characteristic(reset_offset_characteristic)

    
    def add_sensor_characteristics(self):
        # Adding characteristics for enabling and disabling sensors
        self.add_characteristic(SensorStateCharacteristic(self, '00000401-710e-4a5b-8d75-3e5b444bc3cf', 'audio'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000402-710e-4a5b-8d75-3e5b444bc3cf', 'video'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000403-710e-4a5b-8d75-3e5b444bc3cf', 'temp'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000404-710e-4a5b-8d75-3e5b444bc3cf', 'airquality'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000405-710e-4a5b-8d75-3e5b444bc3cf', 'scale'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000406-710e-4a5b-8d75-3e5b444bc3cf', 'cpu'))

    def add_command_characteristics(self):
        # Adding the new command characteristic
        self.add_characteristic(CommandCharacteristic(self, '00000023-710e-4a5b-8d75-3e5b444bc3cf'))
        self.add_characteristic(CommandCharacteristicWResponse(self, '00000502-710e-4a5b-8d75-3e5b444bc3cf'))

    def add_sensor_reading_characteristics(self):
        # Add characteristics to the service
        self.add_characteristic(TempCharacteristic(self))
        self.add_characteristic(UnitCharacteristic(self))
        self.add_characteristic(TempHumidityCharacteristic(self))

    # Method to check if the temperature unit is Fahrenheit
    def is_farenheit(self):
        return self.farenheit

    # Method to set the temperature unit to Fahrenheit or Celsius
    def set_farenheit(self, farenheit):
        self.farenheit = farenheit
