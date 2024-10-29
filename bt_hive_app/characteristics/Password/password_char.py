import dbus
from service import Characteristic


class PasswordVerificationCharacteristic(Characteristic):
    """
    Characteristic for password verification
    """
    def __init__(self, service, uuid, password_file):
        Characteristic.__init__(
            self, uuid,
            ['write', 'read'], service)
        self.password_file = password_file
        self.is_correct_password = False
        print(f"PasswordVerificationCharacteristic initialized with UUID: {uuid}")


    def ReadValue(self, options):
        return [dbus.Byte(1) if self.is_correct_password else dbus.Byte(0)]
    

    def WriteValue(self, value, options):
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
        