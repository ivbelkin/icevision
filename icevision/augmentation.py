import AutomoldRoadAugmentationLibrary.Automold as aug
from PIL import Image
import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt

#load from folder
def load_images(im_folder_path, im_format="jpeg"):
    images_names = glob.glob(im_folder_path + '/*.' + im_format)
    im_list = []
    for image in images_names:
        im_list.append(Image.open(image))
    return im_list


#Convert formats
def pil_2_cv(im_pil_list):
    im_cv_l = []
    for im_pil in im_pil_list:
        im_cv = np.asarray(im_pil)
        im_cv_l.append(im_cv)
    return im_cv_l

def cv_2_pil(im_cv_list):
    im_pil_l = []
    for im_cv in im_cv_list:
        im_pil = im_cv
        im_pil_l.append(im_pil)
    return im_pil_l


#visualize images
def vizualize(im_list, columns):
    fig = plt.figure(figsize=(16 , 9))
    rows = np.ceil(len(im_list) / columns)
    for i in range(len(im_list)):
        a  = fig.add_subplot(rows, columns, i + 1)
        a.imshow(np.asarray(im_list[i]))
    fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    plt.show(fig)

#add effects
def effects(im_list, effect, coeff = 0.5):
    cv_im_list = pil_2_cv(im_list)
    res_list = []
    if effect=="fog":
        res_list = aug.add_fog(cv_im_list, fog_coeff=coeff)
    elif effect=="sun":
        res_list = aug.add_sun_flare(cv_im_list)
    elif effect=="snow":
        res_list = aug.add_snow(cv_im_list, coeff)
    elif effect=="speed":
        res_list = aug.add_speed(cv_im_list, coeff)
    return  cv_2_pil(res_list)







if __name__ == '__main__':
    im_l = load_images("/home/serg/CV/Datasets/IceVision/icevision/TestAug", im_format="jpg")

    vizualize(effects(im_l[0:4], "sun"), 2)
