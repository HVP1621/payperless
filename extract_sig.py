import glob
import os
import random
import sys
import math
import json
from collections import defaultdict
import time
import argparse
import cv2
from PIL import Image, ImageDraw
import numpy as np
from scipy.ndimage.filters import rank_filter
import gc


def dilate(ary, N, iterations): 
    """Dilate using an NxN '+' sign shape. ary is np.uint8."""
    
    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[(N-1)//2,:] = 1  # Bug solved with // (integer division)
    
    dilated_image = cv2.dilate(ary / 255, kernel, iterations=iterations)
    del kernel
    kernel = np.zeros((N,N), dtype=np.uint8)
    kernel[:,(N-1)//2] = 1  # Bug solved with // (integer division)
    dilated_image = cv2.dilate(dilated_image, kernel, iterations=iterations)
    del kernel
    return dilated_image


def props_for_contours(contours, ary):
    """Calculate bounding box & the number of set pixels for each contour."""
    c_info = []
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        c_im = np.zeros(ary.shape)
        cv2.drawContours(c_im, [c], 0, 255, -1)
        c_info.append({
            'x1': x,
            'y1': y,
            'x2': x + w - 1,
            'y2': y + h - 1,
            'sum': np.sum(ary * (c_im > 0))/255
        })
    return c_info


def union_crops(crop1, crop2):
    """Union two (x1, y1, x2, y2) rects."""
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    del crop1, crop2
    return min(x11, x12), min(y11, y12), max(x21, x22), max(y21, y22)


def intersect_crops(crop1, crop2):
    x11, y11, x21, y21 = crop1
    x12, y12, x22, y22 = crop2
    del crop1, crop2
    return max(x11, x12), max(y11, y12), min(x21, x22), min(y21, y22)


def crop_area(crop):
    x1, y1, x2, y2 = crop
    del crop
    return max(0, x2 - x1) * max(0, y2 - y1)


def find_border_components(contours, ary):
    borders = []
    area = ary.shape[0] * ary.shape[1]
    for i, c in enumerate(contours):
        x,y,w,h = cv2.boundingRect(c)
        if w * h > 0.5 * area:
            borders.append((i, x, y, x + w - 1, y + h - 1))
    return borders


def angle_from_right(deg):
    return min(deg % 90, 90 - (deg % 90))


def remove_border(contour, ary):
    """Remove everything outside a border contour."""
    # Use a rotated rectangle (should be a good approximation of a border).
    # If it's far from a right angle, it's probably two sides of a border and
    # we should use the bounding box instead.
    c_im = np.zeros(ary.shape)
    r = cv2.minAreaRect(contour)
    degs = r[2]
    if angle_from_right(degs) <= 10.0:
        box = cv2.boxPoints(r)
        box = np.int0(box)
        cv2.drawContours(c_im, [box], 0, 255, -1)
        cv2.drawContours(c_im, [box], 0, 0, 4)
    else:
        x1, y1, x2, y2 = cv2.boundingRect(contour)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 255, -1)
        cv2.rectangle(c_im, (x1, y1), (x2, y2), 0, 4)
    del r
    return np.minimum(c_im, ary)


def find_components(edges, max_components=16):
    """Dilate the image until there are just a few connected components.
    Returns contours for these components."""
    # Perform increasingly aggressive dilation until there are just a few
    # connected components.
    
    count = 21
    dilation = 5
    n = 100
    while count > 16:
        n += 1
       
        dilated_image = np.uint8(dilate(edges, N=3, iterations=n))
        try:
            _, contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        except:
            contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        count = len(contours)
    return contours


def find_optimal_components_subset(contours, edges):
    """Find a crop which strikes a good balance of coverage/compactness.
    Returns an (x1, y1, x2, y2) tuple.
    """
    c_info = props_for_contours(contours, edges)
    c_info.sort(key=lambda x: -x['sum'])
    total = np.sum(edges) / 255
    area = edges.shape[0] * edges.shape[1]

    c = c_info[0]
    del c_info[0]
    this_crop = c['x1'], c['y1'], c['x2'], c['y2']
    crop = this_crop
    covered_sum = c['sum']

    while covered_sum < total:
        changed = False
        recall = 1.0 * covered_sum / total
        prec = 1 - 1.0 * crop_area(crop) / area
        f1 = 2 * (prec * recall / (prec + recall))
        #print '----'
        for i, c in enumerate(c_info):
            this_crop = c['x1'], c['y1'], c['x2'], c['y2']
            new_crop = union_crops(crop, this_crop)
            new_sum = covered_sum + c['sum']
            new_recall = 1.0 * new_sum / total
            new_prec = 1 - 1.0 * crop_area(new_crop) / area
            new_f1 = 2 * new_prec * new_recall / (new_prec + new_recall)

            # Add this crop if it improves f1 score,
            # _or_ it adds 25% of the remaining pixels for <15% crop expansion.
            # ^^^ very ad-hoc! make this smoother
            remaining_frac = c['sum'] / (total - covered_sum)
            new_area_frac = 1.0 * crop_area(new_crop) / crop_area(crop) - 1
            if new_f1 > f1 or (
                    remaining_frac > 0.25 and new_area_frac < 0.15):
##                print('%d %s -> %s / %s (%s), %s -> %s / %s (%s), %s -> %s' % (
##                        i, covered_sum, new_sum, total, remaining_frac,
##                        crop_area(crop), crop_area(new_crop), area, new_area_frac,
##                        f1, new_f1))
                crop = new_crop
                covered_sum = new_sum
                del c_info[i]
                changed = True
                break

        if not changed:
            break

    return crop


def pad_crop(crop, contours, edges, border_contour, pad_px=15):
    """Slightly expand the crop to get full contours.
    This will expand to include any contours it currently intersects, but will
    not expand past a border.
    """
    bx1, by1, bx2, by2 = 0, 0, edges.shape[0], edges.shape[1]
    if border_contour is not None and len(border_contour) > 0:
        c = props_for_contours([border_contour], edges)[0]
        bx1, by1, bx2, by2 = c['x1'] + 5, c['y1'] + 5, c['x2'] - 5, c['y2'] - 5

    def crop_in_border(crop):
        x1, y1, x2, y2 = crop
        x1 = max(x1 - pad_px, bx1)
        y1 = max(y1 - pad_px, by1)
        x2 = min(x2 + pad_px, bx2) 
        y2 = min(y2 + pad_px, by2)
        return crop
    
    crop = crop_in_border(crop)

    c_info = props_for_contours(contours, edges)
    changed = False
    for c in c_info:
        this_crop = c['x1'], c['y1'], c['x2'], c['y2']
        this_area = crop_area(this_crop)
        int_area = crop_area(intersect_crops(crop, this_crop))
        new_crop = crop_in_border(union_crops(crop, this_crop))
        if 0 < int_area < this_area and crop != new_crop:
##            print('%s -> %s' % (str(crop), str(new_crop)))
            changed = True
            crop = new_crop

    if changed:
        return pad_crop(crop, contours, edges, border_contour, pad_px)
    else:
        return crop


def downscale_image(im, max_dim=2048):
    """Shrink im until its longest dimension is <= max_dim.
    Returns new_image, scale (where scale <= 1).
    """
    #a, b = im.size
    a,b = im.shape[0], im.shape[1]
    if max(a, b) <= max_dim:
        return 1.0, im

    scale = 1.0 * max_dim / max(a, b)
    #new_im = np.array(im.resize((int(a * scale), int(b * scale)), Image.ANTIALIAS))
    new_im = cv2.resize(im, (0,0), fx=scale, fy=scale, interpolation = cv2.INTER_LANCZOS4)
    return scale, new_im

def decrease_scale(img, scale = 50):
    #scale_percent = 40 # percent of original size
    width = int(img.shape[1] * scale / 100)
    height = int(img.shape[0] * scale / 100)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA) 

