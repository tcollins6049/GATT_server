# Bluetooth Hive Connection Application

## Overview
Here are the characteristics, service, and advertisement needed by the React Native application. The application code can be found at this link: https://github.com/tcollins6049/bluetooth_hive_connect. The application is responsible for communicating with the Rasperrby Pi via Bluetooth using this GATT server. It uses these characteristics to read and write data to the pi allowing the user to view data from the sensors connected to the pi as well as modify variables on the pi including sensor states and config file variables.

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
### Code Overview
- **BLEAppServiceAndAdvertisement.py:** Provides the service and advertisment for the application. These will be called by the GATT server.
- **Characteristics Directory:** Contains files for all characteristics used in the application. The application has seperate views so the characteristics are organized into files based on the view those characteristics show up in. 

## Additions
### 1. Changing Password

### 2. Adding a new sensor
