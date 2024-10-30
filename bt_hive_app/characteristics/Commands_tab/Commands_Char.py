import dbus, subprocess
from service import Characteristic


class CommandCharacteristic(Characteristic):
    """
    Characteristic responsible for recieving command from application and running that command on the Pi.

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
    
    Methods:
        WriteValue(value, options): Take command sent from application and run on pi.
    """
    def __init__(self, service, uuid):
        """
        Initialize the class

        Args:
            service (): Service this characteristic is located under.
            uuid (str): This characteristic's UUID
        """
        Characteristic.__init__(
            self, uuid,
            ["write"], service)
    

    def WriteValue(self, value, options):
        """
        Function responsible for recieving and running the command sent from the application.

        Args:
            value (str): Command recieved from the application.
            options ():

        """
        command = ''.join([chr(b) for b in value])
        print(f"Received command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Command output:", result.stdout.decode('utf-8'))
            print("Command error:", result.stderr.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print("Command failed:", e)
    

class CommandCharacteristicWResponse(Characteristic):
    """
    Responsible for recieving and running command sent from application while returning a response

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
    """
    def __init__(self, service, uuid):
        """
        Initialize the class

        Args:
            service (): Service containing this characteristic
            uuid (str): uuid of the characteristic
        """
        Characteristic.__init__(self, uuid, ["write", "read"], service)
        self.result = ""


    def WriteValue(self, value, options):
        """
        Recieves and runs the command sent from the application.

        Args:
            value ():
            options ():
        """
        command = ''.join([chr(b) for b in value])
        print(f"Received command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.result = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
            print("Command output:", self.result)
        except subprocess.CalledProcessError as e:
            self.result = f"Command failed: {e}"
            print("Command failed:", e)


    def ReadValue(self, options):
        return [dbus.Byte(c) for c in self.result]
    