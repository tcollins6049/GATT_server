#!/usr/bin/python3
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
