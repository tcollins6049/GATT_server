import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help

import subprocess
from gi.repository import GLib
from dbus.service import Object, method, signal


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
    

class CommandCharacteristicWResponse(Object):
    def __init__(self, bus, index):
        Object.__init__(self, bus, f"/org/example/service{index}/characteristic0")
        self.value = []
        self.index = index
        self.bus = bus
        self.loop = GLib.MainLoop()

    @method(dbus_interface='org.example.service1.characteristic0', in_signature='s', out_signature='ay')
    def WriteValue(self, value):
        command = value.decode('utf-8')  # Convert byte array to string
        print(f"Received command: {command}")
        
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout + result.stderr
            print("Command output:", output.decode('utf-8'))
            return output  # Return command output as byte array
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {e}"
            print("Command failed:", error_msg)
            return error_msg.encode('utf-8')  # Return error message as byte array

    @method(dbus_interface='org.example.service1.characteristic0', out_signature='ay')
    def ReadValue(self):
        return self.value

DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
mainloop = GLib.MainLoop()

# Replace '1' with the appropriate service index for your characteristic
characteristic = CommandCharacteristicWResponse(bus, 1)

try:
    mainloop.run()
except KeyboardInterrupt:
    mainloop.quit()
    