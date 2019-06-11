# Seq-NMS for Video Object Detection
#   https://arxiv.org/pdf/1602.08465.pdf
#
# Improving Video Object Detection by Seq-Bbox Matching
#   http://www.insticc.org/Primoris/Resources/PaperPdf.ashx?idPaper=72600

import numpy as np
import bisect

from tqdm import tqdm

np.warnings.filterwarnings("ignore")


def sbm_filter(frames, min_tubelet_length=15, window=3, K=12):
    tubelets = find_tubelets(frames)
    frames = frame_level_bbox_rescoring(frames, tubelets)
    tubelets, frames = tubelet_level_box_linking(frames, tubelets, K)
    frames = smooth_tubulets(frames, tubelets, window)
    frames, tubelets = remove_small_tubelets(frames, tubelets, min_tubelet_length)
    return frames


def smooth_tubulets(frames, tubulets, window):
    assert window % 2
    half = (window - 1) // 2
    for tubulet in tubulets:
        for i in range(half, len(tubulet) - half):
            frame_idx, bbox_idx = tubulet[i]
            bbox = 0
            for j in range(-half, half + 1):
                frame_i, bbox_i = tubulet[i + j]
                bbox += frames[frame_i][0][bbox_i]
            frames[frame_idx][0][bbox_idx] = bbox / window
    return frames


def remove_small_tubelets(frames, tubelets, min_tubelet_length):
    new_tubelets = []
    for tubelet in tubelets:
        if len(tubelet) >= min_tubelet_length:
            new_tubelets.append(tubelet)
        else:
            for frame_idx, bbox_idx in tubelet:
                frames[frame_idx][1][bbox_idx] = -np.inf
    new_frames = []
    for bboxes, lls in frames:
        keep = (lls > -np.inf).any(axis=1)
        bboxes = bboxes[keep]
        lls = lls[keep]
        new_frames.append((bboxes, lls))
    return new_frames, new_tubelets


def find_tubelets(frames):
    tubelets = []
    # each bbox in first frame is start of new tubelet
    current_tubelets = [[(0, bbox_idx)] for bbox_idx in range(len(frames[0][0]))]
    print("Find tubelets")
    for current_frame in tqdm(range(1, len(frames))):
        bboxes_1, lls_1 = frames[current_frame - 1]
        bboxes_2, lls_2 = frames[current_frame]
        pairs = seq_bbox_matching(bboxes_1, lls_1, bboxes_2, lls_2)

        # each bbox, which will not extend any tubelet, starts the new one
        unused_bboxs_idxs = set(range(len(bboxes_2))).difference([pair[1] for pair in pairs])
        for bbox_idx in unused_bboxs_idxs:
            current_tubelets.append([(current_frame, bbox_idx)])

        # extend tubelets
        for tubelet in current_tubelets:
            frame_idx, bbox_idx = tubelet[-1]
            index = bisect.bisect_left(pairs, (bbox_idx, -1))
            if index < len(pairs) and pairs[index][0] == bbox_idx:
                tubelet.append((current_frame, pairs[index][1]))
                pairs.pop(index)

        # not extended tubelets are completed
        current_tubelets_new = []
        for tubelet in current_tubelets:
            frame_idx, bbox_idx = tubelet[-1]
            if frame_idx == current_frame:
                current_tubelets_new.append(tubelet)
            else:
                tubelets.append(tubelet)
        current_tubelets = current_tubelets_new

    return tubelets


def frame_level_bbox_rescoring(frames, tubelets):
    scores = find_tubelet_scores(frames, tubelets)
    print("Frame level bbox rescoring")
    for tubelet, score in tqdm(zip(tubelets, scores)):
        for frame_idx, bbox_idx in tubelet:
            frames[frame_idx][1][bbox_idx] = score
    return frames


def find_tubelet_scores(frames, tubelets):
    tubelet_scores = []
    print("Tubelet scoring")
    for tubelet in tqdm(tubelets):
        score = 0
        for frame_idx, bbox_idx in tubelet:
            score += frames[frame_idx][1][bbox_idx]
        tubelet_scores.append(score / len(tubelet))
    return tubelet_scores


def tubelet_level_box_linking(frames, tubelets, K=12):
    tubelets.sort(key=lambda x: (x[0][0], x[-1][0]))
    used = [False] * len(tubelets)
    tubelet_starts = [tubelet[0][0] for tubelet in tubelets]
    new_tubelets = []
    print("Tubelet level box linking")
    for i in tqdm(range(len(tubelets))):
        if used[i]:
            continue
        tubelet = tubelets[i]
        used[i] = True
        while True:
            end_frame_idx, end_bbox_idx = tubelet[-1]
            end_bbox = frames[end_frame_idx][0][end_bbox_idx]
            end_lls = frames[end_frame_idx][1][end_bbox_idx]
            idx = bisect.bisect_left(tubelet_starts, end_frame_idx + 2)
            match_scores = []
            while idx < len(tubelets) and tubelets[idx][0][0] - end_frame_idx <= K + 1:
                if used[idx]:
                    idx += 1
                    continue
                start_frame_idx, start_bbox_idx = tubelets[idx][0]
                start_bbox = frames[start_frame_idx][0][start_bbox_idx]
                start_lls = frames[start_frame_idx][1][start_bbox_idx]
                match_score = bbox_distance(
                    end_bbox[None, :], end_lls[None, :], start_bbox[None, :], start_lls[None, :])[0, 0]
                if match_score < 4:
                    match_scores.append((match_score, idx))
                    break  # select closest match
                idx += 1
            if len(match_scores) > 0:
                best_match = min(match_scores, key=lambda x: x[0])[1]
                used[best_match] = True
                tubelet, frames = join_tubelets(tubelet, tubelets[best_match], frames)
            else:
                new_tubelets.append(tubelet)
                break

    return new_tubelets, frames


