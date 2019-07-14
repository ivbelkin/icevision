from matplotlib.pyplot import imshow
import matplotlib.pyplot as plt


import numpy as np
import cv2
from PIL import Image

#%matplotlib inline

def cv_2_pil(im_cv):
    im_pil = Image.fromarray(im_cv)
    return im_pil

def hisEqulColor(img):
        ycrcb=cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)
        channels=cv2.split(ycrcb)
        cv2.equalizeHist(channels[0],channels[0])
        cv2.merge(channels,ycrcb)
        cv2.cvtColor(ycrcb,cv2.COLOR_YCR_CB2BGR,img)
        return img

def open_and_filter(im_name):
    im = cv2.imread(im_name)
    im = im[:, :, 0 ]
    #print(im[0::2, 0::2].shape)#0::2 - odds, 1::2 - evens
    m = im.shape[0]//2
    n = im.shape[1]//2
    im_out = np.zeros(shape=(m, n, 3))
#     for y in range(m):
#         for x in range(n):
#             im_out[y, x, 0] = im[2 * y + 1, 2 * x + 1]
#             im_out[y, x, 2] = im[2 * y, 2 * x]
#             im_out[y, x, 1] = (im[2 * y, 2 * x + 1]//2 + im[2 * y + 1, 2 * x]//2)
    im_out[:, :, 2] = im[0::2, 0::2] # R
    im_out[:, :, 1] = im[0::2, 1::2]//2 + im[1::2, 0::2]//2 #G
    im_out[:, :, 0] = im[1::2, 1::2] #B
    im_out = np.clip(im_out, a_min=0, a_max=255)
    return cv_2_pil(hisEqulColor(im_out.astype(np.uint8)))
    #return im_out.astype(np.uint8)
