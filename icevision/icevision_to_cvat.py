import argparse
import os
import pandas as pd
import xml.etree.ElementTree as xml
import datetime

from tqdm import tqdm


WIDTH = 2448
HEIGHT = 2048


def build_parser():
    parser = argparse.ArgumentParser("Convert icevision annotations to cvat-compatible xml")
    parser.add_argument(
        "--input-dir",
        type=str,
        help="directory with icetision *.tsv files"
    )
    parser.add_argument(
        "--output-file",
        help="file with *.xml cvat annotations"
    )
    return parser


def add_boxes(image, df):
    for record in df.to_dict("records"):
        xml.SubElement(
            image,
            "box",
            {k: str(record[k]) for k in ["xtl", "ytl", "xbr", "ybr"]},
            label=str(record["class"]),
            occluded=str(int(record["occluded"]))
        )


def add_task(meta, labels, sz):
    task = xml.SubElement(meta, "task")

    id = xml.SubElement(task, "id")
    id.text = "1.1"

    name = xml.SubElement(task, "name")
    name.text = "icevision"

    size = xml.SubElement(task, "size")
    size.text = str(sz)

    mode = xml.SubElement(task, "mode")
    mode.text = "annotation"

    overlap = xml.SubElement(task, "overlap")
    overlap.text = "0"

    xml.SubElement(task, "bugtracker")

    flipped = xml.SubElement(task, "flipped")
    flipped.text = "False"

    created = xml.SubElement(task, "created")
    created.text = str(datetime.datetime.now())

    updated = xml.SubElement(task, "created")
    updated.text = str(datetime.datetime.now())

    start_frame = xml.SubElement(task, "start_frame")
    start_frame.text = "0"

    stop_frame = xml.SubElement(task, "stop_frame")
    stop_frame.text = str(sz)

    xml.SubElement(task, "frame_filter")

    add_labels(task, labels)

    add_segments(task, sz)

    add_owner(task)


def add_labels(task, lbls):
    labels = xml.SubElement(task, "labels")
    for lbl in lbls:
        label = xml.SubElement(labels, "label")

        name = xml.SubElement(label, "name")
        name.text = str(lbl)

        xml.SubElement(label, "attributes")


def add_segments(task, sz):
    segments = xml.SubElement(task, "segments")

    segment = xml.SubElement(segments, "segment")

    id = xml.SubElement(segment, "id")
    id.text = "1"

    start = xml.SubElement(segment, "start")
    start.text = "0"

    stop = xml.SubElement(segment, "stop")
    stop.text = str(sz)

    url = xml.SubElement(segment, "url")
    url.text = "http://localhost:8080/?id=1"


def add_owner(task):
    owner = xml.SubElement(task, "owner")

    username = xml.SubElement(owner, "username")
    username.text = "django"

    xml.SubElement(owner, "email")


def main(args):
    filenames = os.listdir(args.input_dir)

    root = xml.Element("annotations")

    version = xml.SubElement(root, "version")
    version.text = "1.1"

    meta = xml.SubElement(root, "meta")

    dumped = xml.SubElement(meta, "dumped")
    dumped.text = str(datetime.datetime.now())

    labels = set()
    for filename in tqdm(filenames):
        image_id = int(filename.split(".")[0])
        path = os.path.join(args.input_dir, filename)
        df = pd.read_csv(path, sep="\t").fillna("NA")
        labels.update(df["class"])

        image = xml.SubElement(
            root,
            "image",
            id=str(image_id),
            name=filename.replace(".tsv", ".jpg"),
            width=str(WIDTH),
            height=str(HEIGHT)
        )
        add_boxes(image, df)

    labels = set(labels)

    add_task(meta, labels, sz=len(filenames))

    tree = xml.ElementTree(root)
    with open(args.output_file, "w") as f:
        tree.write(f, encoding="unicode")


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
