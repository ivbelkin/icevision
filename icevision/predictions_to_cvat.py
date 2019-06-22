import argparse
import torch
import numpy as np

from icevision.seq_bbox_matching import bbox_nms, sbm_filter
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
        "--labels-file",
        type=str,
        help="file with space separated labels"
    )
    parser.add_argument(
        "--conf-threshold",
        type=float,
        default=0.0
    )
    parser.add_argument(
        "--nms-threshold",
        type=float,
        default=0.3
    )
    parser.add_argument(
        "--add-filenames",
        action="store_true"
    )
    return parser


def extract_frames(predictions):
    frames = []
    for prediction in predictions:
        result = prediction["result"]
        bboxes = result.bbox.numpy()
        lls = result.get_field("log_likelihood").numpy()
        frame = (bboxes, lls)
        frames.append(frame)
    return frames


def extract_filenames(predictions):
    filenames = []
    for prediction in predictions:
        filename = prediction["filename"]
        filenames.append(filename)
    return filenames


def confidence_filter(frames, threshold):
    new_frames = []
    for bboxes, lls in frames:
        scores = np.exp(np.max(lls, axis=1))
        keep = scores > threshold
        bboxes = bboxes[keep]
        lls = lls[keep]
        new_frames.append((bboxes, lls))
    return new_frames


def nms_filter(frames, threshold):
    new_frames = []
    for bboxes, lls in frames:
        scores = np.max(lls, axis=1)
        keep, supressed = bbox_nms(bboxes, scores, threshold)
        for i, j in enumerate(keep):
            for k in supressed[i]:
                lls[j] += lls[k]
        bboxes = bboxes[keep]
        lls = lls[keep]
        new_frames.append((bboxes, lls))
    return new_frames


def bg_filter(frames):
    new_frames = []
    for bboxes, lls in frames:
        keep = []
        for i, (bbox, ll) in enumerate(zip(bboxes, lls)):
            label = np.argmax(ll)
            if label > 0:
                keep.append(i)
        bboxes = bboxes[keep]
        lls = lls[keep]
        new_frames.append((bboxes, lls))
    return new_frames


def area_filter(frames, skip_less_then):
    new_frames = []
    for bboxes, lls in frames:
        areas = (bboxes[:, 2] - bboxes[:, 0]) * (bboxes[:, 3] - bboxes[:, 1])
        keep = areas >= skip_less_then
        bboxes = bboxes[keep]
        lls = lls[keep]
        new_frames.append((bboxes, lls))
    return new_frames


def adjust_bbox(bbox, label):
    label = label.replace("_", ".")
    if label == "5.19" or label.startswith("5.19."):
        bbox = bbox.reshape(-1, 2)
        center = bbox.mean(axis=0)
        bbox = center + (bbox - center) * (1 - 9 / 66)
        bbox = bbox.reshape(-1)
    return bbox


def main(args):
    predictions = torch.load(args.predictions)
    with open(args.labels_file, "r") as f:
        labels = f.read().split(" ")
    ds = CvatDataset()

    frames = extract_frames(predictions)
    filenames = extract_filenames(predictions)

    frames = bg_filter(frames)
    frames = nms_filter(frames, args.nms_threshold)
    frames = sbm_filter(frames, min_tubelet_length=15, window=1, K=12)
    frames = bg_filter(frames)
    frames = area_filter(frames, 1000)
    frames = confidence_filter(frames, args.conf_threshold)

    for image_id, ((bboxes, lls), filename) in enumerate(zip(frames, filenames)):
        ds.add_image(image_id)
        if args.add_filenames:
            ds.set_name(image_id, filename)
        for bbox, ll in zip(bboxes, lls):
            amax = np.argmax(ll)
            assert amax > 0
            if amax == len(labels) + 1:
                continue
            label = labels[amax - 1]
#<<<<<<< HEAD
            #bbox = adjust_bbox(bbox, label)
            #conf = np.exp(lls[amax])
#=======
            # bbox = adjust_bbox(bbox, label)
#>>>>>>> master
            ds.add_box(
                image_id, xtl=bbox[0], ytl=bbox[1], xbr=bbox[2], ybr=bbox[3], label=label
            )

    ds.dump(args.output_file)


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    main(args)
