import argparse
import os
import pandas as pd
from math import sin, cos, pi

from tqdm import tqdm

from cvat import CvatDataset

def build_parser():
    parser = argparse.ArgumentParser("Create .tsv submission file from cvat .xml annotations")
    parser.add_argument(
        "--annot-xml",
        type=str,
        help="cvat annotations"
    )
    parser.add_argument(
        "--output-file",
        help="file with *.xml cvat annotations"
    )
    return parser

rhombus_signs = {'2.1', '2.2'}
triangle_signs = {'2.4'}
round_signs = {'3.1', '3.13', '3.2', '3.24','3.27', '3.32', '3.10','4.1','4.2.1','4.2.2','4.2.3','4.1.1','4.1.2','4.1.3','4.1.4','4.1.5','4.1.6', '4.3'}
reverse_triangle_signs = {'1.17', '1.12.1', '1.31', '1.20.2', '1.25', '1.15', '1.8'}
rectangle_signs = {'8.14', '8.13', '5.14', '8.1.1', '5.6', '5.20', '3.4', '6.4', '5.7.1', '6.16', '8.2.1', '6.6', '1.34.2', '5.5', '5.16', '6.10.1', '8.2.2', '5.19.2', 'NA', '5.7.2', '5.15.5', '8.4.1', '5.3', '8.21.1', '5.31', '8.5.4', '8.2.6', '7.5', '1.34.1', '8.17', '8', '7.3', '5.24.1', '8.22.3', '5.15.2', '8.2.4', '5.23.1', '6.10.2', '5.4', '8.2.5', '6.7', '8.22.1', '5.15.1', '5.15.3', '6.9.2', '5.15.4', '6.13', '5.19.1', '6.9.1'}

def label_image(label):
    if label in rhombus_signs:
        return "rhombus"
    elif label in triangle_signs:
        return "triangle"
    elif label in round_signs:
        return "round"
    elif label in reverse_triangle_signs:
        return "reverse_triangle"
    else: return "box"

def polygon_round(xtl, ytl, xbr, ybr):
    points = list()
    x_c, y_c = (xbr+xtl)//2, (ytl+ybr)//2
    a = (xbr-xtl)//2
    b = (ytl-ybr)//2
    for i in range(30):
        x = x_c + a * cos(i*2*pi/30)
        y = y_c + b * sin(i*2*pi/30)
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

def polygon_reverse_triangle(xtl, ytl, xbr, ybr):
    points = list()
    points.append([xtl, ybr])
    points.append([(xbr+xtl)//2, ytl])
    points.append([xbr, ybr])
    return points


def polygons(df_file):
    df = pd.DataFrame(columns=["frame", "occluded", "xtl", "ytl", "xbr", "ybr", "class"])
    ds = CvatDataset()
    frames = df_file["frame"]
    frames = list(set(frames))
    frames.sort()
    for frame in frames:
        df = df_file.loc[df_file.frame == frame]
        ds.add_image(frame)
        for record in df.to_dict("records"):
            label = list(map(label_image, [record["class"]]))[0]
            if label == "round":
                ds.add_polygon(
                    image_id=frame,
                    points=polygon_round(record["xtl"], record["ytl"], record["xbr"], record["ybr"]),
                    label=record["class"],
                    occluded=int(record["occluded"]))

            elif label == "rhombus":
                ds.add_polygon(
                    image_id=frame,
                    points=polygon_rhombus(record["xtl"], record["ytl"], record["xbr"], record["ybr"]),
                    label=record["class"],
                    occluded=int(record["occluded"]))

            elif label == "triangle":
                ds.add_polygon(
                    image_id=frame,
                    points=polygon_triangle(record["xtl"], record["ytl"], record["xbr"], record["ybr"]),
                    label=record["class"],
                    occluded=int(record["occluded"]))

            elif label == "reverse_triangle":
                ds.add_polygon(
                    image_id=frame,
                    points=polygon_reverse_triangle(record["xtl"], record["ytl"], record["xbr"], record["ybr"]),
                    label=record["class"],
                    occluded=int(record["occluded"]))
            else :
                ds.add_box(
                    image_id=frame,
                    xtl=record["xtl"],
                    ytl=record["ytl"],
                    xbr=record["xbr"],
                    ybr=record["ybr"],
                    label=record["class"],
                    occluded=int(record["occluded"])
                )
    ds.dump(args.output_file)


def main(args):
    ds = CvatDataset()
    ds.load(args.annot_xml)

    result = []
    for image_id in tqdm(ds.get_image_ids()):
        filename = "{:0>6}".format(image_id)
        boxes = ds.get_boxes(image_id)
        for box in boxes:
            label = box["label"].replace("_", ".")
            occluded = box["occluded"]
            record = {k: int(box[k]) for k in ["xtl", "ytl", "xbr", "ybr"]}
            record["frame"] = int(os.path.join("", filename))
            record["class"] = label
            record["occluded"] = occluded

            result.append(record)

    df = pd.DataFrame(result, columns=["frame", "occluded", "xtl", "ytl", "xbr", "ybr", "class"])
    polygons(df)

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
