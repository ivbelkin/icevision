import glob
import pandas as pd
from PIL import Image
from albumentations import HorizontalFlip
import numpy as np

sym_signs = ["1.1", "1.3.1", "1.3.2", "1.5", "1.6", "1.8", "1.16", "1.17", "1.20.1", "1.33", "1.34.3", "2.1", "2.3.1", "2.4", "3.1", "3.2", "3.3", "3.27", "3.32", "3.33", "4.1.1", "4.1.6", "4.2.3", "4.8.1", "5.1", "5.3", "5.5", "5.8", "5.10", "5.14", "5.17", "5.20", "6.8.1", "7.1", "7.5", "7.10", "8.2.3", "8.2.4", "8.3.3", "8.4.8", "8.5.1", "8.5.2", "8.14", "8.22.3"]
sym_first = ["1.4.1", "1.4.2", "1.4.3", "1.11.1", "1.12.1", "1.13", "1.20.2", "1.34.1", "2.3.2", "2.3.4", "2.3.6", "3.18.1", "4.1.2", "4.1.4", "4.8.2", "5.7.1", "5.13.1", "5.13.3", "5.15.5", "5.19.1", "6.8.2", "6.20.1", "8.3.1", "8.22.1", ]
sym_second = ["1.4.4", "1.4.5", "1.4.6", "1.11.2", "1.12.2", "1.14", "1.20.3", "1.34.2", "2.3.3", "2.3.5", "2.3.7", "3.18.2", "4.1.3", "4.1.5", "4.8.3", "5.7.2", "5.13.2", "5.13.4", "5.15.6", "5.19.2", "6.8.3", "6.20.2", "8.3.2", "8.22.2"]

set_sym_signs = set(sym_signs)
set_sym_f = set(sym_signs)
set_sym_s = set(sym_second)


#Convert formats
def pil_2_cv(im_pil):
    im_cv = np.asarray(im_pil)
    return im_cv

def cv_2_pil(im_cv):
    im_pil = Image.fromarray(im_cv)
    return im_pil


def is_flipable(label_list):
    f = True
    for label in label_list:
        if not (label in set_sym_f or label in set_sym_s or label in set_sym_signs):
            f = False
    return f


def flip_labels(label_list):
    for i in range(len(label_list)):
        if label_list[i] in sym_first:
            print(label_list[i])
            label_list[i] = sym_second[sym_first.index(label_list[i])]
        else:
            if label_list[i] in sym_second:
                label_list[i] = sym_first[sym_second.index(label_list[i])]
    return label_list



def flip_im(img, bboxes, masks, labels_list):#xtl ytl xbr ytr

    labels_list = flip_labels(labels_list)
    image = pil_2_cv(img)
    image = HorizontalFlip(always_apply=True)(image=image)['image']
    width = image.shape[1]
    for i in range(len(bboxes)):
        bboxes[i][0] = width - bboxes[i][0]
        bboxes[i][2] = width - bboxes[i][0]
    for i in range(len(masks)):
        for j in range(len(masks[i])):
            masks[i][j][0] = width - masks[i][j][0]
    return image, bboxes, masks, labels_list


if __name__ == '__main__':
    im = Image.open(r"/home/serg/CV/Datasets/IceVision/icevision/AutomoldRoadAugmentationLibrary/test_augmentation/image1.jpg")
    bboxes = [[100, 100, 200, 200], [400, 400, 500, 500]]
    masks = [[[100, 200], [300, 400], [500, 600]], [[0, 0], [100, 600], [200, 400]]]
    labels = ["8.22.3", "8.22.1", "1.3.2", "1.34.2"]
    aug_im, bboxes, masks, labels = flip_im(im, bboxes, masks, labels)
    print(bboxes, masks, labels)






