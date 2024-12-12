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
The password is currently stored in a .txt file in the GATT_Server directory on the Raspberry Pi. In order to change this password, you need to just go into this file and change the password.

However, you will probably also want to change the path of where this file is located. Once you change the path, you will need to update the characteristic on the GATT server so that it can find the file. Do this through the steps below:
- Go to the file "BLEAppServiceAndAdvertisement.py"
- On line 82 within the  __init_ function you will see the following line of code:
  ```
  self.add_characteristic(PasswordVerificationCharacteristic(self, '00000601-710e-4a5b-8d75-3e5b444bc3cf', '/home/bee/GATT_server/password.txt'))
  ```

### 2. Adding a new sensor
