__import__("os").environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import keras
from keras.models import Model, load_model
from load_data import load_dataset
import cv2
import time
import sys

# Load the trained model.
loaded_model = load_model("Saved_Model/Model.h5")
loaded_model.set_weights(loaded_model.get_weights())

# Discard the Softmax layer, Second last layer provides the latent feature
# representation.
matrix_size = loaded_model.layers[-2].output.shape[1]
new_model = Model(loaded_model.inputs, loaded_model.layers[-2].output)
# print(new_model.summary())

images, labels = load_dataset(verbose=1, mode="Test")

images = np.expand_dims(images, axis=3)
# Normalize the image.
images = images / 255.
# Display list of available test songs.
print(np.unique(labels))

# Enter a song name which will be an anchor song.
recommend_wrt = input("Enter Song name: ")
print("Loading...")
prediction_anchor = np.zeros((1, matrix_size))

count = 0
predictions_song = []
predictions_label = []
counts = []
distance_array = []


# Calculate the latent feature vectors for all the songs.
for i in range(len(labels)):
    test_image = images[i]
    test_image = np.expand_dims(test_image, axis=0)

    if labels[i] == recommend_wrt:
        prediction = new_model.predict(test_image)
        prediction_anchor = prediction_anchor + prediction
        count += 1
    elif labels[i] not in predictions_label:
        predictions_label.append(labels[i])
        prediction = new_model.predict(test_image)
        predictions_song.append(prediction)
        counts.append(1)
    elif labels[i] in predictions_label:
        index = predictions_label.index(labels[i])
        prediction = new_model.predict(test_image)
        predictions_song[index] = predictions_song[index] + prediction
        counts[index] += 1

# Count is used for averaging the latent feature vectors.
prediction_anchor = prediction_anchor / count
for i in range(len(predictions_song)):
    predictions_song[i] = predictions_song[i] / counts[i]
    # Cosine Similarity - Computes a similarity score of all songs with respect
    # to the anchor song.
    distance_array.append(np.sum(prediction_anchor * predictions_song[i]) / (np.sqrt(np.sum(prediction_anchor**2)) * np.sqrt(np.sum(predictions_song[i]**2))))

distance_array = np.array(distance_array)
recommendations = 100

print("Recommendation is:")

# Number of Recommendations is set to 2.
for i in range(recommendations):
    index = np.argmax(distance_array)
    value = distance_array[index]
    print("Song Name: " + predictions_label[index] + " with value = %f" % (value))
    distance_array[index] = -np.inf
    recommendations =+ 1
