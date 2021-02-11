__import__("os").environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
# import keras
import struct
from keras.models import Model, load_model
from load_data import load_dataset
import cv2
import json
import io

import librosa
import librosa.display
import matplotlib.pyplot as plt
from pydub import AudioSegment
from PIL import Image



class Controller:
    def __init__(self):
        # подготовим модель
        loaded_model = load_model("Saved_Model/Model.h5")
        loaded_model.set_weights(loaded_model.get_weights())

        self.matrix_size = loaded_model.layers[-2].output.shape[1]
        self.model = Model(loaded_model.inputs, loaded_model.layers[-2].output)

        self.predictions_global = None

        self.channels = 1
        self.frequency = 44100
        self.frame_width = 2
        #
        #
    def create_plot(self, f):
        sound = AudioSegment.from_mp3(io.BytesIO(f))
        #
        # поменяем параметры трека на нужные нам
        if sound.channels != self.channels:
            sound = sound.set_channels(self.channels)
        if sound.frame_rate != self.frequency:
            sound = sound.set_frame_rate(self.frequency)
        if sound.frame_width != self.frame_width:
            sound = sound.set_frame_width(self.frame_width)
        #
        # распакуем байты в числа
        y = np.asarray([struct.unpack("h", sound.raw_data[i:i+self.frame_width])[0]
                        for i in range(0, len(sound.raw_data), self.frame_width)]).astype("float32")
        y /= 2 ** 15
        #
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

        output = io.BytesIO()
        plt.savefig(output, bbox_inches=None, pad_inches=0)
        plt.close()

        return output.getvalue()


    def slice_image_to_bytes(self, raw_image):
        img = Image.open(io.BytesIO(raw_image))
        subsample_size = 128
        number_of_samples = img.size[0] // subsample_size

        crops = []

        for i in range(number_of_samples):
            start = i * subsample_size
            img_temporary = img.crop((start, 0, start + subsample_size, subsample_size))

            output = io.BytesIO()
            img_temporary.convert("RGB").save(output, format='JPEG')
            tempImg = cv2.imdecode(np.frombuffer(output.getvalue(), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            crops.append(cv2.cvtColor(tempImg, cv2.COLOR_BGR2GRAY))

        return np.asarray(crops)

    def update_dataset(self):
        # images, labels = load_dataset()
        # images = np.expand_dims(images, axis=3) / 255
        output = load_dataset()

        predictions = {}

        for image, label in load_dataset():
            image = np.expand_dims(image, axis=2) / 255
            prediction = self.model.predict(np.expand_dims(image, axis=0))
            
            if label not in predictions:
                print("[+] prediction")
                predictions[label] = {"prediction": prediction, "count": 0}
                continue

            predictions[label]["prediction"] += prediction
            predictions[label]["count"] += 1

        for i in predictions:
            predictions[i] = (predictions[i]["prediction"] / predictions[i]["count"]).tolist()

        with open("Saved_Model/outputs.json", "w") as log:
            log.write(json.dumps(predictions, ensure_ascii=False))


    def predict(self, raw_track):
        first = np.zeros((1, self.matrix_size))

        raw_image = self.create_plot(raw_track)
        sliced_image = self.slice_image_to_bytes(raw_image)
        for image in sliced_image:
            first += self.model.predict(np.expand_dims(image, axis=0))
        first /= len(sliced_image)


        if not self.predictions_global:
            with open("Saved_Model/outputs.json") as log:
                self.predictions_global = {i: np.asarray(k) for i, k in json.loads(log.read()).items()}


        distance_array = []
        for _, second in self.predictions_global.items():
            distance_array.append(np.sum(first * second) / (np.sqrt(np.sum(first**2)) * np.sqrt(np.sum(second**2))))

        distance_array = np.asarray(distance_array)
        

        recommendations = 100
        for _ in range(recommendations):
            index = np.argmax(distance_array)
            value = distance_array[index]
            print("Song Name: with value = %f" % (value))
            distance_array[index] = -np.inf
            # recommendations =+ 1


obj = Controller()
obj.update_dataset()

# with open("Dataset/YandexTracks/Выдыхай.mp3", "rb") as log:
#     data = log.read()

# obj.predict(data)
