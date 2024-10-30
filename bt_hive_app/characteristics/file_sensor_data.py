import dbus, os
from service import Characteristic
from datetime import datetime
import bt_hive_app.helper_methods as help


class CPUFileReadAllCharacteristic(Characteristic):
    def __init__(self, service, uuid, base_path):
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = base_path
        # print(f"Characteristic initialized with UUID: {uuid}")
    

    def get_most_recent_file(self, base_path):
        # print("Getting most recent file")
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
        # print("ReadValue called")
        self.file_path = self.get_most_recent_file(self.folder_path)

        if self.file_path is not None:
            try:
                with open(self.file_path, 'r') as file:
                    lines = file.readlines()
                    all_data = ''.join(lines)
                    # print(f"Returning data: {all_data}")
                    return [dbus.Byte(b) for b in all_data.encode()]
            except Exception as e:
                # print(f"Error occurred while reading the file: {e}")
                return []
        else:
            # print("No file found")
            return []
