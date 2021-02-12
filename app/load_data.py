import os
import re
import struct
import io
import numpy as np
import cv2
import math
import librosa
import librosa.display
import matplotlib.pyplot as plt

from pydub import AudioSegment
from PIL import Image


class ParseController:
    def __init__(self):
        self.filename_metadata = "Dataset/fma_metadata/tracks.csv"
        self.folder_tracks = "Dataset/fma_small"
        self.folder_tracks_test = "Dataset/YandexTracks"

        self.template_folder_firstly = "Test_Spectogram_Images"
        self.template_folder_secondfly = "Test_Sliced_Images"

        self.channels = 1
        self.frequency = 44100
        self.frame_width = 2
    def _create_plot(self, f):
        sound = AudioSegment.from_mp3(f)
        sound.export("test.mp3", format="wav")

        y, sr = librosa.load("test.mp3")
        melspectrogram_array = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        mel = librosa.power_to_db(melspectrogram_array)
        # Length and Width of Spectogram
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = float(mel.shape[1]) / float(100)
        fig_size[1] = float(mel.shape[0]) / float(100)
        plt.rcParams["figure.figsize"] = fig_size
        plt.axis('off')
        plt.axes([0., 0., 1., 1.0], frameon=False, xticks=[], yticks=[])
        librosa.display.specshow(mel, cmap='gray_r')

        os.remove("test.mp3")


    def firstly(self):
        folder_output = self.template_folder_firstly


        if not os.path.exists(folder_output):
            os.makedirs(folder_output)


        for f in [os.path.join(self.folder_tracks_test, f) for f in os.listdir(self.folder_tracks_test) if f.endswith(".mp3")]:
            test_id = re.search('Dataset/YandexTracks/(.+?).mp3', f).group(1)
            filename = folder_output + "/" + test_id + ".jpg"
            # главная функция, которая занимается преобразованием
            print(filename)
            if not os.path.isfile(filename):
                self._create_plot(f)
                plt.savefig(filename, bbox_inches=None, pad_inches=0)
                plt.close()


    def secondly(self):
        folder_output_firstly = self.template_folder_firstly
        folder_output = self.template_folder_secondfly

        if os.path.exists(folder_output):
            if len(os.listdir(folder_output)):
                return
        else:
            os.makedirs(folder_output)

        labels = []
        filenames = [os.path.join(folder_output_firstly, f) for f in os.listdir(folder_output_firstly)
                       if f.endswith(".jpg")]

        counter = 0
        re_temp = '/(.+?).jpg'

        for f in filenames:
            song_variable = re.search(folder_output_firstly + re_temp, f).group(1)
            img = Image.open(f)
            subsample_size = 128
            width, height = img.size
            number_of_samples = width // subsample_size
            print(f)
            for i in range(number_of_samples):
                start = i * subsample_size
                img_temporary = img.crop((start, 0., start + subsample_size, subsample_size))
                img_temporary.save(folder_output + "/" + str(counter) + "_" + song_variable + ".jpg")
                counter += 1

def create_dataset():
    control = ParseController()
    control.firstly()
    control.secondly()


def load_dataset():
    filenames = [os.path.join("Test_Sliced_Images", f) for f in os.listdir("Test_Sliced_Images") if f.endswith(".jpg")]

    for f in filenames:
        song_variable = re.search('Test_Sliced_Images/.*_(.+?).jpg', f).group(1)
        tempImg = cv2.imread(f, cv2.IMREAD_UNCHANGED)
        # images.append(cv2.cvtColor(tempImg, cv2.COLOR_BGR2GRAY))
        # labels.append(song_variable)
        yield cv2.cvtColor(tempImg, cv2.COLOR_BGR2GRAY), song_variable

    # images = np.asarray(images)

    # return images, labels

