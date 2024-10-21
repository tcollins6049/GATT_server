import dbus, configparser
from service import Characteristic

# ---------------- Tab 1: Variables Characteristics ---------------------- #
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

            # Create a config parser and read the file
            config = configparser.ConfigParser()
            config.read(self.file_path)

            if self.section_name == 'video':
                # Update the specific section and variable name if section is 'video'
                if self.section_name in config:
                    config[self.section_name][self.variable_name] = data
                    print("HHHHHHHHHH", data)
                else:
                    print(f"Section {self.section_name} not found")
            else:
                # Update all sections except 'video'
                for section in config.sections():
                    if section != 'video' and self.variable_name in config[section]:
                        config[section][self.variable_name] = data
                        print("IIIIIIII", data)
            # Write the updated config back to the file
            with open(self.file_path, 'w') as file:
                config.write(file)
        except Exception as e:
            print(f"Error Writing File: {e}")