#@profile
def process_image(path, out_path):
    gc.collect()
    #scale, im = downscale_image(Image.fromarray(cv2.cvtColor(increase_brightness(path), cv2.COLOR_BGR2RGB)))
    #scale = downscale_image(cv2.cvtColor(increase_brightness(path), cv2.COLOR_BGR2RGB))[0]
    img = increase_brightness(path)
    edges = cv2.Canny(downscale_image(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))[1], 100, 200)
    #del im
    print('Downscaled')
    # TODO: dilate image _before_ finding a border. This is crazy sensitive!
    try:
        _, contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    except:
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    borders = find_border_components(contours, edges)
    borders.sort(key=lambda i_x1_y1_x2_y2: (i_x1_y1_x2_y2[3] - i_x1_y1_x2_y2[1]) * (i_x1_y1_x2_y2[4] - i_x1_y1_x2_y2[2]))

    border_contour = None
    if len(borders):
        border_contour = contours[borders[0][0]]
        edges = remove_border(border_contour, edges)


    edges = 255 * (edges > 0).astype(np.uint8)

    # Remove ~1px borders using a rank filter.
    maxed_rows = rank_filter(edges, -4, size=(1, 20))
    maxed_cols = rank_filter(edges, -4, size=(20, 1))
    edges = np.minimum(np.minimum(edges, maxed_rows), maxed_cols)
    
    contours = find_components(edges)
    
    
    crop = find_optimal_components_subset(contours, edges)
    print('find optimal components')

    crop = pad_crop(crop, contours, edges, border_contour)
    
    crop = [int(x / downscale_image(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))[0]) for x in crop]  # upscale to the original image size.
    
    temp = np.array(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).crop(crop))
    text_im = np.array(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).crop(crop))
    imgSize = np.shape(text_im)
    del crop
    new_mask = np.zeros(imgSize, dtype="uint8")

    #final = cv2.cvtColor(text_im, cv2.COLOR_RGB2GRAY)

    # Adaptive Thresholding requires the blocksize to be odd and bigger than 1
    blockSize = 1 // 8 * imgSize[0] // 2 * 2 + 1
    if blockSize <= 1:
       blockSize = imgSize[0] // 2 * 2 + 1
    const = 10
    del imgSize
    print('adaptiveThreshold')
    text_im = cv2.bitwise_and(text_im, text_im, mask=cv2.bitwise_not(cv2.adaptiveThreshold(cv2.cvtColor(text_im, cv2.COLOR_RGB2GRAY), maxValue = 255, adaptiveMethod = cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType = cv2.THRESH_BINARY, blockSize = blockSize, C = const)))

    # print('created text_im')
    scale = 30
    masked_image = cv2.createBackgroundSubtractorMOG2(128,cv2.THRESH_BINARY,1).apply(decrease_scale(text_im,scale))
    del text_im
    # print('enter masked image block')
    masked_image[masked_image==127]=0
    masked_image = cv2.bitwise_not(masked_image)
    # print('11')
    masked_image = cv2.cvtColor(masked_image, cv2.COLOR_GRAY2RGB)
    # print('22')
    masked_image = cv2.bitwise_and(masked_image, decrease_scale(temp,scale))
    # print('33')
    masked_image = cv2.cvtColor(masked_image, cv2.COLOR_RGB2BGR)
    # print('final')
    cv2.imwrite(out_path, masked_image)
    print('%s -> %s' % (path, out_path))

def increase_brightness(img, value=50):
    img = cv2.imread(img)
    
    h, s, v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
    
    if img.mean() > 155:
        v[v > img.mean()*0.7] = 255
        v[v <= img.mean()*0.7] = 0

    
    img = cv2.cvtColor(cv2.merge((h,s,v)), cv2.COLOR_HSV2BGR)
    img[np.where((img==[0,0,0]).all(axis=2))] = [255, 255, 255]

    scale_percent = 30 # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(img, dim, interpolation = cv2.INTER_AREA) 

    return img

if __name__ == '__main__':
    process_image('2.jpg', '2-out.jpg')
