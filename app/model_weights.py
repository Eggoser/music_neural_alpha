__import__("os").environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import keras
from keras.models import Model, load_model
from load_data import load_dataset
import cv2
import json
import io


class Controller:
    def __init__(self):
        # подготовим модель
        loaded_model = load_model("Saved_Model/Model.h5")
        loaded_model.set_weights(loaded_model.get_weights())

        self.matrix_size = loaded_model.layers[-2].output.shape[1]
        self.model = Model(loaded_model.inputs, loaded_model.layers[-2].output)

        self.predictions_global = None


    def slice_image_to_bytes(self, raw_image):
        img = Image.open(io.BytesIO(raw_image))
        subsample_size = 128
        number_of_samples = img.size[0] // subsample_size

        crops = []

        for i in range(number_of_samples):
            start = i * subsample_size
            img_temporary = img.crop((start, 0, start + subsample_size, subsample_size))

            output = io.BytesIO()
            img_temporary.save(output, format='JPEG')
            crops.append(output.getvalue())

        return crops

    def update_dataset(self):
        images, labels = load_dataset()
        images = np.expand_dims(images, axis=3) / 255

        predictions = {}
        
        for image, label in zip(images, labels):
            prediction = self.model.predict(np.expand_dims(image, axis=0))

            if label not in predictions:
                predictions[label] = {"prediction": prediction, "count": 0}
                continue

            predictions[label]["prediction"] += prediction
            predictions[label]["count"] += 1

        for i in predictions:
            predictions[i] = (predictions[i]["prediction"] / predictions[i]["count"]).tolist()

        with open("Saved_Model/outputs.json", "w") as log:
            log.write(json.dumps(predictions, ensure_ascii=False))


    def predict(self, raw_image):
        first = np.zeros((1, self.matrix_size))

        sliced_image = self.slice_image_to_bytes(raw_image)
        for image in sliced_image:
            first += self.model.predict(np.expand_dims(image, axis=0))
        first /= len(sliced_image)


        if not self.predictions_global:
            with open("Saved_Model/outputs.json") as log:
                self.predictions_global = [np.asarray(i) for i in json.loads(log.read())]


        distance_array = []
        for _, second in self.predictions_global:
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
