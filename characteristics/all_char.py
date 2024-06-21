import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help


# Constants for GATT characteristic interface and notification timeout
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000

# ---------------- Tab 3: Sensor Data Characteristics ---------------------- #
"""
    This class is responsible for reading the cpu temperature from the file

    !! Need to add update functionality !!
"""
class CPUFileReadCharacteristic(Characteristic):
    def __init__(self, service, uuid, base_path):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = base_path
        print(f"Characteristic initialized with UUID: {uuid}")

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
        files = os.listdir(full_path)
        if (len(files) != 1):
            raise ValueError(f"Expected exactly one file in directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return full_path + '/' + files[0]


    def get_relevant_line(self):
        with open(self.file_path, 'r') as file:
            # last_line = file.readlines()[-1]
            lines = file.readlines()

            if ('nan' in lines[-1]):
                last_valid_line = None
                for line in reversed(lines):
                    if 'nan' not in line:
                        last_valid_line = line
                        break
                if last_valid_line is None:
                    print('No valid readings found in the file')
                    last_line = lines[0]
                else:
                    print("last valid before nan: ", last_valid_line)
                    last_line = last_valid_line
            else:
                last_line = lines[-1]
        
        return last_line
    

    def get_update_text(self, last_line):
        if 'nan' not in last_line:
            # Text returned will just contain the update date and time
            unformatted_time = (last_line.split(',')[0]).replace('"','')
            time_obj = datetime.strptime(unformatted_time, '%H-%M-%S')
            formatted_time = time_obj.strftime('%I-%M-%S %p')
            date = (self.file_path.split('/')[6])
            
            update_text = (f"Updated on {date} at {formatted_time}")
            return update_text
            
        else:
            # Text will contain when nan values started being recorded
            unformatted_time = (last_line.split(',')[0]).replace('"','')
            time_obj = datetime.strptime(unformatted_time, '%H-%M-%S')
            formatted_time = time_obj.strftime('%I-%M-%S %p')
            date = (self.file_path.split('/')[6])
            
            update_text = (f"Returning nan values since {formatted_time} on {date}")
            return update_text
           


    def ReadValue(self, options):
        print("ReadValue called")
        # self.file_path = self.get_most_recent_file(self.folder_path)
        self.file_path = help.get_most_recent_sensor_file(self.folder_path)

        if self.file_path is not None:
            try:
                last_line = self.get_relevant_line()
                update_text = self.get_update_text(last_line)
                
                returned_data = f"{last_line.strip()}|{update_text}"
                print(f"Returning data: {returned_data}")
                return [dbus.Byte(b) for b in returned_data.encode()]
            except Exception as e:
                print(f"Error occurred while reading the file: {e}")
                return []
        else:
            print("No file found")
            return []
        


# ---------------- Tab 4: Sensor State Characteristics ---------------------- #
"""
    This class is responsible for enabling and disabling sensors in the config file
"""
class SensorStateCharacteristic(Characteristic):
    def __init__(self, service, uuid, section_name):
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
        self.variable_name = 'auto_start'
    

    """
        Reads the value of the variable from the configuration file.

        :param options: Additional options for reading the value.
        :return: The value of the variable encoded in bytes.
    """
    def ReadValue(self, options):
        try:
            # Cretae a config parser and read the file
            config = configparser.ConfigParser()
            config.read(self.file_path)

            values = []

            # Get the value from only the video section
            if self.section_name in config and self.variable_name in config[self.section_name]:
                value = config[self.section_name][self.variable_name]
                values.append(f"{self.section_name}: {value}")
            else:
                print(f"Variable {self.variable_name} not found in section {self.section_name}")
            
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

            # Ensure the string is 'True' if it's 'true'
            if data.lower() == 'true':
                data = 'True'
            elif data.lower() == 'false':
                data = 'False'

            print('FileCharacteristic Write: {}'.format(data))

            # Create a config parser and read the file
            config = configparser.ConfigParser()
            config.read(self.file_path)

            # Update the specific section and variable name if section is 'video'
            if self.section_name in config:
                config[self.section_name][self.variable_name] = data
                # print("HHHHHHHHHH", data)
            else:
                print(f"Section {self.section_name} not found")
            # Write the updated config back to the file
            with open(self.file_path, 'w') as file:
                config.write(file)
        except Exception as e:
            print(f"Error Writing File: {e}")
    

# ---------------- Tab 5: Command Characteristics ---------------------- #
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
    

# ---------------- Sensor Reading Characteristics ---------------------- #
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

