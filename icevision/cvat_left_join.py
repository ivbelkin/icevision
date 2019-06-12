import argparse

from icevision.cvat import CvatDataset


def build_parser():
    parser = argparse.ArgumentParser("Perform left join of two cvat-compatible files")
    parser.add_argument(
        "--left",
        required=True,
        type=str
    )
    parser.add_argument(
        "--right",
        required=True,
        type=str
    )
    parser.add_argument(
        "--output-file",
        required=True,
        type=str
    )
    parser.add_argument(
        "--on",
        type=str,
        choices=["frame", "name"],
        default="name"
    )
    return parser


def main(args):
    left = CvatDataset()
    left.load(args.left)

    right = CvatDataset()
    right.load(args.right)

    left.update(right, on=args.on)

    left.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
