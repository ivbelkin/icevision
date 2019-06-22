import argparse
import pandas as pd


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", type=str, required=True)
    parser.add_argument(nargs="+", dest="files")
    return parser


def main(args):
    dfs = []
    for path in args.files:
        print("Loading", path)
        df = pd.read_csv(path, sep="\t", dtype=str)
        print("Shape", df.shape)
        dfs.append(df)
        print(df.head())
        print("...")
        print()

    df = pd.concat(dfs, ignore_index=True)
    print("Saving to", args.output_file)
    print("Shape", df.shape)
    print(df.head())
    df.to_csv(args.output_file, sep="\t", index=False)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
