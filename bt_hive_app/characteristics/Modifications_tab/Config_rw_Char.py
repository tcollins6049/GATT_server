import dbus, configparser
from service import Characteristic


class Config_rw_Characteristic(Characteristic):
    """
    Characteristic responsible for reading from and writing to beemon-config file

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
        section_name (str): Either 'global' or 'video' since we want these modified seperately.
        variable_name (str): Variable we want to modify
    
    Methods:
        ReadValue(options): Reads value from config file
        WriteValue(value, options): Writes to value from config file
    """
    def __init__(self, service, uuid, section_name, variable_name):
        """
        Initialize the class

        Args:
            service (): Service containing this characteristic
            uuid (str): uuid of the characteristic
            section_name (str): Either 'global' or 'video' since we want these modified seperately
            variable_name (str): Variable we want to modify
        """
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


    def ReadValue(self, options):
        """
        Reads the value of variable_name from the config file

        Args:
            options (): Additional options for reading the value
        
        Returns:

        """
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


    def WriteValue(self, value, options):
        """
        Writes 'value' to 'variable_name' in the config file

        Args:
            value (): Value to write to variable_name
            options (): Additional options for writing the value
        """
        try:
            # Convert the byte values to a string
            data = ''.join(chr(v) for v in value)

            # Create a config parser and read the file
            config = configparser.ConfigParser()
            config.read(self.file_path)

            if self.section_name == 'video':
                # Update the specific section and variable name if section is 'video'
                if self.section_name in config:
                    config[self.section_name][self.variable_name] = data
                else:
                    print(f"Section {self.section_name} not found")
            else:
                # Update all sections except 'video'
                for section in config.sections():
                    if section != 'video' and self.variable_name in config[section]:
                        config[section][self.variable_name] = data
            # Write the updated config back to the file
            with open(self.file_path, 'w') as file:
                config.write(file)
        except Exception as e:
            print(f"Error Writing File: {e}")
