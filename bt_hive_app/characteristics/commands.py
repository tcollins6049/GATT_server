# import dbus, os, socket, glob, configparser, subprocess, cv2
import dbus, subprocess
# from advertisement import Advertisement
# from service import Application, Service, Characteristic, Descriptor
from service import Characteristic
# from gpiozero import CPUTemperature
# from datetime import datetime
# import helper_methods as help


class CommandCharacteristic(Characteristic):
    """
    Characteristic responsible for recieving command from application and running that command on the Pi.

    """
    def __init__(self, service, uuid):
        """
        init function

        Args:
            service: Service this characteristic is located under.
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
            options:

        """
        command = ''.join([chr(b) for b in value])
        print(f"Received command: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Command output:", result.stdout.decode('utf-8'))
            print("Command error:", result.stderr.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            print("Command failed:", e)
    

"""
Temporary characteristic, will probably be deleted soon.

"""
class CommandCharacteristicWResponse(Characteristic):
    def __init__(self, service, uuid):
        Characteristic.__init__(self, uuid, ["write", "read"], service)
        self.result = ""

    def WriteValue(self, value, options):
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
    