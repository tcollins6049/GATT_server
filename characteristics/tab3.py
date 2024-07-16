import dbus, os, socket, glob, configparser, subprocess, cv2
from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor
from gpiozero import CPUTemperature
from datetime import datetime
import helper_methods as help


# ---------------- Tab 3: Sensor Data Characteristics ---------------------- #
"""
    This class is responsible for reading the cpu temperature from the file

    !! Need to add update functionality !!
"""
class CPUFileReadCharacteristic(Characteristic):
    def __init__(self, service, uuid, base_path):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = base_path
        print(f"Characteristic initialized with UUID: {uuid}")

    def get_most_recent_file(self, base_path):
        print("Getting most recent file")
        # List all directories in the base path
        entries = os.listdir(base_path)
        
        # Filter out possible non directory entries or directories which dont match the data format
        date_dirs = []
        for entry in entries:
            entry_path = os.path.join(base_path, entry)
            if os.path.isdir(entry_path):
                try:
                    # Try to parse the directory name as a date
                    date = datetime.strptime(entry, "%Y-%m-%d")
                    date_dirs.append((entry, date))
                except ValueError:
                    # Skip directories that don't match the date format
                    pass
        if not date_dirs:
            return None

        # Find most recent date
        most_recent_dir = max(date_dirs, key=lambda x: x[1])[0]
        full_path = os.path.join(base_path, most_recent_dir)

        # List files in this directory
        files = os.listdir(full_path)
        if (len(files) != 1):
            raise ValueError(f"Expected exactly one file in directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return full_path + '/' + files[0]


    def get_relevant_line(self):
        with open(self.file_path, 'r') as file:
            # last_line = file.readlines()[-1]
            lines = file.readlines()

            if ('nan' in lines[-1]):
                last_valid_line = None
                for line in reversed(lines):
                    if 'nan' not in line:
                        last_valid_line = line
                        break
                if last_valid_line is None:
                    print('No valid readings found in the file')
                    last_line = lines[0]
                else:
                    print("last valid before nan: ", last_valid_line)
                    last_line = last_valid_line
            else:
                last_line = lines[-1]
        
        return last_line
    

    def get_update_text(self, last_line):
        if 'nan' not in last_line:
            # Text returned will just contain the update date and time
            unformatted_time = (last_line.split(',')[0]).replace('"','')
            time_obj = datetime.strptime(unformatted_time, '%H-%M-%S')
            formatted_time = time_obj.strftime('%I-%M-%S %p')
            date = (self.file_path.split('/')[6])
            
            update_text = (f"Updated on {date} at {formatted_time}")
            return update_text
            
        else:
            # Text will contain when nan values started being recorded
            unformatted_time = (last_line.split(',')[0]).replace('"','')
            time_obj = datetime.strptime(unformatted_time, '%H-%M-%S')
            formatted_time = time_obj.strftime('%I-%M-%S %p')
            date = (self.file_path.split('/')[6])
            
            update_text = (f"Returning nan values since {formatted_time} on {date}")
            return update_text
           


    def ReadValue(self, options):
        print("ReadValue called")
        # self.file_path = self.get_most_recent_file(self.folder_path)
        self.file_path = help.get_most_recent_sensor_file(self.folder_path)

        if self.file_path is not None:
            try:
                last_line = self.get_relevant_line()
                update_text = self.get_update_text(last_line)
                
                returned_data = f"{last_line.strip()}|{update_text}"
                print(f"Returning data: {returned_data}")
                return [dbus.Byte(b) for b in returned_data.encode()]
            except Exception as e:
                print(f"Error occurred while reading the file: {e}")
                return []
        else:
            print("No file found")
            return []
        

class CPUFileReadAllCharacteristic(Characteristic):
    def __init__(self, service, uuid, base_path):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = base_path
        print(f"Characteristic initialized with UUID: {uuid}")
    

    def get_most_recent_file(self, base_path):
        print("Getting most recent file")
        # List all directories in the base path
        entries = os.listdir(base_path)
        
        # Filter out possible non directory entries or directories which dont match the data format
        date_dirs = []
        for entry in entries:
            entry_path = os.path.join(base_path, entry)
            if os.path.isdir(entry_path):
                try:
                    # Try to parse the directory name as a date
                    date = datetime.strptime(entry, "%Y-%m-%d")
                    date_dirs.append((entry, date))
                except ValueError:
                    # Skip directories that don't match the date format
                    pass
        if not date_dirs:
            return None

        # Find most recent date
        most_recent_dir = max(date_dirs, key=lambda x: x[1])[0]
        full_path = os.path.join(base_path, most_recent_dir)

        # List files in this directory
        files = os.listdir(full_path)
        if (len(files) != 1):
            raise ValueError(f"Expected exactly one file in directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return full_path + '/' + files[0]


    def ReadValue(self, options):
        print("ReadValue called")
        self.file_path = self.get_most_recent_file(self.folder_path)

        if self.file_path is not None:
            try:
                with open(self.file_path, 'r') as file:
                    lines = file.readlines()
                    all_data = ''.join(lines)
                    print(f"Returning data: {all_data}")
                    return [dbus.Byte(b) for b in all_data.encode()]
            except Exception as e:
                print(f"Error occurred while reading the file: {e}")
                return []
        else:
            print("No file found")
            return []
        