import argparse

parser = argparse.ArgumentParser("Add conf property to labels.")
parser.add_argument(
        "--in_name",
        type=str,
        help="Path to *.txt with labels"
    )
parser.add_argument(
    "--out_name",
    type=str,
    help="Path for output file"
)


args = parser.parse_args()

in_name = args.in_name
out_name = args.out_name

#in_name = "/home/serg/CV/Datasets/IceVision/icevision/icevision/rtsd_labels_new.txt"
#out_name = "/home/serg/CV/Datasets/IceVision/icevision/icevision/rtsd_labels_new_with_conf.txt"

with open(in_name) as in_f:
    s = in_f.read().split(' ')
    for i in range(len(s)):
        s[i] = s[i] + " @text=conf:-1"
    with open(out_name, 'w') as out_f:
        out_f.write(' '.join(s))