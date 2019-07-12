import argparse
import os

from tqdm import tqdm

from cvat import CvatDataset

def build_parser():
    parser = argparse.ArgumentParser("Add polygons according to sign class")
    parser.add_argument(
        "--input-file",
        type=str
    )
    parser.add_argument(
        "--output-folder",
        type=str
    )
    parser.add_argument(
        "--conf",
        action="store_true"
    )
    return parser

def polygon_to_box(points):
    return {
        "xtl": min(point[0] for point in points),
        "ytl": min(point[1] for point in points),
        "xbr": max(point[0] for point in points),
        "ybr": max(point[1] for point in points)
    }

def write_file(file, dict):
    if args.conf == True:
        file.write(str(dict["label"]) + " " + \
                   str(dict["conf"])  + " " + \
                   str(int(dict["xtl"]))  + " " + \
                   str(int(dict["ytl"]))  + " " + \
                   str(int(dict["xbr"]))  + " " + \
                   str(int(dict["ybr"])) + '\n')
    else:
        file.write(str(dict["label"]) + " " + \
                   str(int(dict["xtl"]))  + " " + \
                   str(int(dict["ytl"]))  + " " + \
                   str(int(dict["xbr"]))  + " " + \
                   str(int(dict["ybr"])) + '\n')

def main(args):
    ds = CvatDataset()
    ds.load(args.input_file)

    for file in os.listdir(args.output_folder):
        file_path = os.path.join(args.output_folder, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    for image_id in tqdm(ds.get_image_ids()):
        f = open(args.output_folder+"/" + str(image_id) + '.txt', 'w')
        polygons = ds.get_polygons(image_id)
        for polygon in polygons:
            box = polygon_to_box(polygon["points"])
            box["label"] = polygon["label"]
            write_file(f, box)
        boxes = ds.get_boxes(image_id)
        for box in boxes:
            write_file(f, box)
        f.close()

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
