# Bluetooth Hive Connection Application

## Overview
A GATT (Generic Attribute Profile) server is a key componenet in Bluetooth Low Energy (BLE) communication. It defines how data is exchanged over a Bluetooth connection using attributes, which are small pieces of data that can be read, written, or notified by connected devices. This repo contains a GATT server which can accomodate multiple bluetooth services or applications. Each different service or application will be organized into seperate directories for easier management.

## Code Structure
```
bt_hive_app
│   README.md  
│   BLEAppServiceAndAdvertisement.py
|   helper_methods.py
└───characteristics
|   |   password_char.py
|   |   file_sensor_data.py
|   |   sensor_readings.py
|   |   modifications_tab.py
|   |   sensor_states.py
|   |   commands.py
|   |   audio_video.py  

```
### Core Files
- **cputemp.py:** Serves as an entry point for the GATT server. It initializes and registers services and advertisments.
- **advertisment.py:** Responsible for managing BLE advertisements. Utilizes D-Bus for communication with the BlueZ service and allows for configuration of various advertisment properties such as local name and service UUIDs.
- **service.py:** Defines the core components for the GATT server. It includes classes for managing GATT services, characteristics, and descriptors. This enables communication between BLE devices.
- **bletools.py:** Provides functions used for interacting with the BLE stack.

## Additions
### 1. Adding a new service and advertisment

### 2. Creating new characteristics
