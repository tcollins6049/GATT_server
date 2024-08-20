import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
# import helper_methods as help


# Constants for GATT characteristic interface and notification timeout
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 5000


# ---------------- Sensor Reading Characteristics ---------------------- #
"""
    This class is responsible for reading the cpu temperature.
"""
class TempCharacteristic(Characteristic):
    TEMP_CHARACTERISTIC_UUID = "00000002-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        self.notifying = False

        Characteristic.__init__(
                self, self.TEMP_CHARACTERISTIC_UUID,
                ["notify", "read"], service)
        self.add_descriptor(TempDescriptor(self))

    def get_temperature(self):
        value = []
        unit = "C"

        cpu = CPUTemperature()
        temp = cpu.temperature
        if self.service.is_farenheit():
            temp = (temp * 1.8) + 32
            unit = "F"

        strtemp = str(round(temp, 1)) + " " + unit
        for c in strtemp:
            value.append(dbus.Byte(c.encode()))

        return value

    def set_temperature_callback(self):
        if self.notifying:
            value = self.get_temperature()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])

        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True

        value = self.get_temperature()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": value}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_temperature_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_temperature()

        return value


class TempDescriptor(Descriptor):
    TEMP_DESCRIPTOR_UUID = "2901"
    TEMP_DESCRIPTOR_VALUE = "CPU Temperature"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.TEMP_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.TEMP_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value


class UnitCharacteristic(Characteristic):
    UNIT_CHARACTERISTIC_UUID = "00000003-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.UNIT_CHARACTERISTIC_UUID,
                ["read", "write"], service)
        self.add_descriptor(UnitDescriptor(self))

    def WriteValue(self, value, options):
        val = str(value[0]).upper()
        if val == "C":
            self.service.set_farenheit(False)
        elif val == "F":
            self.service.set_farenheit(True)

    def ReadValue(self, options):
        value = []

        if self.service.is_farenheit(): val = "F"
        else: val = "C"
        value.append(dbus.Byte(val.encode()))

        return value


class UnitDescriptor(Descriptor):
    UNIT_DESCRIPTOR_UUID = "2901"
    UNIT_DESCRIPTOR_VALUE = "Temperature Units (F or C)"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.UNIT_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.UNIT_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value




#------------- Humidity / temp sensor testing -------------------#
class TempHumidityCharacteristic(Characteristic):
    TEMP_HUMIDITY_CHARACTERISTIC_UUID = "00000004-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, service):
        Characteristic.__init__(
            self, self.TEMP_HUMIDITY_CHARACTERISTIC_UUID,
            ["read"], service)
        self.add_descriptor(TempHumidityDescriptor(self))

    def get_temp_humidity(self):
        value = []
        unit_temp = "C"
        unit_humidity = "%"

        # Replace these lines with your actual sensor reading logic
        temperature = 25.0  # Dummy value for temperature
        humidity = 60.0     # Dummy value for humidity

        if self.service.is_fahrenheit():
            temperature = (temperature * 1.8) + 32
            unit_temp = "F"

        strtemp = f"Temp: {round(temperature, 1)} {unit_temp}"
        strhumidity = f"Humidity: {round(humidity, 1)} {unit_humidity}"
        sensor_data = f"{strtemp}, {strhumidity}"

        for c in sensor_data:
            value.append(dbus.Byte(c.encode()))

        print("THIS IS THE VALUE OF THE TEMP/HUM: ", value)
        return value

    def ReadValue(self, options):
        print("INSIDE THE READ VALUE WITHIN TEMP/HUM")
        value = self.get_temp_humidity()
        print("VALUE WITHIN READ FOR TEMP / HUM", value)
        return value

class TempHumidityDescriptor(Descriptor):
    TEMP_HUMIDITY_DESCRIPTOR_UUID = "2901"
    TEMP_HUMIDITY_DESCRIPTOR_VALUE = "Temperature and Humidity Sensor"

    def __init__(self, characteristic):
        Descriptor.__init__(
            self, self.TEMP_HUMIDITY_DESCRIPTOR_UUID,
            ["read"],
            characteristic)

    def ReadValue(self, options):
        value = []
        desc = self.TEMP_HUMIDITY_DESCRIPTOR_VALUE

        for c in desc:
            value.append(dbus.Byte(c.encode()))

        return value