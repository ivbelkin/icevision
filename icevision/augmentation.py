import AutomoldRoadAugmentationLibrary.Automold as aug
from PIL import Image
import glob
import numpy as np
import cv2
import matplotlib.pyplot as plt
import random
from albumentations import (GaussianBlur, GaussNoise, Compose, RandomBrightnessContrast )

#load from folder
def load_images(im_folder_path, im_format="jpeg"):
    images_names = glob.glob(im_folder_path + '/*.' + im_format)
    im_list = []
    for image in images_names:
        im_list.append(Image.open(image))
    return im_list

#Convert formats
def pil_2_cv(im_pil):
    im_cv = np.asarray(im_pil)
    return im_cv

def cv_2_pil(im_cv):
    im_pil = Image.fromarray(im_cv)
    return im_pil


#visualize images
def vizualize(im_list, columns):
    fig = plt.figure(figsize=(16, 9))
    rows = np.ceil(len(im_list) / columns)
    for i in range(len(im_list)):
        a = fig.add_subplot(rows, columns, i + 1)
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


#########################################################################

def transform(image_pil, nightly=False, hard=False):
    aug_im = pil_2_cv(image_pil)

    #probabilities
    shadow_add_p = 0.05

    sun_add_p = 0.4
    rain_add_p = 0.4
    speed_add_p = 0.2

    g_blur_p = 0.4
    g_noise_p = 1
    br_con_p = 0.4


    ###################
    first_aug = None
    if not nightly:
        if desc(shadow_add_p):
            aug_im = aug.add_shadow(aug_im, no_of_shadows=random.randrange(1) + 1, shadow_dimension=4)
        first_aug = "shadow"
    #get aug

    height = aug_im.shape[0]
    width = aug_im.shape[1]
    y = random.randrange(height//3)
    x = random.randrange(width)
    aug_list = ['aug.add_sun_flare(aug_im, flare_center=(x, y), src_color=(255, 255, 255), src_radius=150, no_of_flare_circles=2)',
                'aug.add_speed(aug_im, random.randrange(30, 60)/100)',
                'aug.add_rain(aug_im, drop_length=random.randrange(10, 30))']
    weights = [sun_add_p, speed_add_p, rain_add_p]
    to_aug = desc_many(aug_list, weights)

    aug_im = eval(to_aug)

    aug_im = GaussianBlur(p=g_blur_p, blur_limit=10)(image=aug_im)['image']
    aug_im = GaussNoise(p=g_noise_p, var_limit=(0, 50))(image=aug_im)['image']
    aug_im = RandomBrightnessContrast(brightness_limit=0.07, contrast_limit=0.07, p=br_con_p)(image=aug_im)['image']
    return cv_2_pil(aug_im)


#########################################################################

def desc(p=0.5):
    return random.randrange(100) < p * 100


def desc_many(augs:dict, weights):
    weights = weights/np.sum(weights)
    t_w  = [0]
    for i in range(len(weights)):
        t_w.append(t_w[i] + weights[i])
    r = random.randrange(100)/100
    for i in range(len(augs)):
        if t_w[i] < r <= t_w[i + 1]:
            return augs[i]




if __name__ == '__main__':
    im_l = load_images("/home/serg/CV/Datasets/IceVision/", im_format="jpg")
    for i in range(len(im_l)):
       for j in range(20):
           transform(im_l[0]).save("/home/serg/CV/Datasets/IceVision/icevision/AutomoldRoadAugmentationLibrary/test_augmentation/Augmented/" +  str(i) + "_" + str(j) + '.jpeg', "jpeg")

    vizualize([im_l[0], transform(im_l[0])], 2)

