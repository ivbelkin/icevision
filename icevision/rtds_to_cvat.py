import argparse

import pandas as pd

from cvat import CvatDataset


def build_parser():
    parser = argparse.ArgumentParser("Convert RTDS dataset to cvat format")
    parser.add_argument(
        "--annot",
        type=str,
        help="Directory with RTDS *.csv files"
    )
    parser.add_argument(
        "--output_file",
        type=str,
        help="Path to output file"
    )
    return parser

def main(args):
    data = pd.read_csv(args.annot)
    ds = CvatDataset()
    image_names = sorted(set(data["filename"]))
    for i in range(len(image_names)):
        ds.add_image()
    #for i in range(len())
    for i in range(len(data['filename'])):
        k = image_names.index(data['filename'][i])
        #data["x_from"] = int(data["x_from"])
        #data["y_from"] = int(data["y_from"])
        #data["width"] = int(data["width"])
        #data["height"] = int(data["height"])
        ds.add_box(
            image_id=k,
            xtl=int(data["x_from"][i]),
            ybr=int(data["y_from"][i]) + int(data["height"][i]),
            xbr=int(data["x_from"][i]) + int(data["width"][i]),
            ytl=int(data["y_from"][i]),
            label=data["sign_class"][i]
        )
    ds.dump(args.output_file)




if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    main(args)