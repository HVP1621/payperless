import os
import cv2
import argparse
import numpy as np


def darken(inpath, outpath):
    im = cv2.imread(inpath, cv2.IMREAD_UNCHANGED)
    filter = np.ones(im.shape, dtype='uint8')*100
    im_dark = cv2.dilate(im, np.ones( (2,2), dtype='uint8'), iterations = 1)
    im_dark = cv2.subtract(im_dark, filter)
    cv2.imwrite(outpath, im_dark)


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument("--input", required = True, help = 'Path to an image')
    ap.add_argument("--ouput", required = True, help = 'Destination path')
    args = vars(ap.parse_args())
    darken(args['input'], args['outpath'])

    
    
