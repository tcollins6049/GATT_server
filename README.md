# GATT_server

## Overview
A GATT (Generic Attribute Profile) server is a key componenet in Bluetooth Low Energy (BLE) communication. It defines how data is exchanged over a Bluetooth connection using attributes, which are small pieces of data that can be read, written, or notified by connected devices. This repo contains a GATT server which can accomodate multiple bluetooth services or applications. Each different service or application will be organized into seperate directories for easier management.
### Current Structure
- **bt_hive_app**: This folder contains the service, advertisment, and characteristics for the Bluetooth Hive Connection application. This application manages the Bluetooth communication for monitoring and interacting with a hive. It enables the user to view real time data from sensors and to manage hive properties such as config file variables or enabling and disabling sensors.

## Getting Started
### Required Libraries

### Installing and Running
**Clone the Repository:** Navigate to /home/bee on a Raspberry Pi and run the following command.
```
git clone https://github.com/tcollins6049/GATT_server.git
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
- **cputemp.py:**
- **advertisment.py:**
- **service.py:**
- **bletools.py:**

## Additions

