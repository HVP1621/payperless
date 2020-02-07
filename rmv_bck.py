import cv2
import os
import numpy as np

def add_alpha_channel(in_path, out_path):
	image = cv2.cvtColor(cv2.imread(in_path), cv2.COLOR_BGR2BGRA)
	image[np.all(image == [0, 0, 0, 255], axis=2)] = [0, 0, 0, 0]
	cv2.imwrite(out_path, image)