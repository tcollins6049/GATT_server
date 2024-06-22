import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help


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
        
    """
        Writes the provided value to the configuration file, updating the variable.

        :param value: The value to write, provided as a list of bytes.
        :param options: Additional options for writing the value.
    
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
    """
    def ReadValue(self, options):
        try:
            # Create a config parser and read the file
            config = configparser.ConfigParser()
            config.read(self.file_path)

            values = []

            # Iterate through all sections in the configuration
            for section in config.sections():
                # Check if the auto_start variable exists in the section
                if self.variable_name in config[section]:
                    value = config[section][self.variable_name]
                    if value.lower() == 'true':
                        values.append(f"{section}: True")
                    elif value.lower() == 'false':
                        values.append(f"{section}: False")
                else:
                    # If auto_start variable is not found in the section, consider it True
                    values.append(f"{section}: True")

            if values:
                captured_data = '\n'.join(values)
                print(f"FileCharacteristic Read:\n{captured_data}")
                return [dbus.Byte(c) for c in captured_data.encode()]
            else:
                print(f"Variable {self.variable_name} not found in any applicable section")
                return []

        except Exception as e:
            print(f"Error Reading File: {e}")
            return []


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
                if data == 'True':
                    # Remove the auto_start=True line if it exists
                    if self.variable_name in config[self.section_name]:
                        del config[self.section_name][self.variable_name]
                else:
                    # Set auto_start=False
                    config[self.section_name][self.variable_name] = 'False'

                # Write the updated config back to the file
                with open(self.file_path, 'w') as file:
                    config.write(file)
            else:
                print(f"Section {self.section_name} not found")

        except Exception as e:
            print(f"Error Writing File: {e}")
