# !/usr/bin/env python3
# coding: utf-8
# -*- coding: utf-8 -*-

import numpy as np
from sklearn import svm
from scipy import fft


class GestureClassifier:
    def __init__(self):
        super().__init__()
        self.CATEGORIES = ["steady", "shake"]
        self.MAX_LENGTH = 15
        self._observers = []
        self.raw_x_data = np.array([])
        self.raw_y_data = np.array([])
        self.raw_z_data = np.array([])
        self.predicter = svm.SVC()
        self.train_predicter()

    # Observer pattern taken from https://en.wikipedia.org/wiki/Observer_pattern
    def register_callback(self, func):
        self._observers.append(func)

    def notify_observers(self):
        for func in self._observers:
            func()

    # Gets raw x, y and z accelerometer data from wiimote and tries to predict the gesture using the svm.
    # If gesture 'shake' is detected all observers get notified.
    def add_accelerometer_data(self, x, y, z):
        frequency = self.get_frequency(x, y, z)
        try:
            prediction = self.predicter.predict(np.array(frequency[0].reshape(-1, 1)))
            # Source:
            # https://stackoverflow.com/questions/12297016/how-to-find-most-frequent-values-in-numpy-ndarray
            u, indices = np.unique(prediction, return_inverse=True)
            actual_category = u[np.argmax(np.bincount(indices))]
            if actual_category == "shake":
                self.notify_observers()
        except Exception as e:
            print(e)

    # Calculates frequency of raw x, y and z values
    def get_frequency(self, x, y, z):
        buffer_size = 32
        self.raw_x_data = np.append(self.raw_x_data, x)
        self.raw_y_data = np.append(self.raw_y_data, y)
        self.raw_z_data = np.append(self.raw_z_data, z)
        self.raw_x_data = self.raw_x_data[-buffer_size:]
        self.raw_y_data = self.raw_y_data[-buffer_size:]
        self.raw_z_data = self.raw_z_data[-buffer_size:]
        raw_gesture_data = [self.raw_x_data + self.raw_y_data + self.raw_z_data / 3]
        return [np.abs(fft(l) / len(l))[1:int(len(l) / 2)] for l in raw_gesture_data]

    # Reads csv files containing movement data. These data gets used to train the svm.
    def train_predicter(self):
        all_freq_raw = []
        all_lengths = []
        all_freq = []
        all_categories = []
        for i in range(0, len(self.CATEGORIES)):
            category = self.CATEGORIES[i]
            freq = self.read_csv(category + ".csv")
            all_freq_raw.append(freq)
            all_lengths.append(len(freq))

        min_length = min(all_lengths)
        for i in range(0, len(all_freq_raw)):
            arr = all_freq_raw[i]
            cat = self.CATEGORIES[i]
            all_freq += arr[0:min_length]
            all_categories += min_length * [cat]

        all_freq = np.array(all_freq).reshape(-1, 1)
        self.predicter.fit(all_freq, all_categories)

    # reading csv-file and returning list of frequency-values (without header)
    def read_csv(self, fileName):
        result = []
        for line in open(fileName, "r").readlines():
            result.append(line)
        result = result[1:]
        result = list(map(float, result))
        return result
