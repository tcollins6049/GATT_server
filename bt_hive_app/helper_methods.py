import os, cv2
from datetime import datetime

import librosa
import librosa.display
import matplotlib.pyplot as plt


def get_most_recent_sensor_file(base_path):
    print("Getting most recent file")
    try:
        # List all directories in the base path
        entries = os.listdir(base_path)
        print(f"Entries: {entries}")
            
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
            print("Not date_dirs")
            return None

        # Find most recent date
        most_recent_dir = max(date_dirs, key=lambda x: x[1])[0]
        print(f"Most_recent_dir: {most_recent_dir}")
        full_path = os.path.join(base_path, most_recent_dir)
        print(f"Full_path: {full_path}")

        # List files in this directory
        files = os.listdir(full_path)
        if (len(files) != 1):
            raise ValueError(f"Expected exactly one file in directory {full_path}, found {len(files)}")
            
        # Get full path of the file
        return full_path + '/' + files[0]
    except:
        print("Failure within get_most_recent_sensor_file()")


def create_waveform_file(audio_file):
    bgcolor = '#e0e0e0'
    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Plot the waveform
    plt.figure(figsize=(14, 5), facecolor=bgcolor)
    librosa.display.waveshow(y, sr=sr)
    plt.gca().set_facecolor(bgcolor)
    plt.title('Waveform of Audio File')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.tight_layout()

    # Save the plot as a JPG file
    output_file = '/home/bee/GATT_server/waveform.jpg'
    plt.savefig(output_file, facecolor=bgcolor)

    print(f'Waveform image saved as {output_file}')
    return output_file


def delete_file(file_path):
        try:
            os.remove(file_path)
            # print(f"Deleted file: {file_path}")
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
        except PermissionError:
            print(f"Error: Permission denied to delete file '{file_path}'")
        except Exception as e:
            print(f"Error: {e}")


def get_most_recent_video_file(base_path):
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
        files = []
        most_recent_file = '';
        for file in os.listdir(full_path):
            if file.endswith('.h264'):
                files.append(file)
                if most_recent_file == '':
                    most_recent_file = file
                else:
                    split_file = (file.split('@')[-1].split('.')[0].split('-'))
                    split_mr_file = (most_recent_file.split('@')[-1].split('.')[0].split('-'))
                    
                    if split_file[0] > split_mr_file[0]:
                        most_recent_file = file
                    elif split_file[0] == split_mr_file[0] and split_file[1] > split_mr_file[1]:
                        most_recent_file = file

        if (len(files) < 1):
            raise ValueError(f"No files in the directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return (full_path + '/' + most_recent_file)


def get_most_recent_audio_file(base_path):
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
        files = []
        most_recent_file = '';
        for file in os.listdir(full_path):
            if file.endswith('.wav'):
                files.append(file)
                if most_recent_file == '':
                    most_recent_file = file
                else:
                    split_file = (file.split('@')[-1].split('.')[0].split('-'))
                    split_mr_file = (most_recent_file.split('@')[-1].split('.')[0].split('-'))
                    
                    if split_file[0] > split_mr_file[0]:
                        most_recent_file = file
                    elif split_file[0] == split_mr_file[0] and split_file[1] > split_mr_file[1]:
                        most_recent_file = file

        if (len(files) < 1):
            raise ValueError(f"No files in the directory {full_path}, found {len(files)}")
        
        # Get full path of the file
        return (full_path + '/' + most_recent_file)


def extract_frame(video_file, frame_number, output_file):
        # Open the video file
        cap = cv2.VideoCapture(video_file)

        # Check if the video file was opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open video file '{video_file}'")
            return

        # Get total number of frames in the video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # print(f"Total frames in the video: {total_frames}")

        # Set the desired frame number
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame
        ret, frame = cap.read()

        if ret:
            # Save the frame as an image file
            cv2.imwrite(output_file, frame)
            print(f"Frame {frame_number} saved as {output_file}")

            # Get size of the saved image file
            file_size = os.path.getsize(output_file)
            # print(f"Size of {output_file}: {file_size} bytes")

            cap.release()
            return output_file
        else:
            print(f"Error: Could not read frame {frame_number} from video")
            cap.release()
            return None
        