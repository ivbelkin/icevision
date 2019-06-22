import argparse
import os
import pandas as pd

from tqdm import tqdm

from icevision.cvat import CvatDataset


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
    parser.add_argument(
        "--labels",
        type=str,
        help="file with space-separated labels"
    )
    return parser


def main(args):
    filenames = sorted(os.listdir(args.annot_dir))
    if os.path.exists(args.labels):
        with open(args.labels, "r") as f:
            labels = f.read().strip().split(" ")
    else:
        labels = []

    ds = CvatDataset()
    for filename in tqdm(filenames):
        image_id = int(filename.split(".")[0])
        path = os.path.join(args.annot_dir, filename)
        df = pd.read_csv(path, sep="\t", na_values=[], keep_default_na=False, dtype={
            "class": str, "xtl": int, "ytl": int, "xbr": int, "ybr": int,
            "temporary": bool, "occluded": bool, "data": str
        })

        labels.extend(df["class"])

        ds.add_image(image_id)
        ds.set_name(image_id, filename.replace(".tsv", ".jpg"))
        for record in df.to_dict("records"):
            ds.add_box(
                image_id=image_id,
                xtl=record["xtl"],
                ytl=record["ytl"],
                xbr=record["xbr"],
                ybr=record["ybr"],
                label=record["class"],
                occluded=int(record["occluded"])
            )

    labels = sorted(list(set(labels)))
    with open(args.labels, "w") as f:
        f.write(" ".join(labels))

    ds.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
