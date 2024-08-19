import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help


# ---------------- Tab 5: Command Characteristics ---------------------- #
"""
This class is responsible for running a command on the pi sent from the app
"""
class CommandCharacteristic(Characteristic):
    # COMMAND_CHARACTERISTIC_UUID = "00000023-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service, uuid):
        Characteristic.__init__(
            self, uuid,
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
    