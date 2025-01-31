# GATT_server

## Overview
A GATT (Generic Attribute Profile) server is a key componenet in Bluetooth Low Energy (BLE) communication. It defines how data is exchanged over a Bluetooth connection using attributes, which are small pieces of data that can be read, written, or notified by connected devices. This repo contains a GATT server which can accomodate multiple bluetooth services or applications. Each different service or application will be organized into seperate directories for easier management.
### Current Structure
- **bt_hive_app**: This folder contains the service, advertisment, and characteristics for the Bluetooth Hive Connection application. This application manages the Bluetooth communication for monitoring and interacting with a hive. It enables the user to view real time data from sensors and to manage hive properties such as config file variables or enabling and disabling sensors.

For documentation on the Bluetooth Hive Connection application, see [bt_hive_app_docs.md](docs/bt_hive_app_docs.md).

## Getting Started
### Installing and Running
**Clone the Repository:** Navigate to /home/bee on a Raspberry Pi and run the following command.
```
git clone https://github.com/tcollins6049/GATT_server.git
```

**Download Dependencies:** On the raspberry pi, run the following commands.
```
sudo apt install libdbus-1-dev libdbus-glib-1-dev
sudo apt-get install libcairo2-dev cmake libgirepository1.0-dev
pip install dbus-python pycairo PyGObject opencv-python pydub
```

**beemon-config modifications:** In the file */home/bee/AppMAIS/beemon-config.ini*, add the following lines to the *[video]* section.
```
capture_window_start_time = 0800
capture_window_end_time = 2000
capture_duration_seconds = 60
capture_interval_seconds = 300
```

**Running:** Run the following command to start advertising services.
```
python3 cputemp.py
```
   
## Code Structure
```
GATT_Server
│   README.md  
│   advertisment.py
|   bletools.py
|   cputemp.py
|   service.py
└───bt_hive_app
└───docs
    │   bt_hive_app_docs.md

```
### Core Files
- **cputemp.py:** Serves as an entry point for the GATT server. It initializes and registers services and advertisments.
- **advertisment.py:** Responsible for managing BLE advertisements. Utilizes D-Bus for communication with the BlueZ service and allows for configuration of various advertisment properties such as local name and service UUIDs.
- **service.py:** Defines the core components for the GATT server. It includes classes for managing GATT services, characteristics, and descriptors. This enables communication between BLE devices.
- **bletools.py:** Provides functions used for interacting with the BLE stack.

## Additions
### 1. Adding a new service and advertisment

### 2. Creating new characteristics
