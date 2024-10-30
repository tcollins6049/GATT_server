import dbus
from service import Characteristic


class PasswordVerificationCharacteristic(Characteristic):
    """
    Characteristic for password verification

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
        password_file (str): File containing the correct password
    
    Methods:
        ReadValue(options): Returns if password was correct or incorrect
        WriteValue(value, options): Compares password entered from user with correct password.
    """
    def __init__(self, service, uuid, password_file):
        """
        Initialize the class

        Args:
            service (): Service containing this characteristic
            uuid (str): uuid of the characteristic
            password_file (str): Path to file containing the correct password
        """
        Characteristic.__init__(
            self, uuid,
            ['write', 'read'], service)
        self.password_file = password_file
        self.is_correct_password = False
        # print(f"PasswordVerificationCharacteristic initialized with UUID: {uuid}")


    def ReadValue(self, options):
        """
        Returns if teh password was correct or incorrect

        Args:
            options (): Additional options for writing value
        
        Returns:

        """
        return [dbus.Byte(1) if self.is_correct_password else dbus.Byte(0)]
    

    def WriteValue(self, value, options):
        """
        Recives password attempt from user, compares that with correct password, and returns if it is correct or not

        Args:
            value (): User password attempt
            options (): Additional options for writing value
        
        Returns:
        
        """
        input_password = bytes(value).decode()
        with open(self.password_file, 'r') as file:
            stored_password = file.read().strip()
        
        if input_password == stored_password:
            print("Password is correct")
            self.is_correct_password = True
            return [dbus.Byte(1)]
        else:
            print("Password is incorrect")
            self.is_correct_password = False
            return [dbus.Byte(0)]
        