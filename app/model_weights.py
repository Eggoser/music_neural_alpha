import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
__import__("matplotlib").use('Agg')

import numpy as np
from keras.models import Model, load_model

import cv2
import json
import io
from pathlib import PurePath

import librosa
import librosa.display


import matplotlib.pyplot as plt

from pydub import AudioSegment
from PIL import Image


if __name__ == '__main__':
    from load_data import load_dataset, create_dataset
else:
    from .load_data import load_dataset, create_dataset



base_dir = PurePath(__file__).parent


class Controller:
    def __init__(self):
        # подготовим модель
        loaded_model = load_model(base_dir / "Saved_Model/Model.h5")
        loaded_model.set_weights(loaded_model.get_weights())

        self.matrix_size = loaded_model.layers[-2].output.shape[1]
        self.model = Model(loaded_model.inputs, loaded_model.layers[-2].output)

        self.predictions_global = None

        self.channels = 1
        self.frequency = 44100
        self.frame_width = 2


    def create_plot(self, f):
        sound = AudioSegment.from_mp3(f)
        sound.export("test.mp3", format="wav")

        y, sr = librosa.load("test.mp3")
        melspectrogram_array = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        mel = librosa.power_to_db(melspectrogram_array)

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

        os.remove("test.mp3")

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
        create_dataset()
        output = load_dataset()
        count_all_images = len(os.listdir(base_dir / "Test_Sliced_Images"))

        predictions = {}

        image_count = 0

        for image, label in load_dataset():
            image = np.expand_dims(image, axis=2) / 255.
            prediction = self.model.predict(np.expand_dims(image, axis=0))

            if label not in predictions:
                predictions[label] = {"prediction": prediction, "count": 1}
                continue

            predictions[label]["prediction"] += prediction
            predictions[label]["count"] += 1

            image_count += 1
            print(f"[+] prediction {round(image_count / count_all_images * 100, 2)}%")

        for i in predictions:
            predictions[i] = (predictions[i]["prediction"] / predictions[i]["count"]).tolist()

        with open(base_dir / "Saved_Model/outputs.json", "w") as log:
            log.write(json.dumps(predictions, ensure_ascii=False))


    def predict(self, raw_track):
        first = np.zeros((1, self.matrix_size))

        raw_image = self.create_plot(raw_track)
        sliced_image = self.slice_image_to_bytes(raw_image) / 255.
        for image in sliced_image:
            first += self.model.predict(np.expand_dims(image, axis=0))
        first /= len(sliced_image)


        if not self.predictions_global:
            with open(base_dir / "Saved_Model/outputs.json") as log:
                self.predictions_global = {i: np.asarray(k) for i, k in json.loads(log.read()).items()}


        distance_array = []
        label_array = []
        for label, second in self.predictions_global.items():
            distance_array.append(np.sum(first * second) / (np.sqrt(np.sum(first**2)) * np.sqrt(np.sum(second**2))))
            label_array.append(label)

        distance_array = np.asarray(distance_array)
        

        distance_and_labels = []
        for _ in range(len(distance_array)):
            index = np.argmax(distance_array)
            distance_and_labels.append((label_array[index], distance_array[index]))
            distance_array[index] = -np.inf

        return distance_and_labels

    def get_labels(self):
        with open(base_dir / "Dataset/tracks_info.json") as log:
            data = json.loads(log.read())

        return data


    def save_labels(self, data):
        with open(base_dir / "Dataset/tracks_info.json", "w") as log:
            data = json.dumps(data, ensure_ascii=False)
            log.write(data)


        return data



if __name__ == '__main__':
    obj = Controller()
    obj.update_dataset()

