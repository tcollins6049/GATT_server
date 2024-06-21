#!/usr/bin/python3
import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help

# Characteristic Imports
from characteristics.tab1Variables import FileCharacteristic
from characteristics.tab2 import FileInfoCharacteristic
from characteristics.tab2 import FileTransferCharacteristic
from characteristics.tab2 import ResetOffsetCharacteristic
from characteristics.tab3 import CPUFileReadCharacteristic
from characteristics.tab4 import SensorStateCharacteristic
from characteristics.tab5 import CommandCharacteristic
from characteristics.sensorReadings import TempCharacteristic
from characteristics.sensorReadings import UnitCharacteristic


"""
    Advertisement class for the Thermometer service
"""
class ThermometerAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_service_uuid(ThermometerService.THERMOMETER_SVC_UUID)
        self.include_tx_power = True
        # Uncomment the line below to add a local name to the advertisement
        # self.add_local_name("")
        system_name = socket.gethostname()
        self.add_local_name(system_name)
        print(f"Local name set to: {system_name}")


"""
    Class to establish the provided service, this service is responsible for all characteristics so far
    !! Maybe come back and add a few more services for better characteristic organization !!
"""
class ThermometerService(Service):
    # UUID for the Thermometer service
    THERMOMETER_SVC_UUID = "00000001-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):
        # Initialize the temperature unit to Fahrenheit
        self.farenheit = True

        # Initialize the base Service class with the service UUID
        Service.__init__(self, index, self.THERMOMETER_SVC_UUID, True)

        # -------------- Tab 1: Variables -- Characteristics ------------------- #
        # Adding file-related variable change characteristics
        self.add_characteristic(FileCharacteristic(self, '00000005-710e-4a5b-8d75-3e5b444bc3cf', 'global','capture_window_start_time'))
        self.add_characteristic(FileCharacteristic(self, '00000006-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_window_end_time'))
        self.add_characteristic(FileCharacteristic(self, '00000007-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_duration_seconds'))
        self.add_characteristic(FileCharacteristic(self, '00000008-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_interval_seconds'))
        # Adding file-related variable change characteristics for video
        self.add_characteristic(FileCharacteristic(self, '00000012-710e-4a5b-8d75-3e5b444bc3cf', 'video','capture_window_start_time'))
        self.add_characteristic(FileCharacteristic(self, '00000013-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_window_end_time'))
        self.add_characteristic(FileCharacteristic(self, '00000014-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_duration_seconds'))
        self.add_characteristic(FileCharacteristic(self, '00000015-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_interval_seconds'))

        # ------------- Tab 2: Audio + Video -- Characteristics ------------------ #
        # Adding a characteristic for file information (e.g., file size)
        self.add_characteristic(FileInfoCharacteristic(self, '00000009-710e-4a5b-8d75-3e5b444bc3cf'));
        # Adding a characteristic for pulling a file
        file_transfer_characteristic = (FileTransferCharacteristic(self, '00000011-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/video/'))
        self.add_characteristic(file_transfer_characteristic)
        # Adding characteristic to reset offset when getting file
        self.add_characteristic(ResetOffsetCharacteristic(self, '00000022-710e-4a5b-8d75-3e5b444bc3cf', file_transfer_characteristic))

        # --------------- Tab 3: Sensor data -- Characteristics ----------------- #
        # Adding a characterisitc for cpu file data
        self.add_characteristic(CPUFileReadCharacteristic(self, '00000010-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/cpu/'))
        self.add_characteristic(CPUFileReadCharacteristic(self, '00000024-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/temp/'))

        # --------------- Tab 4: Sensor State Management -- Characteristics ----------------- #
        # Adding characteristics for enabling and disabling sensors
        self.add_characteristic(SensorStateCharacteristic(self, '00000016-710e-4a5b-8d75-3e5b444bc3cf', 'audio'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000017-710e-4a5b-8d75-3e5b444bc3cf', 'video'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000018-710e-4a5b-8d75-3e5b444bc3cf', 'temp'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000019-710e-4a5b-8d75-3e5b444bc3cf', 'airquality'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000020-710e-4a5b-8d75-3e5b444bc3cf', 'scale'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000021-710e-4a5b-8d75-3e5b444bc3cf', 'cpu'))

        # --------------- Tab 5: Commands -- Characteristics ---------------- #
        # Adding the new command characteristic
        self.add_characteristic(CommandCharacteristic(self))

        # -------------- Sensor Readings -- Characteristics ---------------- #
        # Add characteristics to the service
        self.add_characteristic(TempCharacteristic(self))
        self.add_characteristic(UnitCharacteristic(self))


    # Method to check if the temperature unit is Fahrenheit
    def is_farenheit(self):
        return self.farenheit

    # Method to set the temperature unit to Fahrenheit or Celsius
    def set_farenheit(self, farenheit):
        self.farenheit = farenheit


"""
    This is what will run first
"""
def main():
    app = Application()
    app.add_service(ThermometerService(0))
    app.register()

    adv = ThermometerAdvertisement(0)
    adv.register()

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()


if __name__ == "__main__":
    main()
