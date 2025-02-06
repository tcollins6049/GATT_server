# Characteristics

## AudVid_tab (Characteristics used in the audio and video tabs in application)
### FileInfoCharacteristic (Located in FileInfo_Char.py)
Retreives information from audio and video files, including file size and RMS level for audio recordings. The audio side of the application was left a bit unfinished so this characteristic is mainly only used in the video tab. 

### FileRead_LBL_Characteristic (Located in FileRead_LBL_Char.py)
Reads lines from the most recent CSV file in a specified directory. It identifies the latest file by date and retrieves lines sequentially. If the end of the file is reached, it returns an "EOF" indicator. Within the application we can read each line from the CSV file and then when EOF is returned, we know that we have finished reading the file.


## Commands_tab (Characteristics used in the commands tab of the application)
### CommandCharacteristic
Handles recieving commands from the application and executing them on the Raspberry Pi. Takes in a string value sent by the application which is then run on the Pi. The output and any errors are printed to the console on the Pi.

### CommandCharacteristicWResponse
Performs the same function as the above characteristic but returns the commands output to the application. 


## Modifications_tab (Characteristics used in the modifications tab of the application)
### Config_rw_Characteristic
Handles reading and writing to the beemon-config.ini file. ReadValue() is called when the application wants to display the variable values and not modify them. WriteValue() is called by the application when we are ready to modify a variable.


## Password (Characteristics for password verification)
### PasswordVerificationCharacteristic
Responsible for verifying password before letting user perform any operations with the Pi. The characteristic recieves the user entered password from the application, compares this to the correct password stored on the Pi, and then returns true or false depending on if the password was accurate or not.


## Sensor_Files (Characteristics for DeviceDetails screen)
### SF_Read_Characteristic (Located in SF_read_Char.py)
Responsible for reading the most recent recorded single sensor value from the Raspberry Pi. It either returns the most recent non nan sensor reading or, if the value is nan, it traces up through the file and finds when nan recordings began and returns this.

### SF_Read_LBL_Characteristic (Located in SF_read_Char.py)
Responsible for reading sensor data, similar to the characteristic above, but here we are able to read the entire file line by line. This allows the application to get all values recorded by a certain sensor and display those values in the graphs.
