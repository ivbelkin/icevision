import argparse
import os
import pandas as pd

from tqdm import tqdm

from icevision.cvat import CvatDataset


def build_parser():
    parser = argparse.ArgumentParser("Create .tsv submission file from cvat .xml annotations")
    parser.add_argument(
        "--annot-xml",
        type=str,
        help="cvat annotations"
    )
    parser.add_argument(
        "--image-folder",
        type=str,
        help="folder name which will be appended to filenames"
    )
    parser.add_argument(
        "--labels-file",
        type=str,
        help="file with space separated labels"
    )
    parser.add_argument(
        "--output-file",
        help="submission file"
    )
    parser.add_argument(
        "--image-ext",
        type=str,
        help="image extension which will be removed"
    )
    return parser


def main(args):
    ds = CvatDataset()
    ds.load(args.annot_xml)

    with open(args.labels_file, "r") as f:
        labels = tuple(f.read().split(" "))

    result = []
    for image_id in tqdm(ds.get_image_ids()):
        filename = os.path.basename(ds.get_name(image_id)).replace(args.image_ext, "")
        boxes = ds.get_boxes(image_id)
        for box in boxes:
            label = box["label"].replace("_", ".")
            cnt = 0
            for lbl in labels:
                if label == lbl or label.startswith(lbl + "."):
                    record = {k: int(box[k]) for k in ["xtl", "ytl", "xbr", "ybr"]}
                    record["frame"] = os.path.join(args.image_folder, filename)
                    record["class"] = lbl

                    result.append(record)
                    cnt += 1
            assert cnt <= 1

    df = pd.DataFrame(result, columns=["frame", "xtl", "ytl", "xbr", "ybr", "class"])
    df.to_csv(args.output_file, index=False, sep="\t")


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
