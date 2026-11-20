"""Trim scanner bars and facing-page slivers from an exported logbook page.

The source PDFs are scans of a sheet that often includes a black scanner
edge and a strip of the neighboring page, turned the other way. This keeps
the upright log sheet, with a white margin so a crop box can include the
whole entry. It cannot restore handwriting the scanner never captured.
"""

from __future__ import annotations

import numpy as np

PAD = 40


def _clusters(frac, thr, gap, min_len, max_len=None, below=False):
    idx = np.where(frac < thr)[0] if below else np.where(frac > thr)[0]
    if not len(idx):
        return []
    breaks = np.where(np.diff(idx) > gap)[0]
    starts = [int(idx[0])] + [int(idx[i + 1]) for i in breaks]
    ends = [int(idx[i]) for i in breaks] + [int(idx[-1])]
    found = []
    for start, end in zip(starts, ends):
        length = end - start + 1
        if length < min_len:
            continue
        if max_len is not None and length > max_len:
            continue
        found.append((start, end))
    return found


def _expand_shoulder(frac, start, end, thr=0.12):
    while start > 0 and frac[start - 1] > thr:
        start -= 1
    while end + 1 < len(frac) and frac[end + 1] > thr:
        end += 1
    return start, end


def _margin_gap(ink, side):
    """White gap with a facing-page sliver outside it and the log inside it."""
    width = len(ink)
    smooth = np.convolve(ink, np.ones(21) / 21, mode="same")
    band = int(width * 0.22)
    if side == "left":
        runs = [run for run in _clusters(smooth[:band], 0.045, 6, 28, below=True) if run[0] > 36]
        runs = [
            run
            for run in runs
            if float(ink[: run[0]].mean()) > 0.045 and float(ink[run[1] : run[1] + 100].mean()) > 0.05
        ]
        runs = [run for run in runs if run[1] < band]
        if not runs:
            return None
        _start, end = runs[-1]
        return end - 12
    runs = _clusters(smooth, 0.045, 6, 28, below=True)
    runs = [(start, end) for start, end in runs if start > width - band and end < width - 36]
    runs = [
        run
        for run in runs
        if float(ink[run[1] + 1 :].mean()) > 0.045 and float(ink[run[0] - 100 : run[0]].mean()) > 0.05
    ]
    if not runs:
        return None
    start, _end = runs[0]
    return start + 12


def _content_box(gray):
    height, width = gray.shape
    row_dark = (gray < 50).mean(axis=1)
    col_dark = (gray < 50).mean(axis=0)
    col_ink = (gray < 155).mean(axis=0)
    top, bottom, left, right = 0, height, 0, width
    left_rule = False
    right_rule = False

    for start, end in _clusters(row_dark, 0.45, 4, 12):
        if float(row_dark[start : end + 1].max()) < 0.70:
            continue
        start, end = _expand_shoulder(row_dark, start, end)
        center = (start + end) / 2
        if center < height * 0.32:
            top = max(top, end + 1)
        elif center > height * 0.68:
            bottom = min(bottom, start)

    for start, end in _clusters(col_dark, 0.30, 4, 2, 40):
        center = (start + end) / 2
        if center > width * 0.75 and (width - end) >= 90:
            right = min(right, start)
            right_rule = True
        elif center < width * 0.25 and start >= 90:
            left = max(left, end + 1)
            left_rule = True

    # A low-ink gap is the facing-page strip. Skip it when a dark rule already
    # marks the paper edge, so a long line is not trimmed short of that edge.
    if not left_rule:
        cut = _margin_gap(col_ink, "left")
        if cut is not None and cut > left:
            left = cut
    if not right_rule:
        cut = _margin_gap(col_ink, "right")
        if cut is not None and cut < right:
            right = cut

    if right - left < width * 0.70 or bottom - top < height * 0.70:
        return 0, 0, width, height
    return left, top, right, bottom


def _whiten_bars(rgb):
    gray = rgb.min(axis=2)
    dark = gray < 55
    integral = np.pad(dark.astype(np.float32), ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    radius = 15
    height, width = dark.shape
    y0 = np.clip(np.arange(height) - radius, 0, height)
    y1 = np.clip(np.arange(height) + radius + 1, 0, height)
    x0 = np.clip(np.arange(width) - radius, 0, width)
    x1 = np.clip(np.arange(width) + radius + 1, 0, width)
    y0v = y0[:, None]
    y1v = y1[:, None]
    x0v = x0[None, :]
    x1v = x1[None, :]
    total = integral[y1v, x1v] - integral[y0v, x1v] - integral[y1v, x0v] + integral[y0v, x0v]
    area = (y1v - y0v) * (x1v - x0v)
    mask = (total / area) > 0.62
    for _ in range(6):
        grown = np.pad(mask, 1)
        neigh = grown[:-2, 1:-1] | grown[2:, 1:-1] | grown[1:-1, :-2] | grown[1:-1, 2:]
        mask = mask | (neigh & dark)
    out = rgb.copy()
    out[mask] = 255
    return out


def _drop_hairlines(rgb):
    out = rgb.copy()
    row = (out.min(axis=2) < 40).mean(axis=1)
    height = len(row)
    for index in list(range(min(28, height))) + list(range(max(0, height - 28), height)):
        if row[index] > 0.80:
            out[index] = 255
    return out


def tidy_rgb(rgb: np.ndarray) -> np.ndarray:
    """Return a copy of an upright page image with scanner junk trimmed off."""
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("tidy_rgb expects an RGB array")
    left, top, right, bottom = _content_box(rgb.min(axis=2))
    cleaned = _drop_hairlines(_whiten_bars(rgb[top:bottom, left:right]))
    height, width = cleaned.shape[:2]
    canvas = np.full((height + PAD * 2, width + PAD * 2, 3), 255, np.uint8)
    canvas[PAD : PAD + height, PAD : PAD + width] = cleaned
    return canvas