def join_tubelets(tubelet_1, tubelet_2, frames):
    size_1 = len(tubelet_1)
    frame_idx_1, bbox_idx_1 = tubelet_1[-1]
    bbox_1 = frames[frame_idx_1][0][bbox_idx_1]
    lls_1 = frames[frame_idx_1][1][bbox_idx_1]

    size_2 = len(tubelet_2)
    frame_idx_2, bbox_idx_2 = tubelet_2[0]
    bbox_2 = frames[frame_idx_2][0][bbox_idx_2]
    lls_2 = frames[frame_idx_2][1][bbox_idx_2]

    mid_lls = (size_1 * lls_1 + size_2 * lls_2) / (size_1 + size_2)
    mid_tubelet = []
    # do bilinear interpolation of bboxes
    for mid_frame_idx in range(frame_idx_1 + 1, frame_idx_2):
        alpha = (mid_frame_idx - frame_idx_1) / (frame_idx_2 - frame_idx_1)
        mid_bbox = bbox_1 * (1 - alpha) + bbox_2 * alpha
        frame_bboxes, frame_lls = frames[mid_frame_idx]
        mid_bbox_idx = len(frame_bboxes)
        frame_bboxes = np.concatenate((frame_bboxes, mid_bbox[None, :]), axis=0)
        frame_lls = np.concatenate((frame_lls, mid_lls[None, :]), axis=0)
        mid_tubelet.append((mid_frame_idx, mid_bbox_idx))
        frames[mid_frame_idx] = frame_bboxes, frame_lls
    return tubelet_1 + mid_tubelet + tubelet_2, frames


def seq_bbox_matching(bboxes_1, scores_1, bboxes_2, scores_2):
    pairs = []
    if len(bboxes_1) > 0 and len(bboxes_2) > 0:
        distance = bbox_distance(bboxes_1, scores_1, bboxes_2, scores_2)
        amin = argmin_ndim(distance)
        while distance[amin] < np.inf:
            pairs.append(amin)
            distance[amin[0], :] = np.inf
            distance[:, amin[1]] = np.inf
            amin = argmin_ndim(distance)
    return sorted(pairs)


def argmin_ndim(a):
    return np.unravel_index(np.argmin(a, axis=None), a.shape)


def bbox_distance(bboxes_1, scores_1, bboxes_2, scores_2):
    iou = bbox_iou(bboxes_1, bboxes_2)
    sem_sim = semantic_similarity(scores_1, scores_2)
    return 1 / (iou * sem_sim)


def semantic_similarity(scores_1, scores_2):
    norm_squared_1 = (scores_1 * scores_1).sum(axis=1)
    norm_squared_2 = (scores_2 * scores_2).sum(axis=1)
    cos_sim = scores_1.dot(scores_2.T) / np.sqrt(np.outer(norm_squared_1, norm_squared_2))
    return cos_sim


# Reference:
#   https://github.com/kuangliu/torchcv/blob/master/torchcv/utils/box.py
def bbox_iou(bboxes_1, bboxes_2):
    lt = np.maximum(bboxes_1[:, None, :2], bboxes_2[:, :2])  # [N, M, 2]
    rb = np.minimum(bboxes_1[:, None, 2:], bboxes_2[:, 2:])  # [N, M, 2]

    wh = (rb - lt).clip(min=0)  # [N, M, 2]
    inter = wh[:, :, 0] * wh[:, :, 1]  # [N, M]

    area_1 = (bboxes_1[:, 2] - bboxes_1[:, 0]) * (bboxes_1[:, 3] - bboxes_1[:, 1])  # [N,]
    area_2 = (bboxes_2[:, 2] - bboxes_2[:, 0]) * (bboxes_2[:, 3] - bboxes_2[:, 1])  # [M,]
    iou = inter / (area_1[:, None] + area_2 - inter)
    return iou


# Reference:
#   https://github.com/rbgirshick/py-faster-rcnn/blob/master/lib/nms/py_cpu_nms.py
def bbox_nms(bboxes, scores, thresh):
    x1 = bboxes[:, 0]
    y1 = bboxes[:, 1]
    x2 = bboxes[:, 2]
    y2 = bboxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    supressed = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= thresh)[0]
        new_order = order[inds + 1]
        supressed.append(set(order) - set(new_order) - set([i]))
        order = new_order

    return keep, supressed
