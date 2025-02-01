# Characteristics

## AudVid_tab (Characteristics used in the audio and video tabs in application)
### FileInfoCharacteristic (Located in FileInfo_Char.py)
Retreives information from audio and video files, including file size and RMS level for audio recordings. The audio side of the application was left a bit unfinished so this characteristic is mainly only used in the video tab. 

### FileRead_LBL_Characteristic (Located in FileRead_LBL_Char.py)
Reads lines from the most recent CSV file in a specified directory. It identifies the latest file by date and retrieves lines sequentially. If the end of the file is reached, it returns an "EOF" indicator. Within the application we can read each line from the CSV file and then when EOF is returned, we know that we have finished reading the file.
