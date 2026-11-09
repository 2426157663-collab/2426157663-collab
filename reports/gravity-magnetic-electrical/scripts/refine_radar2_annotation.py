"""Detect and annotate the two manhole responses in the line-2 radargram."""

from pathlib import Path
import os
import shutil
import tempfile
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).parent
DOCX = BASE / "重磁电综合实验报告_真实图件标注版.docx"
SOURCE = BASE / "探地雷达实验/DAT_0002_反向_虚拟机输出.png"
ANNOTATED = BASE / "探地雷达实验/DAT_0002_反向_虚拟机输出_标注.png"

FONT = next(
    path
    for path in (
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    )
    if os.path.exists(path)
)

# Plot geometry in the 1800 x 820 source image.
L, T, W, H = 125, 70, 1600, 650
TRACE_COUNT = 8940
OUTPUT_SIZE = (1300, 585)


def ns_to_plot_y(ns):
    return ns / 200 * H


def plot_y_to_ns(y):
    return y / H * 200


def smooth(values, width):
    return np.convolve(values, np.ones(width) / width, mode="same")


def find_peaks(profile, count=2, minimum_distance=320):
    peaks = []
    for index in np.argsort(profile)[::-1]:
        if all(abs(index - peak) >= minimum_distance for peak in peaks):
            peaks.append(int(index))
        if len(peaks) == count:
            return sorted(peaks)
    raise RuntimeError(f"Only detected {len(peaks)} distinct anomaly responses")


def horizontal_bounds(profile, peak):
    """Estimate the response width from its locally elevated column energy."""
    radius = 120
    local = profile[max(0, peak - radius):min(W, peak + radius + 1)]
    background = float(np.median(local))
    threshold = background + 0.25 * (float(profile[peak]) - background)

    left = peak
    while left > max(0, peak - radius) and profile[left] > threshold:
        left -= 1
    right = peak
    while right < min(W - 1, peak + radius) and profile[right] > threshold:
        right += 1

    # A little padding keeps the outline outside the measured response.
    half_width = max(24, peak - left, right - peak) + 8
    return min(48, half_width)


def vertical_bounds(normalized_residual, peak, half_width):
    """Estimate top and tail bottom using energy local to this response."""
    center = normalized_residual[:, peak - half_width:peak + half_width + 1]
    left_side = normalized_residual[:, peak - 4 * half_width:peak - 2 * half_width]
    right_side = normalized_residual[:, peak + 2 * half_width:peak + 4 * half_width]
    sides = np.concatenate((left_side, right_side), axis=1)

    response = np.maximum(center.mean(axis=1) - sides.mean(axis=1), 0)
    response = smooth(response, 9)

    search_top = int(ns_to_plot_y(78))
    search_bottom = int(ns_to_plot_y(155))
    energy = response[search_top:search_bottom]
    cumulative = np.cumsum(energy)
    if cumulative[-1] <= 0:
        raise RuntimeError("Detected response has no measurable vertical energy")

    # The first 80% captures the visible ringing tail without circling noise.
    bottom = search_top + int(np.searchsorted(cumulative, cumulative[-1] * 0.80))
    top = int(ns_to_plot_y(80))
    return top, max(bottom, int(ns_to_plot_y(105)))


def detect_anomalies(image):
    gray = np.asarray(image.convert("L"), dtype=float)
    plot = gray[T:T + H, L:L + W]

    # Remove the horizontally continuous background reflector and normalize
    # each row so that local vertical responses dominate the detection score.
    residual = np.abs(plot - np.median(plot, axis=1, keepdims=True))
    row_scale = np.percentile(residual, 75, axis=1, keepdims=True) + 1.0
    normalized = np.clip(residual / row_scale, 0, 8)

    band_top = int(ns_to_plot_y(82))
    band_bottom = int(ns_to_plot_y(155))
    profile = smooth(normalized[band_top:band_bottom].mean(axis=0), 31)
    profile[:120] = 0
    profile[-120:] = 0

    peaks = find_peaks(profile)
    background = max(float(np.median(profile[120:-120])), 1e-6)
    anomalies = []
    for peak in peaks:
        half_width = horizontal_bounds(profile, peak)
        top, bottom = vertical_bounds(normalized, peak, half_width)
        confidence = float(profile[peak] / background)
        anomalies.append((peak, top, bottom, half_width, confidence))
    return anomalies


def font(size):
    return ImageFont.truetype(FONT, size)


def draw_label(draw, x, text):
    color = (190, 0, 0)
    box = draw.textbbox((x, 41), text, font=font(14), anchor="ms")
    draw.rounded_rectangle(
        (box[0] - 5, box[1] - 2, box[2] + 5, box[3] + 2),
        radius=4,
        fill="white",
        outline=color,
        width=1,
    )
    draw.text((x, 41), text, font=font(14), fill=color, anchor="ms")


def draw_annotation(image, anomalies):
    output = image.convert("RGB").resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(output)
    sx, sy = OUTPUT_SIZE[0] / image.width, OUTPUT_SIZE[1] / image.height

    draw.text(
        (650, 15),
        "探地雷达剖面  测线2（8940 道，数据已反向处理）",
        font=font(20),
        fill="black",
        anchor="mm",
    )
    draw.text((650, 575), "道号（沿测线位置）", font=font(15), fill="black", anchor="ms")

    for number, (peak, top, bottom, half_width, _) in enumerate(anomalies, start=1):
        center_x = (L + peak) * sx
        top_y = (T + top) * sy
        bottom_y = (T + bottom) * sy
        radius_x = half_width * sx
        color = (205, 0, 0)
        draw.ellipse(
            (center_x - radius_x, top_y, center_x + radius_x, bottom_y),
            outline=color,
            width=2,
        )
        # A compact pointer makes the label-to-response mapping unambiguous
        # without drawing a long line through the measured radar data.
        draw.polygon(
            ((center_x, top_y - 2), (center_x - 4, top_y - 9), (center_x + 4, top_y - 9)),
            fill=color,
        )
        draw_label(draw, center_x, f"井盖响应{number}")
    return output


def update_docx(image_path):
    work = Path(tempfile.mkdtemp(prefix="refine_radar2_"))
    rebuilt = work.with_suffix(".docx")
    try:
        with zipfile.ZipFile(DOCX) as archive:
            archive.extractall(work)
        shutil.copyfile(image_path, work / "word" / "media" / "image7.png")
        with zipfile.ZipFile(rebuilt, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in work.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(work))
        shutil.move(rebuilt, DOCX)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        rebuilt.unlink(missing_ok=True)


source_image = Image.open(SOURCE)
detected = detect_anomalies(source_image)
annotated = draw_annotation(source_image, detected)
annotated.save(ANNOTATED)
update_docx(ANNOTATED)

for number, (peak, top, bottom, half_width, confidence) in enumerate(detected, start=1):
    trace = round(peak / (W - 1) * (TRACE_COUNT - 1) + 1)
    print(
        f"response {number}: trace {trace}, "
        f"{plot_y_to_ns(top):.1f}-{plot_y_to_ns(bottom):.1f} ns, "
        f"half-width {half_width}px, confidence {confidence:.1f}x"
    )
print("updated", ANNOTATED.name, "and", DOCX.name)
