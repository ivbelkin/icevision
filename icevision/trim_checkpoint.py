import argparse
import torch


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in-checkpoint",
        type=str,
        required=True
    )
    parser.add_argument(
        "--out-checkpoint",
        type=str,
        required=True
    )
    return parser


def main(args):
    checkpoint = torch.load(args.in_checkpoint)

    del checkpoint["optimizer"]
    del checkpoint["scheduler"]
    del checkpoint["iteration"]

    torch.save(checkpoint, args.out_checkpoint)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
