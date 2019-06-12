import argparse
from math import sin, cos, pi

from tqdm import tqdm

from icevision.cvat import CvatDataset

RHOMBUS_SIGNS = {"2.1", "2.2"}

TRIANGLE_SIGNS = {
    "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "1.10",
    "1.11.1", "1.11.2",
    "1.12.1", "1.12.2",
    "1.13", "1.14", "1.15", "1.16", "1.17", "1.18", "1.19",
    "1.20.1", "1.20.2", "1.20.3",
    "1.21", "1.22", "1.23", "1.24", "1.25", "1.26", "1.27", "1.28", "1.29", "1.30", "1.31", "1.32", "1.33",

    "2.3.1", "2.3.2", "2.3.3", "2.3.4", "2.3.5", "2.3.6", "2.3.7"
}

ROUND_SIGNS = {
    "2.6",

    "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14", "3.15", "3.16",
    "3.17.1", "3.17.2", "3.17.3",
    "3.18.1", "3.18.2",
    "3.19", "3.20", "3.21", "3.22", "3.23", "3.24", "3.25", "3.26", "3.27", "3.28", "3.29", "3.30", "3.31", "3.32", "3.33",

    "4.1.1", "4.1.2", "4.1.3", "4.1.4", "4.1.5", "4.1.6",
    "4.2.1", "4.2.2", "4.2.3",
    "4.3",
    "4.4.1", "4.4.2",
    "4.5.1", "4.5.2", "4.5.3", "4.5.4", "4.5.5", "4.5.6", "4.5.7",
    "4.6", "4.7"
}

REVERSE_TRIANGLE_SIGNS = {"2.4"}

OCTAGON_SIGNS = {"2.5"}


def build_parser():
    parser = argparse.ArgumentParser("Add polygons according to sign class")
    parser.add_argument(
        "--input-file",
        type=str
    )
    parser.add_argument(
        "--output-file",
        type=str
    )
    return parser


def label_image(label):
    if label in RHOMBUS_SIGNS:
        return "rhombus"
    elif label in TRIANGLE_SIGNS:
        return "triangle"
    elif label in ROUND_SIGNS:
        return "round"
    elif label in REVERSE_TRIANGLE_SIGNS:
        return "reverse_triangle"
    elif label in OCTAGON_SIGNS:
        return "octagon"
    else:
        return "box"


def polygon_round(xtl, ytl, xbr, ybr):
    points = list()
    x_c, y_c = (xbr + xtl) / 2, (ytl + ybr) / 2
    a = (xbr - xtl) / 2
    b = (ytl - ybr) / 2
    for i in range(30):
        x = x_c + a * cos(i * 2 * pi / 30)
        y = y_c + b * sin(i * 2 * pi / 30)
        points.append([x, y])
    return points


def polygon_rhombus(xtl, ytl, xbr, ybr):
    points = list()
    points.append([(xbr + xtl) / 2, ytl])
    points.append([xbr, (ytl + ybr) / 2])
    points.append([(xbr + xtl) / 2, ybr])
    points.append([xtl, (ytl + ybr) / 2])
    return points


def polygon_reverse_triangle(xtl, ytl, xbr, ybr):
    points = list()
    points.append([xbr, ytl])
    points.append([(xbr + xtl) / 2, ybr])
    points.append([xtl, ytl])
    return points


def polygon_triangle(xtl, ytl, xbr, ybr):
    points = list()
    points.append([xtl, ybr])
    points.append([(xbr + xtl) / 2, ytl])
    points.append([xbr, ybr])
    return points


def polygon_box(xtl, ytl, xbr, ybr):
    points = list()
    points.append([xtl, ytl])
    points.append([xtl, ybr])
    points.append([xbr, ybr])
    points.append([xbr, ytl])
    return points


def polygon_octagon(xtl, ytl, xbr, ybr):
    points = list()
    x_c, y_c = (xbr + xtl) / 2, (ytl + ybr) / 2
    a = (xbr - xtl) / 2
    b = (ytl - ybr) / 2
    for i in range(8):
        x = x_c + a * cos(i * 2 * pi / 8 + pi / 8)
        y = y_c + b * sin(i * 2 * pi / 8 + pi / 8)
        points.append([x, y])
    return points


def polygon_to_box(points):
    return {
        "xtl": min(point[0] for point in points),
        "ytl": min(point[1] for point in points),
        "xbr": max(point[0] for point in points),
        "ybr": max(point[1] for point in points)
    }


def main(args):
    ds = CvatDataset()
    ds.load(args.input_file)

    for image_id in tqdm(ds.get_image_ids()):
        polygons = ds.get_polygons(image_id)
        ds._images[image_id]["polygons"] = []
        for box in ds.get_boxes(image_id):
            label = label_image(box["label"].replace("_", "."))
            bbox = box["xtl"], box["ytl"], box["xbr"], box["ybr"]

            if label == "round":
                points = polygon_round(*bbox)
            elif label == "rhombus":
                points = polygon_rhombus(*bbox)
            elif label == "triangle":
                points = polygon_triangle(*bbox)
            elif label == "reverse_triangle":
                points = polygon_reverse_triangle(*bbox)
            elif label == "octagon":
                points = polygon_octagon(*bbox)
            else:
                points = polygon_box(*bbox)

            ds.add_polygon(
                image_id=image_id,
                points=points,
                label=box["label"],
                occluded=int(box["occluded"])
            )

        for polygon in polygons:
            box = polygon_to_box(polygon["points"])
            ds.add_box(
                image_id,
                **box,
                label=polygon["label"],
                occluded=polygon["occluded"]
            )
            ds.add_polygon(image_id, **polygon)

    ds.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
