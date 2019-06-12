import argparse
import os

import pandas as pd

from icevision.cvat import CvatDataset
from tqdm import tqdm


def build_parser():
    parser = argparse.ArgumentParser("Convert RTDS dataset to cvat format")
    parser.add_argument(
        "--annot",
        type=str,
        help="Directory with RTDS *.csv files"
    )
    parser.add_argument(
        "--image-dir",
        type=str,
        help="Directory with images"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to output file"
    )
    return parser


def main(args):
    data = pd.read_csv(args.annot).set_index("filename")
    ds = CvatDataset()
    image_names = sorted(os.listdir(args.image_dir))
    for image_id, filename in enumerate(tqdm(image_names)):
        ds.add_image(image_id)
        ds.set_name(image_id, filename)
        if filename in data.index:
            sdf = data.loc[filename:filename]
            for record in sdf.to_dict("records"):
                ds.add_box(
                    image_id=image_id,
                    xtl=int(record["x_from"]),
                    ybr=int(record["y_from"]) + int(record["height"]),
                    xbr=int(record["x_from"]) + int(record["width"]),
                    ytl=int(record["y_from"]),
                    label=record["sign_class"]
                )

    ds.dump(args.output_file)


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    main(args)
