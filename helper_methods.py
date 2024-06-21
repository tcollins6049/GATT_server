import os
from datetime import datetime

# import librosa
# import librosa.display
# import matplotlib.pyplot as plt


def get_most_recent_sensor_file(base_path):
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


'''
def create_waveform_file(base_path):
     # Path to your audio file (.mp3)
    audio_file = base_path

    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Plot the waveform
    plt.figure(figsize=(14, 5))
    librosa.display.waveshow(y, sr=sr)
    plt.title('Waveform of Audio File')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.tight_layout()

    # Save the plot as a JPG file
    output_file = '/home/tcollins6049/GATT_server/waveform.jpg'
    plt.savefig(output_file)

    print(f'Waveform image saved as {output_file}')
'''
