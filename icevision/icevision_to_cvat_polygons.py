import argparse
import os
import pandas as pd
from math import sin, cos, pi

from tqdm import tqdm

from cvat import CvatDataset

def build_parser():
    parser = argparse.ArgumentParser("Convert icevision annotations to cvat-compatible xml")
    parser.add_argument(
        "--annot-dir",
        type=str,
        help="directory with icevision *.tsv files"
    )
    parser.add_argument(
        "--output-file",
        help="file with *.xml cvat annotations"
    )
    return parser

rhombus_signs = {'2.1'}
triangle_signs = {'2.4'}
round_signs = {'3.1','3.24','3.27','4.1','4.2.1','4.2.2','4.2.3','4.1.1','4.1.2','4.1.3','4.1.4','4.1.5','4.1.6'}
rectangle_signs = {'1.17', '5.15.2', '8.14', '8.22.3', '8.2.6', '1.34.2', '8.2.1', '8.2.2', '5.5', '8.5.4', '5.31', '3.4', '6.9.2', '5.19.2', '8.21.1', '5.7.1', '5.23.1', '2.2', '8.4.1', '1.12.1', '8', '6.6', '5.19.1', '8.2.4', '5.24.1', '1.31', '8.2.5', '5.6', '5.7.2', '1.34.1', '3.10', '1.20.2', '8.22.1', 'NA', '5.15.1', '6.9.1', '8.17', '8.13', '6.16', '5.15.5', '3.2', '1.25', '5.4', '6.13', '6.7', '6.10.1', '5.15.3', '3.13', '1.15', '5.15.4', '7.5', '4.3', '3.32', '5.3', '5.14', '5.16', '8.1.1', '6.10.2', '1.8', '5.20', '7.3', '2.1', '6.4'}

def label_image(label):
    if label in rhombus_signs:
        return "rhombus"
    elif label in triangle_signs:
        return "triangle"
    elif label in round_signs:
        return "round"
    else: return "box"

def polygon_round(xtl, ytl, xbr, ybr):
    points = list()
    x_c, y_c = (xbr+xtl)//2, (ytl+ybr)//2
    radius = (xbr-xtl)//2
    for i in range(30):
        x = x_c + radius * cos(i*2*pi/30)
        y = y_c + radius * sin(i*2*pi/30)
        points.append([int(x), int(y)])
    return points

def polygon_rhombus(xtl, ytl, xbr, ybr):
    points = list()
    points.append([(xbr+xtl)//2, ytl])
    points.append([xbr, (ytl+ybr)//2])
    points.append([(xbr+xtl)//2, ybr])
    points.append([xtl, (ytl+ybr)//2])
    return points

def polygon_triangle(xtl, ytl, xbr, ybr):
    points = list()
    points.append([xbr, ytl])
    points.append([(xbr+xtl)//2, ybr])
    points.append([xtl, ytl])
    return points

def main(args):
    filenames = sorted(os.listdir(args.annot_dir))

    ds = CvatDataset()
    for filename in tqdm(filenames):
        image_id = int(filename.split(".")[0])
        path = os.path.join(args.annot_dir, filename)
        df = pd.read_csv(path, sep="\t", na_values=[], keep_default_na=False, dtype={
            "class": str, "xtl": int, "ytl": int, "xbr": int, "ybr": int,
            "temporary": bool, "occluded": bool, "data": str
        })

        ds.add_image(image_id)
        for record in df.to_dict("records"):
            label = label_image(record["class"])
            if label == "round":
                ds.add_polygon(
                    image_id=image_id,
                    points=polygon_round(record["xtl"], record["ytl"], record["xbr"], record["ybr"]),
                    label=record["class"],
                    occluded=int(record["occluded"]))

            elif label == "rhombus":
                ds.add_polygon(
                    image_id=image_id,
                    points=polygon_rhombus(record["xtl"], record["ytl"], record["xbr"], record["ybr"]),
                    label=record["class"],
                    occluded=int(record["occluded"]))

            elif label == "triangle":
                ds.add_polygon(
                    image_id=image_id,
                    points=polygon_triangle(record["xtl"], record["ytl"], record["xbr"], record["ybr"]),
                    label=record["class"],
                    occluded=int(record["occluded"]))

            else :
                ds.add_box(
                    image_id=image_id,
                    xtl=record["xtl"],
                    ytl=record["ytl"],
                    xbr=record["xbr"],
                    ybr=record["ybr"],
                    label=record["class"],
                    occluded=int(record["occluded"])
                )

    ds.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
