import argparse
import torch

from tqdm import tqdm
from maskrcnn_benchmark.layers import nms as box_nms

from icevision.cvat import CvatDataset


def build_parser():
    parser = argparse.ArgumentParser("Convert maskrcnn predictions to cvat-compatible xml")
    parser.add_argument(
        "--predictions",
        type=str,
        help="maskrcnn predictions in *.pth dictionary"
    )
    parser.add_argument(
        "--output-file",
        help="file with *.xml cvat annotations"
    )
    parser.add_argument(
        "--conf-threshold",
        type=float,
        default=0.1
    )
    parser.add_argument(
        "--nms-threshold",
        type=float,
        default=0.3
    )
    return parser


def main(args):
    predictions = torch.load(args.predictions)
    ds = CvatDataset()

    for image_id, prediction in enumerate(tqdm(predictions)):
        ds.add_image(image_id)
        boxes = prediction.bbox
        scores = prediction.get_field("scores")
        if args.nms_threshold > 0:
            keep_ids = box_nms(boxes, scores, args.nms_threshold)
        else:
            keep_ids = range(len(prediction))

        for box_id in keep_ids:
            bbox = prediction.bbox[box_id].numpy()
            label = prediction.get_field("labels")[box_id].numpy()
            score = prediction.get_field("scores")[box_id].numpy()
            if score < args.conf_threshold:
                continue
            ds.add_box(
                image_id, xtl=bbox[0], ytl=bbox[1], xbr=bbox[2], ybr=bbox[3], label=label
            )

    ds.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
