#!/usr/bin/python3
import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help

# Characteristic Imports
from characteristics import FileInfoCharacteristic
from characteristics import FileCharacteristic
from characteristics import SensorStateCharacteristic
from characteristics import CPUFileReadCharacteristic
from characteristics import FileTransferCharacteristic
from characteristics import ResetOffsetCharacteristic


# Constants for GATT characteristic interface and notification timeout
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

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

        # Add characteristics to the service
        self.add_characteristic(TempCharacteristic(self))
        self.add_characteristic(UnitCharacteristic(self))
        
        # Adding file-related variable change characteristics
        cap_start = FileCharacteristic(self, '00000005-710e-4a5b-8d75-3e5b444bc3cf', 'global','capture_window_start_time')
        self.add_characteristic(cap_start)
        cap_end = FileCharacteristic(self, '00000006-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_window_end_time')
        self.add_characteristic(cap_end)
        cap_duration = FileCharacteristic(self, '00000007-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_duration_seconds')
        self.add_characteristic(cap_duration)
        cap_interval = FileCharacteristic(self, '00000008-710e-4a5b-8d75-3e5b444bc3cf', 'global', 'capture_interval_seconds')
        self.add_characteristic(cap_interval)

        # Adding a characteristic for file information (e.g., file size)
        self.add_characteristic(FileInfoCharacteristic(self, '00000009-710e-4a5b-8d75-3e5b444bc3cf'));
    
        # Adding a characterisitc for cpu file data
        self.add_characteristic(CPUFileReadCharacteristic(self, '00000010-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/cpu/'))
        self.add_characteristic(CPUFileReadCharacteristic(self, '00000024-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/temp/'))

        # Adding a characteristic for pulling a file
        file_transfer_characteristic = (FileTransferCharacteristic(self, '00000011-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/video/'))
        self.add_characteristic(file_transfer_characteristic)

        # Adding file-related variable change characteristics for video
        self.add_characteristic(FileCharacteristic(self, '00000012-710e-4a5b-8d75-3e5b444bc3cf', 'video','capture_window_start_time'))
        self.add_characteristic(FileCharacteristic(self, '00000013-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_window_end_time'))
        self.add_characteristic(FileCharacteristic(self, '00000014-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_duration_seconds'))
        self.add_characteristic(FileCharacteristic(self, '00000015-710e-4a5b-8d75-3e5b444bc3cf', 'video', 'capture_interval_seconds'))

        # Adding characteristics for enabling and disabling sensors
        self.add_characteristic(SensorStateCharacteristic(self, '00000016-710e-4a5b-8d75-3e5b444bc3cf', 'audio'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000017-710e-4a5b-8d75-3e5b444bc3cf', 'video'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000018-710e-4a5b-8d75-3e5b444bc3cf', 'temp'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000019-710e-4a5b-8d75-3e5b444bc3cf', 'airquality'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000020-710e-4a5b-8d75-3e5b444bc3cf', 'scale'))
        self.add_characteristic(SensorStateCharacteristic(self, '00000021-710e-4a5b-8d75-3e5b444bc3cf', 'cpu'))

        # Adding characteristic to reset offset when getting file
        self.add_characteristic(ResetOffsetCharacteristic(self, '00000022-710e-4a5b-8d75-3e5b444bc3cf', file_transfer_characteristic))

        # Adding the new command characteristic
        self.add_characteristic(CommandCharacteristic(self))


    # Method to check if the temperature unit is Fahrenheit
    def is_farenheit(self):
        return self.farenheit

    # Method to set the temperature unit to Fahrenheit or Celsius
    def set_farenheit(self, farenheit):
        self.farenheit = farenheit


"""
This class is responsible for running a command on the pi sent from the app

!! This is just test right now, not currently working !!
"""
class CommandCharacteristic(Characteristic):
    COMMAND_CHARACTERISTIC_UUID = "00000023-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.COMMAND_CHARACTERISTIC_UUID,
            ["write"], service)
    
    def WriteValue(self, value, options):
        command = ''.join([chr(b) for b in value])
        print(f"Received command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Command output:", result.stdout.decode('utf-8'))
            print("Command error:", result.stderr.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print("Command failed:", e)



"""
    This class is responsible for reading the cpu temperature.
"""
class TempCharacteristic(Characteristic):
    TEMP_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
                self, self.TEMP_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(TempDescriptor(self))

    def get_temperature(self):
        value = []
        unit = "C"

        cpu = CPUTemperature()
        temp = cpu.temperature
        if self.service.is_farenheit():
            temp = (temp * 1.8) + 32
            unit = "F"

        strtemp = str(round(temp, 1)) + " " + unit
        for c in strtemp:
            value.append(dbus.Byte(c.encode()))

        return value

    def set_temperature_callback(self):
        if self.notifying:
            value = self.get_temperature()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True

        value = self.get_temperature()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_temperature_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_temperature()

        return value


class TempDescriptor(Descriptor):
    TEMP_DESCRIPTOR_UUID = "2901"
    TEMP_DESCRIPTOR_VALUE = "CPU Temperature"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.TEMP_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.TEMP_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class UnitCharacteristic(Characteristic):
    UNIT_CHARACTERISTIC_UUID = "00000003-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.UNIT_CHARACTERISTIC_UUID,
                ["read", "write"], service)
        self.add_descriptor(UnitDescriptor(self))

    def WriteValue(self, value, options):
        val = str(value[0]).upper()
        if val == "C":
            self.service.set_farenheit(False)
        elif val == "F":
            self.service.set_farenheit(True)

    def ReadValue(self, options):
        value = []

        if self.service.is_farenheit(): val = "F"
        else: val = "C"
        value.append(dbus.Byte(val.encode()))

        return value


class UnitDescriptor(Descriptor):
    UNIT_DESCRIPTOR_UUID = "2901"
    UNIT_DESCRIPTOR_VALUE = "Temperature Units (F or C)"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.UNIT_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.UNIT_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


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
