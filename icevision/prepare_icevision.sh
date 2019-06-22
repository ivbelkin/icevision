#!/usr/bin/env bash

python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-02-13_1418_left/ \
    --output-file annotations/icevision_2018-02-13_1418_left.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-02-13_1418_left.xml \
    --output-file annotations/icevision_2018-02-13_1418_left_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-02_1239_right/ \
    --output-file annotations/icevision_2018-03-02_1239_right.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-02_1239_right.xml \
    --output-file annotations/icevision_2018-03-02_1239_right_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-07_1322_right/ \
    --output-file annotations/icevision_2018-03-07_1322_right.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-07_1322_right.xml \
    --output-file annotations/icevision_2018-03-07_1322_right_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-07_1325_left/ \
    --output-file annotations/icevision_2018-03-07_1325_left.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-07_1325_left.xml \
    --output-file annotations/icevision_2018-03-07_1325_left_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-07_1336_right/ \
    --output-file annotations/icevision_2018-03-07_1336_right.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-07_1336_right.xml \
    --output-file annotations/icevision_2018-03-07_1336_right_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-07_1354_right/ \
    --output-file annotations/icevision_2018-03-07_1354_right.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-07_1354_right.xml \
    --output-file annotations/icevision_2018-03-07_1354_right_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-07_1357_right/ \
    --output-file annotations/icevision_2018-03-07_1357_right.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-07_1357_right.xml \
    --output-file annotations/icevision_2018-03-07_1357_right_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-16_1316_left/ \
    --output-file annotations/icevision_2018-03-16_1316_left.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-16_1316_left.xml \
    --output-file annotations/icevision_2018-03-16_1316_left_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-16_1347_left/ \
    --output-file annotations/icevision_2018-03-16_1347_left.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-16_1347_left.xml \
    --output-file annotations/icevision_2018-03-16_1347_left_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/training/2018-03-16_1418_left/ \
    --output-file annotations/icevision_2018-03-16_1418_left.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-16_1418_left.xml \
    --output-file annotations/icevision_2018-03-16_1418_left_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/test/2018-02-13_1523_left/ \
    --output-file annotations/icevision_2018-02-13_1523_left_test.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-02-13_1523_left_test.xml \
    --output-file annotations/icevision_2018-02-13_1523_left_test_masks.xml


python icevision/icevision_to_cvat.py \
    --annot-dir ../annotations/test/2018-03-16_1324_left/ \
    --output-file annotations/icevision_2018-03-16_1324_left.xml \
    --labels icevision/icevision_labels.txt

python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-03-16_1324_left.xml \
    --output-file annotations/icevision_2018-03-16_1324_left_masks.xml


python icevision/prepare_for_maskrcnn.py \
    --input-file annotations/icevision_2018-02-13_1523_left.xml \
    --output-file annotations/icevision_2018-02-13_1523_left_masks.xml
