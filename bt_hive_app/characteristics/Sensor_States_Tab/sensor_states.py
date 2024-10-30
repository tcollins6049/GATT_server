import dbus, configparser
from service import Characteristic


class SensorStateCharacteristic(Characteristic):
    """
    Characteristic for enabling and disabling sensors in the config file

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
        section_name (str): Sensor we are turning on or off

    Methods:
        ReadValue(options): Read current state of sensor
        WriteValue(value, options): Set sensor state to 'value'
    """
    def __init__(self, service, uuid, section_name):
        """
        Initialize the class

        Args:
            service (): Service containing this characteristic
            uuid (str): uuid of the characteristic
            section_name (str): Sensor we are changing state of
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
        self.variable_name = 'auto_start'
    

    def ReadValue(self, options):
        """
        Read and return current state of the sensor

        Args:
            options (): Additional options for reading value

        Returns:

        """
        try:
            # Create a config parser and read the file
            config = configparser.ConfigParser()
            config.read(self.file_path)

            if self.section_name in config and self.variable_name in config[self.section_name]:
                value = config[self.section_name][self.variable_name].lower()
                if value == 'true':
                    captured_data = f"{self.section_name}: True"
                elif value == 'false':
                    captured_data = f"{self.section_name}: False"
                else:
                    captured_data = f"{self.section_name}: True"  # Default to True if value is not recognized
            else:
                captured_data = f"{self.section_name}: True"  # Default to True if section or variable is not found

            # print(f"FileCharacteristic Read: {captured_data}")
            return [dbus.Byte(c) for c in captured_data.encode()]

        except Exception as e:
            print(f"Error Reading File: {e}")
            return []


    def WriteValue(self, value, options):
        """
        Change selected sensor state to value

        Args:
            value (): State to change selected sensor to
            options (): Additional options when writing value
        """
        try:
            # Convert the byte values to a string
            data = ''.join(chr(v) for v in value)

            # Ensure the string is 'True' if it's 'true'
            if data.lower() == 'true':
                data = 'True'
            elif data.lower() == 'false':
                data = 'False'

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
