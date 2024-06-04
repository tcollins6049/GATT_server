#!/usr/bin/python3
import dbus, os, socket, glob, configparser
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime


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
        self.add_characteristic(CPUFileReadCharacteristic(self, '00000010-710e-4a5b-8d75-3e5b444bc3cf'))

        # Adding a characteristic for pulling a file
        self.add_characteristic(FileTransferCharacteristic(self, '00000011-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/appmais/bee_tmp/audio/2024-05-29/rpi4-60@2024-05-29@14-20-00.wav'))


    # Method to check if the temperature unit is Fahrenheit
    def is_farenheit(self):
        return self.farenheit

    # Method to set the temperature unit to Fahrenheit or Celsius
    def set_farenheit(self, farenheit):
        self.farenheit = farenheit


"""
    This is a generic class responsible for reading and writing to variables from the beemon-config file
"""
class FileCharacteristic(Characteristic):
    def __init__(self, service, uuid, section_name, variable_name):
        # Initialize the base Characteristic class with read and write properties
        Characteristic.__init__(
            self,
            uuid, 
            ['read', 'write'],  
            service)
        
        # Path to the configuration file.
        self.file_path = '/home/bee/AppMAIS/beemon-config.ini'
        # Section name to look for in config file
        self.section_name = section_name
        # Variable name to look for in the configuration file
        self.variable_name = variable_name


    """
        Reads the value of the variable from the configuration file.

        :param options: Additional options for reading the value.
        :return: The value of the variable encoded in bytes.
    """
    def ReadValue(self, options):
        '''try:
            capture_lines = []

            # Open the configuration file and find the line starting with the variable name
            with open(self.file_path, 'r') as file:
                for line in file:
                    if line.startswith(self.variable_name):
                        capture_lines.append(line.strip())
                        break
            
            # Join the captured lines and print the read value
            captured_data = '\n'.join(capture_lines)
            print('FileCharacteristic Read: {}'.format(captured_data))

            # Return the read value as a list of dbus.Byte
            return [dbus.Byte(c) for c in captured_data.encode()]
        except Exception as e:
            print(f"Error Reading File: {e}")
            return []
        '''
        try:
            # Cretae a config parser and read the file
            config = configparser.ConfigParser()
            config.read(self.file_path)

            values = []

            # Handles reading variable in video section
            if self.section_name == 'video':
                # Get the value from only the video section
                if self.section_name in config and self.variable_name in config[self.section_name]:
                    value = config[self.section_name][self.variable_name]
                    values.append(f"{self.section_name}: {value}")
                else:
                    print(f"Variable {self.variable_name} not found in section {self.section_name}")
            # Handles reading that variable in all other sections
            else:
                # Get the value from all sections except 'video'
                for section in config.sections():
                    if section != 'video' and self.variable_name in config[section]:
                        value = config[section][self.variable_name]
                        values.append(f"{section}: {value}")
            
            if values:
                captured_data = '\n'.join(values)
                print(f"FileCharacteristic Read: {captured_data}")
                return [dbus.Byte(c) for c in captured_data.encode()]
            else:
                print(f"Variable {self.variable_name} not found in any applicable section")
                return []
            

        except Exception as e:
            print(f"Error Reading File: {e}")
            return []


    """
        Writes the provided value to the configuration file, updating the variable.

        :param value: The value to write, provided as a list of bytes.
        :param options: Additional options for writing the value.
    """
    def WriteValue(self, value, options):
        try:
            # Convert the byte values to a string
            data = ''.join(chr(v) for v in value)
            print('FileCharacteristic Write: {}'.format(data))

            modified_lines = []

            # Open the configuration file and update the line starting with the variable name
            with open(self.file_path, 'r') as file:
                for line in file:
                    if line.startswith(self.variable_name):
                        modified_line = self.variable_name + ' = ' + data + '\n'
                        modified_lines.append(modified_line)
                    else:
                        modified_lines.append(line)

            # Write the modified lines back to the file
            with open(self.file_path, 'w') as file:
                file.writelines(modified_lines)
        except Exception as e:
            print(f"Error Writing File: {e}")


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
        self.file_path = '/home/bee/AppMAIS/beemon-config.ini'

    def ReadValue(self, options):
        file_size = os.path.getsize(self.file_path)
        file_info = f"File Size: {file_size} bytes"
        print('FileInfoCharacteristic Read: {}'.format(file_info))
        return [dbus.Byte(c) for c in file_info.encode()]
    

"""
    This class is responsible for reading the cpu temperature from the file

    !! Need to add update functionality !!
"""
class CPUFileReadCharacteristic(Characteristic):
    def __init__(self, service, uuid):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = '/home/bee/appmais/bee_tmp/cpu/'
        print(f"Characteristic initialized with UUID: {uuid}")

    def get_most_recent_file(self):
        print("Getting most recent file")
        try:
            dirs = [d for d in os.listdir(self.folder_path) if os.path.isdir(os.path.join(self.folder_path, d))]
            print(f"Directories found: {dirs}")
            dirs.sort(key=lambda x: datetime.strptime(x, '%Y-%m-%d'), reverse=True)
            print(f"Sorted directories: {dirs}")
            for d in dirs:
                files = glob.glob(os.path.join(self.folder_path, d, '*.csv'))
                print(f"Files in {d}: {files}")
                files.sort(key=os.path.getmtime, reverse=True)
                print(f"Sorted files in {d}: {files}")
                if files:
                    print("FILES[0]", files[0])
                    return files[0]
        except Exception as e:
            print(f"Error occurred while getting most recent file: {e}")
        print("GONNA RETURN NONE")
        return None


    def ReadValue(self, options):
        print("ReadValue called")
        self.file_path = self.get_most_recent_file()
        if self.file_path is not None:
            try:
                with open(self.file_path, 'r') as file:
                    last_line = file.readlines()[-1]
                print(f"Returning data: {last_line}")
                return [dbus.Byte(b) for b in last_line.encode()]
            except Exception as e:
                print(f"Error occurred while reading the file: {e}")
                return []
        else:
            print("No file found")
            return []


"""
    This class is responsible for pulling a file from the passed in file path

    !! This is just test right now, not currently working !!
"""  
class FileTransferCharacteristic(Characteristic):
    def __init__(self, service, uuid, file_path):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.file_path = file_path
        print(f"FileTransferCharacteristic initialized with UUID: {uuid}")

    def ReadValue(self, options):
        print("FileTransferCharacteristic ReadValue called")
        try:
            with open(self.file_path, 'rb') as file:
                file_data = file.read()
            print(f"Read {len(file_data)} bytes from file")
            return [dbus.Byte(b) for b in file_data]
        except Exception as e:
            print(f"Error reading file: {e}")
            return []


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
