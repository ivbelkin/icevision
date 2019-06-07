import argparse
import os
import pandas as pd
import torch

from tqdm import tqdm

from icevision.cvat import CvatDataset


def build_parser():
    parser = argparse.ArgumentParser("Convert maskrcnn predictions to cvat-compatible xml")
    parser.add_argument(
        "--predictions",
        type=str,
        help="maskrcnn predictions in *.pth dictionary"
    )
    parser.add_argument(
        "--output-file",
        help="file with *.xml cvat annotations"
    )
    return parser


def main(args):
    predictions = torch.load(args.predictions)
    ds = CvatDataset()

    for image_id, prediction in enumerate(tqdm(predictions)):
        ds.add_image(image_id)
        for box_id in range(len(prediction)):
            bbox = prediction.bbox[box_id].numpy()
            label = prediction.get_field("labels")[box_id].numpy()
            ds.add_box(
                image_id, xtl=bbox[0], ytl=bbox[1], xbr=bbox[2], ybr=bbox[3], label=label
            )

    ds.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
