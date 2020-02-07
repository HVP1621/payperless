#!/usr/bin/env python
# coding: utf-8

import cv2 
import os
import numpy as np
import random
import math
import gc
#import matplotlib.pyplot as plt

#@profile
def preprocess(save_path, out_path):
    im = cv2.imread(save_path)
    print("image read")
    scale_percent = 50 # percent of original size
    width = int(im.shape[1] * scale_percent / 100)
    height = int(im.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    im = cv2.resize(im, dim, interpolation = cv2.INTER_AREA)
     
    blk = np.zeros(im.shape, np.uint8)
    blk[:] = [255,255,255]
    im = (im + blk)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
    print("changed color to Lab")
   
    sample = np.zeros((100,100,3) , dtype='uint8')
    for i in range(100):
        for j in range(100):
            sample[i,j]+=im[random.randint(0, im.shape[0]-1), random.randint(0,im.shape[1]-1)]

    print("randomising matrix made")
    intensity = np.zeros((100,100), dtype='uint16')


    for i in range(100):
        for j in range(100):
            b,g,r = sample[i,j]
            intensity[i,j] = math.sqrt(int(b**3) + int(g**2) + int(r**2))

    print("intensity matrix made")
    # ### Sort according to intensity

    x = np.argsort(intensity, axis=0)
    print("Sorted")
    # ### Create Sorted Sample according to intensity

    sample_sorted = np.zeros(sample.shape, dtype='uint8')
    for i in range(100):
        for j in range(100):
            sample_sorted[i,j] = sample[x[i,j], j]
   
    # ### Bin the values in the sorted sample
    print("made sample_sorted")
    binned = np.zeros(sample.shape, dtype="uint8")
    for i in range(100):
        for j in range(100):
            (b,g,r) = sample_sorted[i,j]
            binned[i,j] = (b>>2)<<2, (g>>2)<<2, (r>>2)<<2


    # ### Define Backgound Color - bck and Threshold - th
    print("binning done")
    bck = binned[90,50]
    th = (20.5)


    # ### Make the background uniform using a threshold

    ## Make a copy of the original L*a*b image
    #im2 = im.copy()
    fall = np.zeros(im.shape, np.uint8)
    fall[:] = bck
    gc.collect()
    distance = np.uint16((np.sum((fall-im)**2, axis=2, dtype= 'int')))
    del fall, binned,x,sample_sorted
    print("distance done")
    # #### Thresholding
    gc.collect()
    im[np.where((distance)**(0.5) < th)] = bck
    #plt.imshow(im2)
    print("np.where done")

    im_g = cv2.cvtColor(im, cv2.COLOR_LAB2BGR)
    #plt.imshow(im_g)
    print("color switch done")

    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(im_g,kernel,iterations = 1)
    #plt.imshow(erosion)
    scale_percent = 50 # percent of original size
    width = int(erosion.shape[1] /scale_percent *100)
    height = int(erosion.shape[0] / scale_percent * 100)
    dim = (width, height)
    # resize image
    erosion = cv2.resize(erosion, dim, interpolation = cv2.INTER_LANCZOS4 )
     

    cv2.imwrite(out_path, erosion)


if __name__ == '__main__':
        preprocess('7.jpg', 'output.jpg')
