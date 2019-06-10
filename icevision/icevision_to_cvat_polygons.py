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

def label_image(label):
    if label == '2.1':
        return "rhombus"
    elif label == '2.4':
        return "triangle"
    elif ((label=='3.1')|(label=='3.24')|(label=='3.27')|(label=='4.1')|(label=='4.2.1')|(label=='4.2.2')|(label=='4.2.3')|(label=='4.1.1')|(label=='4.1.2')|(label=='4.1.3')|(label=='4.1.4')|(label=='4.1.5')|(label=='4.1.6')):
        return "round"
    else:
        return "box"

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
