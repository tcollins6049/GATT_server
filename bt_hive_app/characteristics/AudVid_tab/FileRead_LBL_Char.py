import dbus, os
from service import Characteristic
from datetime import datetime


class FileRead_LBL_Characteristic(Characteristic):
    """
    The following characteristic pulls lines from file one at a time.

    Attributes:
        service (): Service containing this characteristic
        uuid (str): uuid of the characteristic
        base_path (str): Path of directory to get most recent file from
    
    Methods:
        get_most_recent_file(base_path): Gets most recent file at base_path
        ReadValue(): Reads line at offset from file
        reset(): Resets offset to 0
    """
    def __init__(self, service, uuid, base_path):
        """
        Initialize the class

        Args:
            service: Service the characteristic is located under
            uuid (str): Characteristic's UUID
            base_path (str): Full path up to where get_most_recent_file() needs to be called.
        """
        Characteristic.__init__(
            self,
            uuid,
            ['read'],
            service)
        self.folder_path = base_path
        self.line_offset = 0
        print(f"Characteristic initialized with UUID: {uuid}")
    

    def get_most_recent_file(self, base_path):
        """
        Function used to get most recent file from the base_path. Ensures were pulling the most up to date info from the Pi.

        Args:
            base_path (str): Path of directory we are pulling most recent file from.

        Returns:
            str: Full path of the most recent file in the base_path directory if successful, None otherwise.

        Raises:
            ValueError: If no files are found in the directory.
        """
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
        files = []
        most_recent_file = '';
        for file in os.listdir(full_path):
            if file.endswith('.csv'):
                files.append(file)
                most_recent_file = file

        if (len(files) < 1):
            raise ValueError(f"No files in the directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return (full_path + '/' + most_recent_file)


    def ReadValue(self):
        """
        Function responsible for reading line from specified file.

        Returns:
            list: Contains line of data if successful, empty otherwise.
        """
        print("ReadValue called")
        self.file_path = self.get_most_recent_file(self.folder_path)

        if self.file_path is not None:
            try:
                with open(self.file_path, 'r') as file:
                    lines = file.readlines()
                    all_data = ''.join(lines)
                    # print(f"Returning data: {all_data}")
                    if (self.line_offset >= len(lines)):
                        self.line_offset = 0
                        return [dbus.Byte(b) for b in 'EOF'.encode()]
                    
                    self.line_offset += 1
                    return [dbus.Byte(b) for b in lines[self.line_offset].encode()]
            except Exception as e:
                # Error while reading file
                return []
        else:
            # File not found
            return []
        

    def reset_offset(self):
        """
        Function responsible for resetting the offset, ensures we start reading from the beginning of the file.
        """
        self.line_offset = 0
        self.file_path = None
        self.lines = []
