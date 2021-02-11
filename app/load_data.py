import os
import re
import struct
import numpy as np
import cv2
import math
import librosa
import librosa.display
import matplotlib.pyplot as plt
import pandas as pd

from pydub import AudioSegment
from PIL import Image
from keras.utils import np_utils
from sklearn.model_selection import train_test_split


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

        # поменяем параметры трека на нужные нам
        if sound.channels != self.channels:
            sound = sound.set_channels(self.channels)
        if sound.frame_rate != self.frequency:
            sound = sound.set_frame_rate(self.frequency)
        if sound.frame_width != self.frame_width:
            sound = sound.set_frame_width(self.frame_width)

        # распакуем байты в числа
        y = np.asarray([struct.unpack("h", sound.raw_data[i:i+self.frame_width])[0]
                        for i in range(0, len(sound.raw_data), self.frame_width)]).astype("float32")
        y /= 2 ** 15

        # y, sr = librosa.load(f)
        melspectrogram_array = librosa.feature.melspectrogram(y=y, sr=self.frequency, n_mels=128, fmax=8000)
        mel = librosa.power_to_db(melspectrogram_array)
        # Length and Width of Spectogram
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = float(mel.shape[1]) / float(100)
        fig_size[1] = float(mel.shape[0]) / float(100)
        plt.rcParams["figure.figsize"] = fig_size
        plt.axis('off')
        plt.axes([0., 0., 1., 1.0], frameon=False, xticks=[], yticks=[])
        librosa.display.specshow(mel, cmap='gray_r')


    def firstly(self):
        folder_output = self.template_folder_firstly


        if os.path.exists(folder_output):
            if len(os.listdir(folder_output)):
                return
        else:
            os.makedirs(folder_output)


        for f in [os.path.join(self.folder_tracks_test, f) for f in os.listdir(self.folder_tracks_test) if f.endswith(".mp3")]:
            test_id = re.search('Dataset/YandexTracks/(.+?).mp3', f).group(1)
            # главная функция, которая занимается преобразованием
            self._create_plot(f)
            plt.savefig(folder_output + "/" + test_id + ".jpg", bbox_inches=None, pad_inches=0)
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
            for i in range(number_of_samples):
                start = i * subsample_size
                img_temporary = img.crop((start, 0., start + subsample_size, subsample_size))
                img_temporary.save(folder_output + "/" + str(counter) + "_" + song_variable + ".jpg")
                counter += 1



def load_dataset():
    control = ParseController()
    control.firstly()
    control.secondly()


    filenames = [os.path.join("Test_Sliced_Images", f) for f in os.listdir("Test_Sliced_Images") if f.endswith(".jpg")]
    images = []
    labels = []

    for f in filenames:
        song_variable = re.search('Test_Sliced_Images/.*_(.+?).jpg', f).group(1)
        tempImg = cv2.imread(f, cv2.IMREAD_UNCHANGED)
        images.append(cv2.cvtColor(tempImg, cv2.COLOR_BGR2GRAY))
        labels.append(song_variable)

    images = np.asarray(images)

    return images, labels

