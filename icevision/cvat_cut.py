import argparse

from icevision.cvat import CvatDataset


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-file",
        type=str,
        required=True
    )
    parser.add_argument(
        "--start-frame",
        type=int,
        default=0
    )
    parser.add_argument(
        "--end-frame",
        type=int,
        required=True
    )
    parser.add_argument(
        "--output-file",
        type=str,
        required=True
    )
    return parser


def main(args):
    ds = CvatDataset()
    ds.load(args.input_file)

    ds._images = {
        image_id: ds._images[image_id]
        for image_id in ds.get_image_ids() if args.start_frame <= image_id <= args.end_frame
    }

    ds.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
