import dbus, os
from service import Characteristic
import bt_hive_app.helper_methods as help
from pydub import AudioSegment


class FileInfoCharacteristic(Characteristic):
    """
    This class holds the charactersitics code for pulling info from audio and video files.
    Pulls data such as file size and RMS level.

    """
    def __init__(self, service, uuid, file_path, file_type):
        """
        init function

        Args:
            service: Service this characteristic is under
            uuid (str): uuid for this characteristic
            file_path (str): Path of the file we are reading info from
            file_type (str): Either 'audio' or 'video'.
        
        """
        super().__init__(
            uuid,
            ['read'],
            service)
        self.file_path = file_path
        self.file_type = file_type


    def ReadValue(self, options):
        """
        Function responsible for reading information from file at file_path

        Args:
            options: 

        """
        temp_file_path = self.file_path

        if self.file_type == 'audio':
            temp_file_path = help.get_most_recent_audio_file(temp_file_path)
        elif self.file_type == 'video':
            temp_file_path = help.get_most_recent_video_file(temp_file_path)

        
        print("FILE PATH: ", temp_file_path)

        file_size_wav = os.path.getsize(temp_file_path)

        if temp_file_path.endswith('.wav'):
            audio = AudioSegment.from_wav(temp_file_path)
            mp3_file_name = os.path.basename(temp_file_path).replace('.wav', '.mp3')
            mp3_file_path = os.path.join('/home/bee/GATT_server', mp3_file_name)
            audio.export(mp3_file_path, format='mp3')
            file_size_mp3 = os.path.getsize(mp3_file_path)
            os.remove(mp3_file_path)

            rms_level, silence_detected = self.calculate_rms_and_check_silence(audio)
        else:
            file_size_mp3 = 0
            rms_level = 0
            silence_detected = False

        file_info = (f"{temp_file_path}, File Size: {file_size_wav} bytes, File Size: {file_size_mp3} bytes, "
                     f"RMS Level: {rms_level}, Silence Detected: {'Yes' if silence_detected else 'No'}")
        print('FileInfoCharacteristic Read: {}'.format(file_info))

        return [dbus.Byte(c) for c in file_info.encode()]
    

    def calculate_rms_and_check_silence(self, audio_segment):
        """
        Function used to calculate the rms level of the audio recording and determine if it is silent

        Args:
            audio_segment: audio segment taken from the read .wav file
        
        """
        rms_level = audio_segment.rms
        print('RMS Level: {}'.format(rms_level))
        
        # Define a suitable threshold based on your requirements
        silence_threshold = 100
        silence_detected = rms_level < silence_threshold
        print('Silence detected' if silence_detected else 'Sound detected')

        return rms_level, silence_detected
