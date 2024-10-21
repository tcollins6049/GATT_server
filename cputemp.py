#!/usr/bin/python3
# import os
# import socket
# import subprocess
# from datetime import datetime

# import dbus
# import cv2
# from gpiozero import CPUTemperature

# from advertisement import Advertisement
# from service import Application, Service, Characteristic, Descriptor
from service import Application

# Imports for services and advertisments
from bt_hive_app.BLEAppServiceAndAdvertisement import BLEAdvertisement, BLEService


def main():
    app = Application()
    app.add_service(BLEService(0))
    app.register()

    adv = BLEAdvertisement(0)
    adv.register()

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()


if __name__ == "__main__":
    main()
