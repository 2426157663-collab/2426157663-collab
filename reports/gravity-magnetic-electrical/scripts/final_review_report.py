"""Build the fully reviewed final version of the integrated geophysics report."""

from pathlib import Path
import math
import shutil
import struct
import tempfile
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


BASE = Path(__file__).parent
SOURCE = BASE / "重磁电综合实验报告_真实图件标注版.docx"
OUTPUT = BASE / "重磁电综合实验报告_终审版.docx"
MEDIA_DIR = BASE / ".audit" / "final_media"
WDA = BASE / " 直流电高密度勘探实验/ 直流电高密度勘探实验数据.WDA"
GRAVITY_XLSX = BASE / "重力仪测量实验/重力仪测量实验数据.xlsx"
MAGNETIC_XLSX = BASE / "磁法实验/磁法实验数据.xlsx"
GPR_DIR = BASE / "探地雷达实验"

SONGTI = "/System/Library/Fonts/Supplemental/Songti.ttc"
HEITI = "/System/Library/Fonts/STHeiti Medium.ttc"

INK = (35, 45, 55)
GRID = (218, 224, 230)
BLUE = (36, 103, 160)
ORANGE = (226, 126, 34)
GREEN = (72, 139, 65)
RED = (190, 25, 25)


def fnt(size, bold=False):
    return ImageFont.truetype(HEITI if bold else SONGTI, size)


def text_center(draw, xy, text, size, fill=INK, bold=False):
    draw.text(xy, text, font=fnt(size, bold), fill=fill, anchor="mm")


def text_right(draw, xy, text, size, fill=INK, bold=False):
    draw.text(xy, text, font=fnt(size, bold), fill=fill, anchor="rm")


def text_left(draw, xy, text, size, fill=INK, bold=False):
    draw.text(xy, text, font=fnt(size, bold), fill=fill, anchor="lm")


def nice_ticks(low, high, count=6):
    span = max(high - low, 1e-9)
    raw = span / max(count - 1, 1)
    power = 10 ** math.floor(math.log10(raw))
    fraction = raw / power
    step = (1 if fraction <= 1 else 2 if fraction <= 2 else 5 if fraction <= 5 else 10) * power
    start = math.floor(low / step) * step
    end = math.ceil(high / step) * step
    values = []
    value = start
    while value <= end + step * 0.01:
        values.append(value)
        value += step
    return values


def draw_axes(draw, box, x_ticks, y_ticks, x_map, y_map, x_fmt, y_fmt, x_label, y_label):
    left, top, right, bottom = box
    for value in x_ticks:
        x = x_map(value)
        draw.line((x, top, x, bottom), fill=GRID, width=1)
        text_center(draw, (x, bottom + 22), x_fmt(value), 17)
    for value in y_ticks:
        y = y_map(value)
        draw.line((left, y, right, y), fill=GRID, width=1)
        text_right(draw, (left - 10, y), y_fmt(value), 17)
    draw.line((left, top, left, bottom), fill=INK, width=2)
    draw.line((left, bottom, right, bottom), fill=INK, width=2)
    text_center(draw, ((left + right) / 2, bottom + 58), x_label, 19)
    label = Image.new("RGBA", (320, 40), (255, 255, 255, 0))
    ld = ImageDraw.Draw(label)
    text_center(ld, (160, 20), y_label, 19)
    label = label.rotate(90, expand=True)
    draw._image.paste(label, (18, int((top + bottom - label.height) / 2)), label)


def load_xlsx_values(path):
    from openpyxl import load_workbook

    ws = load_workbook(path, data_only=True).active
    return [[cell.value for cell in row] for row in ws.iter_rows()]


def parse_wda():
    data = WDA.read_bytes()
    rows = []
    for index in range(162):
        record = data[524 + index * 148:524 + (index + 1) * 148]
        x = struct.unpack_from("<f", record, 4)[0] - 1.0
        n = struct.unpack_from("<i", record, 8)[0]
        rho = struct.unpack_from("<f", record, 24)[0]
        rows.append((x, n, rho))
    return np.asarray(rows, dtype=float)


def save_gravity_chart(path):
    values = [float(row[1]) for row in load_xlsx_values(GRAVITY_XLSX) if row[1] is not None]
    background = (values[0] + values[2]) / 2
    im = Image.new("RGB", (1000, 600), "white")
    d = ImageDraw.Draw(im)
    box = (125, 80, 930, 475)
    xmin, xmax, ymin, ymax = 0.7, 3.3, 5703.0, 5710.0
    xm = lambda x: box[0] + (x - xmin) / (xmax - xmin) * (box[2] - box[0])
    ym = lambda y: box[3] - (y - ymin) / (ymax - ymin) * (box[3] - box[1])
    draw_axes(
        d, box, [1, 2, 3], list(range(5703, 5711)), xm, ym,
        lambda x: f"测点{int(x)}", lambda y: f"{int(y)}",
        "测点序号", "相对重力仪读数（格）",
    )
    text_center(d, (500, 35), "三个测点相对重力读数对比", 28, bold=True)
    y_bg = ym(background)
    for x in range(box[0], box[2], 22):
        d.line((x, y_bg, min(x + 12, box[2]), y_bg), fill=RED, width=2)
    text_right(d, (box[2] - 5, y_bg - 14), f"背景参考值 = {background:.1f} 格", 17, RED)
    points = [(xm(i + 1), ym(value)) for i, value in enumerate(values)]
    d.line(points, fill=BLUE, width=4)
    for i, ((x, y), value) in enumerate(zip(points, values), 1):
        color = RED if i == 2 else BLUE
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=color, outline="white", width=2)
        text_center(d, (x, y - 24), f"{value:.1f}", 18, color, bold=True)
    im.save(path)


def save_magnetic_charts(total_path, gradient_path):
    rows = load_xlsx_values(MAGNETIC_XLSX)[1:]
    total = np.asarray([float(row[0]) for row in rows])
    gradient = np.asarray([float(row[1]) for row in rows])
    points = np.arange(1, len(total) + 1)
    background = float(np.median(total))
    anomaly = total - background

    im = Image.new("RGB", (1400, 850), "white")
    d = ImageDraw.Draw(im)
    text_center(d, (700, 30), "椭圆闭合测线磁场周向变化", 28, bold=True)

    def panel(box, values, color, ylabel, zero=None):
        xmin, xmax = 0.5, 22.5
        ymin, ymax = nice_ticks(float(values.min()), float(values.max()), 6)[0], nice_ticks(
            float(values.min()), float(values.max()), 6
        )[-1]
        xm = lambda x: box[0] + (x - xmin) / (xmax - xmin) * (box[2] - box[0])
        ym = lambda y: box[3] - (y - ymin) / (ymax - ymin) * (box[3] - box[1])
        draw_axes(
            d, box, [1, 5, 10, 15, 20, 22], nice_ticks(ymin, ymax, 6), xm, ym,
            lambda x: str(int(x)), lambda y: str(int(y)),
            "沿椭圆周向的测点序号", ylabel,
        )
        if zero is not None:
            y = ym(zero)
            for x in range(box[0], box[2], 22):
                d.line((x, y, min(x + 12, box[2]), y), fill=(110, 110, 110), width=2)
        coords = [(xm(x), ym(y)) for x, y in zip(points, values)]
        d.line(coords, fill=color, width=3)
        for x, y in coords:
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)
        return xm, ym

    _, ym1 = panel((125, 80, 1320, 380), total, BLUE, "总磁场强度（nT）", background)
    text_left(d, (145, ym1(background) - 15), f"经验背景值 = {background:.1f} nT", 17, (90, 90, 90))
    panel((125, 485, 1320, 770), anomaly, ORANGE, "相对磁异常 ΔT（nT）", 0)
    im.save(total_path)

    im = Image.new("RGB", (1400, 570), "white")
    d = ImageDraw.Draw(im)
    text_center(d, (700, 32), "磁梯度通道周向变化", 28, bold=True)
    box = (125, 80, 1320, 460)
    xmin, xmax = 0.5, 22.5
    ymin, ymax = -35, 30
    xm = lambda x: box[0] + (x - xmin) / (xmax - xmin) * (box[2] - box[0])
    ym = lambda y: box[3] - (y - ymin) / (ymax - ymin) * (box[3] - box[1])
    draw_axes(
        d, box, [1, 5, 10, 15, 20, 22], [-30, -20, -10, 0, 10, 20, 30], xm, ym,
        lambda x: str(int(x)), lambda y: str(int(y)),
        "沿椭圆周向的测点序号", "磁梯度通道读数（nT）",
    )
    d.line((box[0], ym(0), box[2], ym(0)), fill=(110, 110, 110), width=2)
    coords = [(xm(x), ym(y)) for x, y in zip(points, gradient)]
    d.line(coords, fill=GREEN, width=3)
    for x, y in coords:
        d.rectangle((x - 5, y - 5, x + 5, y + 5), fill=GREEN)
    im.save(gradient_path)


def draw_legend(draw, entries, x, y):
    for index, (name, color) in enumerate(entries):
        yy = y + index * 28
        draw.line((x, yy, x + 32, yy), fill=color, width=3)
        draw.ellipse((x + 11, yy - 4, x + 19, yy + 4), fill=color)
        text_left(draw, (x + 42, yy), name, 17)


def save_resistivity_charts(profile_path, section_path):
    data = parse_wda()
    valid = (data[:, 2] > 0) & (data[:, 2] < 9000)
    clean = data[valid]

    im = Image.new("RGB", (1400, 650), "white")
    d = ImageDraw.Draw(im)
    text_center(d, (700, 32), "不同隔离系数下的视电阻率变化", 28, bold=True)
    box = (130, 80, 1320, 535)
    xm = lambda x: box[0] + (x - 0) / 60 * (box[2] - box[0])
    ym = lambda y: box[3] - y / 8000 * (box[3] - box[1])
    draw_axes(
        d, box, list(range(0, 61, 10)), list(range(0, 8001, 1000)), xm, ym,
        lambda x: str(int(x)), lambda y: str(int(y)),
        "测点中心位置 x（m）", "视电阻率 ρₛ（Ω·m）",
    )
    colors = {1: BLUE, 2: ORANGE, 3: GREEN}
    for n in (1, 2, 3):
        rows = clean[clean[:, 1] == n]
        rows = rows[np.argsort(rows[:, 0])]
        last = None
        for x, _, rho in rows:
            px, py = xm(x), ym(rho)
            if last is not None and x - last[0] <= 3.1:
                d.line((last[1], last[2], px, py), fill=colors[n], width=3)
            d.ellipse((px - 5, py - 5, px + 5, py + 5), fill=colors[n], outline="white", width=1)
            last = (x, px, py)
    draw_legend(d, [(f"n={n}", colors[n]) for n in (1, 2, 3)], box[0] + 18, box[1] + 22)
    im.save(profile_path)

    im = Image.new("RGB", (1430, 500), "white")
    d = ImageDraw.Draw(im)
    text_center(d, (715, 28), "视电阻率拟断面图", 28, bold=True)
    box = (115, 70, 1250, 400)
    grid_w, grid_h = box[2] - box[0], box[3] - box[1]
    xs = np.linspace(1.5, 57.5, grid_w)
    ns = np.linspace(0.8, 3.2, grid_h)
    gx, gn = np.meshgrid(xs, ns)
    px = clean[:, 0][:, None, None]
    pn = clean[:, 1][:, None, None]
    pv = np.log10(clean[:, 2])[:, None, None]
    dist2 = ((gx[None] - px) / 5.0) ** 2 + ((gn[None] - pn) / 0.65) ** 2
    weights = 1.0 / (dist2 + 0.04) ** 1.5
    values = np.sum(weights * pv, axis=0) / np.sum(weights, axis=0)

    stops = [
        (0.0, (32, 50, 170)),
        (0.20, (30, 150, 240)),
        (0.40, (30, 220, 170)),
        (0.60, (235, 235, 55)),
        (0.80, (250, 125, 25)),
        (1.0, (180, 20, 20)),
    ]

    def color(value):
        t = max(0.0, min(1.0, (value - 1.4) / (4.0 - 1.4)))
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if t <= b:
                q = (t - a) / (b - a)
                return tuple(round(ca[i] + q * (cb[i] - ca[i])) for i in range(3))
        return stops[-1][1]

    rgb = np.empty((grid_h, grid_w, 3), dtype=np.uint8)
    flat = values.ravel()
    rgb.reshape(-1, 3)[:] = np.asarray([color(value) for value in flat], dtype=np.uint8)
    plot = Image.fromarray(rgb, "RGB")
    im.paste(plot, (box[0], box[1]))
    xm = lambda x: box[0] + (x - 1.5) / 56.0 * grid_w
    ym = lambda n: box[1] + (n - 0.8) / 2.4 * grid_h
    for x in range(0, 61, 10):
        xx = xm(max(1.5, min(57.5, x)))
        d.line((xx, box[1], xx, box[3]), fill=(255, 255, 255), width=1)
        text_center(d, (xx, box[3] + 22), str(x), 17)
    for n in (1, 2, 3):
        yy = ym(n)
        d.line((box[0], yy, box[2], yy), fill=(255, 255, 255), width=1)
        text_right(d, (box[0] - 10, yy), str(n), 17)
    d.rectangle(box, outline=INK, width=2)
    text_center(d, ((box[0] + box[2]) / 2, box[3] + 58), "测点中心位置 x（m）", 19)
    label = Image.new("RGBA", (230, 40), (255, 255, 255, 0))
    ld = ImageDraw.Draw(label)
    text_center(ld, (115, 20), "隔离系数 n", 19)
    label = label.rotate(90, expand=True)
    im.paste(label, (20, int((box[1] + box[3] - label.height) / 2)), label)
    for x, n, _ in clean:
        d.ellipse((xm(x) - 3, ym(n) - 3, xm(x) + 3, ym(n) + 3), fill="black")
    d.rounded_rectangle((xm(20), box[1] + 3, xm(35), box[3] - 3), radius=12, outline=RED, width=3)
    d.rounded_rectangle((xm(44), box[1] + 3, xm(57.5), box[3] - 3), radius=12, outline=(20, 80, 190), width=3)
    text_center(d, ((xm(20) + xm(35)) / 2, box[1] - 15), "中段相对高阻区", 17, RED, bold=True)
    text_center(d, ((xm(44) + xm(57.5)) / 2, box[1] - 15), "右侧相对低阻区", 17, (20, 80, 190), bold=True)
    cb = (1290, box[1], 1322, box[3])
    for y in range(cb[1], cb[3]):
        value = 4.0 - (y - cb[1]) / (cb[3] - cb[1]) * 2.6
        d.line((cb[0], y, cb[2], y), fill=color(value))
    d.rectangle(cb, outline=INK, width=1)
    for value in (1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
        y = cb[3] - (value - 1.4) / 2.6 * (cb[3] - cb[1])
        text_left(d, (cb[2] + 10, y), f"{value:.1f}", 16)
    im.save(section_path)


def load_segy(path):
    raw = path.read_bytes()
    samples = struct.unpack("<H", raw[3220:3222])[0]
    interval_ps = struct.unpack("<H", raw[3216:3218])[0]
    trace_size = 240 + samples * 2
    traces = (len(raw) - 3600) // trace_size
    data = np.empty((traces, samples), dtype=np.float32)
    for trace in range(traces):
        data[trace] = np.frombuffer(
            raw, dtype="<i2", count=samples, offset=3600 + trace * trace_size + 240
        )
    return data, interval_ps / 1000.0


def gpr_image(path, out_path, line, anomalies, reversed_note=False):
    data, interval_ns = load_segy(path)
    traces, samples = data.shape
    window = interval_ns * samples
    data -= data.mean(axis=1, keepdims=True)
    gain = np.linspace(1.0, 3.0, samples, dtype=np.float32)
    data *= gain[None, :]
    clip = float(np.percentile(np.abs(data[::max(1, traces // 800)]), 98.8))
    gray = np.clip(128 + data.T / max(clip, 1) * 127, 0, 255).astype(np.uint8)
    radar = Image.fromarray(gray, "L").resize((1135, 430), Image.Resampling.BILINEAR).convert("RGB")

    im = Image.new("RGB", (1300, 585), "white")
    im.paste(radar, (105, 65))
    d = ImageDraw.Draw(im)
    plot = (105, 65, 1240, 495)
    xm = lambda trace: plot[0] + (trace - 1) / (traces - 1) * (plot[2] - plot[0])
    ym = lambda ns: plot[1] + ns / window * (plot[3] - plot[1])
    for i in range(6):
        trace = 1 + i * (traces - 1) / 5
        x = xm(trace)
        d.line((x, plot[1], x, plot[3]), fill=(205, 205, 205), width=1)
        text_center(d, (x, plot[3] + 21), f"{round(trace):d}", 15)
        time = i * window / 5
        y = ym(time)
        d.line((plot[0], y, plot[2], y), fill=(205, 205, 205), width=1)
        text_right(d, (plot[0] - 10, y), f"{time:.0f}", 15)
    d.rectangle(plot, outline=INK, width=2)
    note = "，道序已反向" if reversed_note else ""
    text_center(d, (650, 20), f"探地雷达剖面  测线{line}（{traces} 道，时窗 {window:.1f} ns{note}）", 21, bold=True)
    text_center(d, (672, 560), "道号（沿测线位置）", 17)
    label = Image.new("RGBA", (230, 35), (255, 255, 255, 0))
    ld = ImageDraw.Draw(label)
    text_center(ld, (115, 17), "双程走时（ns）", 17)
    label = label.rotate(90, expand=True)
    im.paste(label, (12, int((plot[1] + plot[3] - label.height) / 2)), label)

    for number, (trace, top_ns, bottom_ns, width_traces) in enumerate(anomalies, 1):
        cx, top, bottom = xm(trace), ym(top_ns), ym(bottom_ns)
        half = width_traces / 2 / (traces - 1) * (plot[2] - plot[0])
        d.ellipse((cx - half, top, cx + half, bottom), outline=RED, width=2)
        box = d.textbbox((cx, 49), f"井盖响应{number}", font=fnt(15), anchor="ms")
        d.rounded_rectangle((box[0] - 5, box[1] - 2, box[2] + 5, box[3] + 2), radius=4, fill="white", outline=RED, width=1)
        d.text((cx, 49), f"井盖响应{number}", font=fnt(15), fill=RED, anchor="ms")
        d.line((cx, 53, cx, top - 5), fill=RED, width=1)
        d.polygon(((cx, top - 1), (cx - 4, top - 8), (cx + 4, top - 8)), fill=RED)
    im.save(out_path)


REPLACEMENTS = {
    "3. 熟悉重力仪的格值标定与读数校正（零点漂移、固体潮等）的基本流程；":
        "3. 了解仪器格值、零点漂移、固体潮和测点高程差等因素对相对重力观测的影响；",
    '仪器原理：弹簧式相对重力仪的核心是一套"质量块—弹簧"系统。质量块受到的重力 m·g 与弹簧弹力相平衡，当测点重力发生变化时，弹簧的伸长量随之改变；通过测微螺旋（读数装置）将弹簧恢复到参考位置，所转动的格数即为读数。读数乘以仪器格值 C（单位：mGal/格）即得到相对重力值，故仪器测量的是各点相对于基点的重力差，而非绝对重力。':
        '仪器原理：弹簧式相对重力仪的核心是一套“质量块—弹簧”系统。质量块受到的重力 m·g 与弹簧弹力相平衡；测点重力变化时，弹簧平衡位置随之改变，通过测微装置使其恢复到参考位置并读取格数。两测点读数差乘以仪器格值 C（单位：mGal/格）可换算为相对重力差，因此该仪器测量的是点间重力差，而非绝对重力值。',
    "测量原理：两测点间的重力差可表示为 Δg = C·(S₂ − S₁)，其中 S 为重力仪读数，C 为仪器格值。地下空洞相对于周围土体或混凝土属于密度亏损体，会使其上方测点出现局部负重力异常。本实验通过比较三个测点的相对读数，以邻近正常测点作为背景参考，识别井盖下方空洞对应的低值异常。正式重力勘探还应考虑零点漂移、固体潮和高程差等影响。":
        "测量原理：两测点间的重力差可表示为 Δg = C·(S₂ − S₁)，其中 S 为重力仪读数，C 为仪器格值。地下空洞相对于周围土体或混凝土属于密度亏损体，理论上会在其上方形成局部负重力异常。本实验在测点高程接近、观测时段较短且漂移影响可忽略的前提下，以邻近测点作为背景参考，比较三个测点的相对读数。",
    "选取三个测点开展相对重力观测，其中包含井盖测点，用于识别井盖下方可能存在的空洞。各测点均按整平、解锁、对零和读数的流程进行观测，得到相对重力仪读数 5709.0、5703.6 和 5709.2 格。通过比较各测点读数的相对高低，识别由地下密度亏损引起的局部低重力异常。":
        "依次完成三个测点的相对重力观测，原始数据表记录的读数分别为 5709.0、5703.6 和 5709.2 格。结合现场记录，测点 2 为井盖测点；测点 1 和测点 3 作为邻近参考点。原始数据未包含仪器格值、观测时间和测点高程，因此本报告仅比较相对读数，不进行 mGal 换算及漂移、高程改正。",
    "空洞内部主要为空气，其平均密度显著低于周围土体或混凝土，因此会造成局部质量亏损，并在地表表现为负重力异常。若测点 2 为井盖上的观测点，则其明显偏低的读数与井盖下存在空洞的现场情况相符，可判断测点 2 对应空洞位置；测点 1 和测点 3 可作为附近正常场的参考。由于资料未给出仪器格值，本文仅比较相对读数，未将 5.5 格的异常幅值换算为 mGal。":
        "测点 2 比测点 1、3 的背景平均值低 5.5 格。该低值与井盖下方空洞造成密度亏损、产生局部负重力异常的理论响应一致。但由于缺少仪器格值、重复观测、漂移改正和高程信息，本结果只能作为局部低值异常的定性识别，不能给出异常的 mGal 幅值或单独据此确定空洞规模。",
    "本实验利用相对重力仪比较了三个测点的重力读数。测点 1 和测点 3 的读数分别为 5709.0 格和 5709.2 格，可视为附近背景参考；测点 2 的读数为 5703.6 格，比背景平均值低约 5.5 格，表现为明显的局部低重力异常。结合井盖下方为空洞的现场条件，可判断测点 2 对应井盖及其下方空洞。实验表明，相对重力测量能够利用地下介质密度差异识别空洞等低密度异常体。":
        "三个测点中，井盖测点 2 的读数比邻近参考点平均值低 5.5 格，表现为局部低值，与井盖下方空洞的密度亏损响应一致。受原始资料完整性限制，本实验结论为定性判断；后续应增加重复观测，并结合仪器格值、零点漂移和高程改正验证异常幅值。",
    "2. 掌握质子旋进磁力仪（及磁梯度仪）的工作原理与野外总场、垂直梯度的测量方法；":
        "2. 掌握质子旋进磁力仪及磁梯度仪的工作原理与野外总场、梯度通道观测方法；",
    "4. 根据磁异常及梯度的变化特征，对地下磁性体（异常源）作初步推断。":
        "4. 根据磁异常及梯度通道变化特征，对局部磁性异常源作初步分析。",
    "仪器原理：质子旋进磁力仪利用氢质子在地磁场中的旋进现象工作。强极化磁场撤去后，质子绕地磁场方向旋进，其旋进频率 f 与总磁场强度 T 成正比，可写为 T = f/γ_p，其中 γ_p 为质子旋磁比。因此，通过测量旋进频率即可获得总场强度。磁梯度观测通常由竖直方向上、下两个探头的总场差值 ΔT 获得；只有在已知探头间距 Δz 时，才能进一步计算垂直梯度 ΔT/Δz。":
        "仪器原理：质子旋进磁力仪利用氢质子在地磁场中的旋进现象工作。强极化磁场撤去后，质子旋进频率 f 与总磁场强度 T 成正比；若 γₚ 采用频率形式的旋磁系数，则 T = f/γₚ。磁梯度仪通常记录竖直方向上、下两个探头的总场差值 ΔT；只有在已知探头间距 Δz 时，才能进一步计算垂直梯度 ΔT/Δz。",
    "22 个测点的总磁场强度范围为 52315.92～53980.99 nT，中位数约为 53538 nT。以该中位数作为椭圆闭合测线的经验背景值后，多数测点的相对异常在 ±300 nT 内；沿椭圆观测至第 10、11 测点附近时，总场降至约 52316 nT，对应约 −1220 nT 的局部负异常，说明椭圆周向上的该段位置受到显著局部磁场影响。异常正负同时受目标磁性、形状、埋深、磁化方向和区域场方向影响，不能仅凭负异常判断目标性质。":
        "22 个测点的总磁场强度范围为 52315.92～53980.99 nT，中位数为 53538.405 nT。以该中位数作为经验背景值后，13 个测点的相对异常位于 ±300 nT 内；第 10、11 测点总场分别为 52315.92 nT 和 52316.00 nT，对应约 −1222.5 nT 的局部负异常。异常正负同时受目标磁性、形状、埋深、磁化方向和区域场方向影响，不能仅凭负异常判断目标性质。",
    "本实验沿椭圆闭合测线完成了 22 个测点的总场与梯度通道观测，掌握了环绕式磁测数据的整理和周向变化分析方法。第 10～11 测点所在的椭圆周向段出现幅值约 −1200 nT 的局部负异常，并伴随明显的梯度通道负极值，是最值得进一步核查的异常段。环绕测量能够从不同方位感知异常体的磁场响应；若要确定异常源的平面位置、性质和范围，还需记录各测点坐标与椭圆方位，并开展日变改正及加密测量。":
        "本实验沿椭圆闭合测线完成了 22 个测点的总场与梯度通道观测。第 10～11 测点所在周向段出现约 −1222 nT 的局部负异常，并伴随梯度通道负极值，是最需核查的异常段。由于缺少测点坐标、椭圆方位、探头间距和日变改正，本资料只能识别周向异常段，不能确定异常源的平面位置、性质和范围。",
    "1. 掌握直流电阻率法（高密度电法）的基本原理与视电阻率的概念；":
        "1. 掌握直流电阻率法（高密度电法）的基本原理与视电阻率概念；",
    "3. 学会原始数据（WDA 数据格式）的格式转换（→三列文本→配套绘图软件网格）与视电阻率等值断面图的绘制；":
        "3. 学会将 WDA 原始数据转换为三列文本，并绘制视电阻率拟断面图；",
    "4. 根据视电阻率断面图推断地下电性结构的横向与纵向变化。":
        "4. 根据视电阻率拟断面图分析地下介质的横向电性差异。",
    "仪器原理：高密度电阻率法是阵列式直流电法。一次性沿测线布设数十根电极（本实验为 60 道），由程控开关按预设装置（温纳、偶极—偶极等）自动选择供电电极 A、B 和测量电极 M、N 的组合，逐次供入电流 I 并测量电位差 ΔU。视电阻率由 ρ_s = K·ΔU/I 计算，其中 K 为与电极排列几何相关的装置系数。改变电极间距（隔离系数 n）即可获得不同深度的信息，从而实现二维电性结构的高密度探测。":
        "仪器原理：高密度电阻率法是阵列式直流电法。本实验沿测线布设 60 根电极，由程控开关自动选择供电电极 A、B 和测量电极 M、N，逐次供入电流 I 并测量电位差 ΔU。视电阻率按 ρₛ = K·ΔU/I 计算，其中 K 为装置系数。WDA 数据中 n = 1～3 的排列数量及中心位置与温纳装置一致；增大隔离系数 n 可获得对更深部介质的响应。",
    "测量原理：以测点中心位置 x 为横坐标、隔离系数 n（极距，正比于探测深度）为纵坐标，将各排列的视电阻率绘制成视电阻率拟断面图（等值断面图）。高阻区通常对应基岩、干燥砂砾或空洞，低阻区对应含水层、黏土或断裂破碎带，据此推断地下电性界面与异常体。":
        "测量原理：以排列中心位置 x 为横坐标、隔离系数 n 为纵坐标，将各排列的视电阻率绘制成拟断面图。隔离系数仅与探测深度相关，不等同于真实深度；高、低阻异常也具有多解性，需结合地质资料、数据质量控制和二维反演进行解释。",
    "沿测线等间距（0.5 m 测点间距）布设 60 道电极，连接多芯电缆与主机，设定装置类型与隔离系数后由仪器自动逐排列采集，共获得 162 个观测记录（保存为 WDA 文件），每条记录包含测点位置 x、供电电流 I、电位差 ΔU 及视电阻率 ρ_s。随后用配套格式转换程序将 WDA 数据导出为 (x, n, ρ_s) 三列文本，导入配套绘图软件生成网格并绘制视电阻率等值断面图。":
        "沿测线按 1.0 m 电极间距布设 60 根电极，连接多芯电缆与主机后完成 n = 1～3 的自动采集，共获得 162 条 WDA 观测记录。经配套格式转换后得到 (x, n, ρₛ) 三列数据，其中排列中心位置 x 的范围为 1.5～57.5 m；随后按质量筛选条件成图。",
    "从 WDA 原始数据中共解析出 162 个观测记录，测点位置 x 覆盖 2.5～58.5 m。按本次成图采用的筛选条件 0 < ρ_s < 9000 Ω·m，共保留 68 条记录，占约 42%；其余 94 条约占 58%，主要为负值或溢出值 99999。负值和溢出值可由接地不良、供电不足、信噪比较低或测量超量程等多种因素造成，仅凭结果数据不能确定唯一原因，故成图前统一剔除。":
        "WDA 文件包含 162 条记录，转换后的排列中心位置 x 为 1.5～57.5 m。按 0 < ρₛ < 9000 Ω·m 的成图筛选条件，共保留 68 条记录，占 42.0%；剔除的 94 条记录包括 78 条负值、11 条 99999 溢出值，以及 5 条高于 9000 Ω·m 的正值。异常值成因可能包括接地、供电、信噪比或量程问题，仅凭结果数据不能确定唯一原因。",
    "有效视电阻率的中位数约为 924 Ω·m，范围为 29～7822 Ω·m。视电阻率剖面和拟断面图显示，测线中段 x ≈ 20～35 m 整体相对高阻，测线两端及 x > 44 m 段相对低阻，反映出明显的横向电性差异。高、低阻成因具有多解性，可能分别与介质密实程度、含水量、岩性或破碎程度有关。由于有效数据仅占约 42%，且当前图件为视电阻率拟断面而非反演电阻率断面，异常位置和深度解释应保持谨慎。":
        "有效视电阻率范围为 29.28～7822.24 Ω·m，中位数为 924.21 Ω·m。有效数据的分段统计显示，x = 20～35 m 段中位数约为 1569 Ω·m，整体相对高阻；x > 44 m 段中位数约为 621 Ω·m，整体相对低阻。高、低阻成因具有多解性；同时有效记录仅占 42.0%，当前图件又是拟断面而非反演电阻率断面，因此不作真实深度和具体地质体的确定性解释。",
    "本实验完成了 60 道高密度电阻率法的数据采集、WDA 数据格式转换和视电阻率拟断面成图，掌握了从原始数据到图件解释的基本流程。结果显示测线中段相对高阻、两端相对低阻，说明地下介质存在横向电性差异。本次仅约 42% 的记录满足成图筛选条件，数据完整性是解释可靠性的主要限制。后续应优先检查电极接地和供电状态、复测异常数据，并采用质量控制和二维反演提高解释可信度。":
        "本实验完成了 60 根电极的高密度电阻率法采集、WDA 格式转换和视电阻率拟断面成图。有效数据表明测线中段相对高阻、右侧相对低阻，反映出横向电性差异。由于仅 42.0% 的记录满足本次成图筛选条件，后续应优先检查接地和供电状态、复测异常记录，并通过质量控制与二维反演提高解释可信度。",
    "图3-1  不同隔离系数 n 下的视电阻率剖面 ρ_s(x)":
        "图3-1  不同隔离系数 n 下的视电阻率剖面 ρₛ(x)",
    "图3-2  视电阻率拟断面图（红色细框为中段相对高阻区，蓝色细框为右侧低阻区）":
        "图3-2  视电阻率拟断面图（纵轴为隔离系数 n；色标为 log₁₀[ρₛ/(1 Ω·m)]）",
    "1. 了解探地雷达（探地雷达）的探测原理及其在浅层工程探测中的应用；":
        "1. 了解探地雷达的探测原理及其在浅层工程探测中的应用；",
    "2. 熟悉雷达主机、天线（本实验 2000 MHz）及 配套采集软件的野外工作流程；":
        "2. 熟悉雷达主机、2000 MHz 天线及配套采集软件的野外工作流程；",
    "测量原理：界面或目标的等效深度可由双程走时 t 按 h = v·t/2 换算。本实验按干燥砂相对介电常数 ε_r = 5 估算波速 v ≈ 0.134 m/ns，因此 50 ns 时窗对应的理论最大等效深度约为 3.35 m。该深度随介电常数和时零位置变化，未经速度标定时只能作为估计值。天线沿测线连续移动形成雷达剖面，孤立目标通常表现为绕射双曲线，连续界面则表现为较连续的反射同相轴。":
        "测量原理：界面或目标的等效深度可由双程走时 t 按 h = v·t/2 换算。若按 εᵣ = 5 估算，波速约为 0.134 m/ns；但本次数据未完成时零与速度标定，因此图件统一采用双程走时轴，不直接标注真实深度。SEG-Y 文件头显示 DAT_0001 的时窗为 49.7 ns，DAT_0002 和 DAT_0003 的时窗均为 199.7 ns。",
    "采用 2000 MHz 非屏蔽天线，设定时窗 50 ns、每道 512 采样点、叠加 2 次，沿三条测线连续拖动采集，分别得到剖面 DAT_0001、DAT_0002、DAT_0003（道数依次为 8995、8940、10602），数据以 SEG-Y 数据格式导出。室内处理对每道去直流、施加随深度增大的线性增益，并以灰度成像得到雷达剖面。":
        "采用 2000 MHz 天线沿三条测线连续采集，分别得到 DAT_0001、DAT_0002、DAT_0003，共 8995、8940、10602 道；每道均为 512 个采样点。根据 SEG-Y 文件头，三条测线的采样间隔分别为 0.097、0.390、0.390 ns。室内成图对每道去除直流分量并施加线性时间增益，再按统一灰度规则显示。",
    "三条雷达剖面均存在横向连续的强同相轴，但其双程走时位置差异明显：DAT_0001 约位于 30 ns，DAT_0002 约位于 22 ns，DAT_0003 则接近时窗顶部。由于数据尚未完成统一的时零校正，该强同相轴更宜解释为首波、直达波或天线耦合产生的强响应，不能直接作为同一地下界面进行深度对比。DAT_0002 的采集行进方向与另外两条测线相反，原始 SEG-Y 道记录已按测线方向整体倒序处理，以统一三条剖面的显示方向。三条测线上均出现两组位置对应的局部异常：DAT_0001 约位于第 2800 道和第 5000 道，翻转后的 DAT_0002 约位于第 3290 道和第 5440 道，DAT_0003 约位于第 3200 道和第 5650 道。结合现场测线记录，这两组异常分别由雷达天线经过两个井盖时产生。金属井盖及天线耦合条件的突变会造成强反射、振铃、局部信号扰动或衰减，因此不同测线中的异常形态有所差异。":
        "三条雷达剖面均存在横向连续的强同相轴，其主要位置分别约为 31、89、14 ns。由于各测线时窗和时零位置不同，该同相轴更宜解释为首波、直达波或天线耦合响应，不能直接作为同一地下界面比较深度。DAT_0002 的原始道序已整体倒序，以统一显示方向。结合自动能量识别与图像检查，两组井盖响应中心约位于：DAT_0001 第 2770、4940 道，DAT_0002 第 3240、5440 道，DAT_0003 第 3220、5670 道。井盖及耦合条件突变会造成局部强反射、振铃、扰动或衰减，因此三条测线的响应形态并不完全相同。",
    "图4-1  测线一雷达剖面（DAT_0001，8995 道；红色细圈为经过两个井盖时的响应）":
        "图4-1  测线一雷达剖面（DAT_0001，时窗 49.7 ns；红圈为井盖响应）",
    "图4-2  测线二雷达剖面（DAT_0002，原始道数据已反向处理；红色细圈为经过两个井盖时的响应）":
        "图4-2  测线二雷达剖面（DAT_0002，时窗 199.7 ns，道序已反向；红圈为井盖响应）",
    "图4-3  测线三雷达剖面（DAT_0003；红色细圈为经过两个井盖时的响应）":
        "图4-3  测线三雷达剖面（DAT_0003，时窗 199.7 ns；红圈为井盖响应）",
}

ALT_TEXTS = [
    "三个测点相对重力仪读数折线图，测点2为明显低值。",
    "椭圆闭合测线总磁场与相对磁异常周向变化图。",
    "椭圆闭合测线磁梯度通道周向变化图。",
    "不同隔离系数下的视电阻率剖面图。",
    "视电阻率拟断面图，标出中段相对高阻区和右侧相对低阻区。",
    "探地雷达测线一剖面及两处井盖响应标注。",
    "探地雷达测线二剖面及两处井盖响应标注。",
    "探地雷达测线三剖面及两处井盖响应标注。",
]


def set_run_font(run, east_asia="宋体", size=Pt(12), bold=None, color=None):
    run.font.name = "Times New Roman"
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), "Times New Roman")
    rfonts.set(qn("w:hAnsi"), "Times New Roman")
    rfonts.set(qn("w:eastAsia"), east_asia)
    run.font.size = size
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def replace_paragraph_text(paragraph, value):
    for run in paragraph.runs:
        run.text = ""
    paragraph.add_run(value)


def remove_paragraph(paragraph):
    element = paragraph._element
    element.getparent().remove(element)


def fill_metadata_table(table):
    contents = [
        ["姓名：***", "班级：*******", "学号：**********", "指导老师：**"],
        ["组员：", "***、**、***、***、***", "实验成绩：", ""],
    ]
    for row, values in zip(table.rows, contents):
        for cell, value in zip(row.cells, values):
            cell.text = value
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    set_run_font(run, size=Pt(9.5))


def add_alt_texts(doc):
    drawings = doc._element.xpath(".//wp:docPr")
    for node, value in zip(drawings, ALT_TEXTS):
        node.set("descr", value)
        node.set("title", value.split("，")[0].rstrip("。"))


def build_document():
    doc = Document(SOURCE)
    matched = set()
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text in REPLACEMENTS:
            replace_paragraph_text(paragraph, REPLACEMENTS[text])
            matched.add(text)

    missing = set(REPLACEMENTS) - matched
    if missing:
        raise RuntimeError(f"Unmatched paragraphs: {len(missing)}")

    for table in doc.tables:
        fill_metadata_table(table)

    for paragraph in list(doc.paragraphs):
        if paragraph._p.xpath(".//w:br[@w:type='page']"):
            remove_paragraph(paragraph)
        elif paragraph.text.strip().startswith("测量实物图："):
            remove_paragraph(paragraph)

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        if text == "重磁电综合实验报告":
            for run in paragraph.runs:
                set_run_font(run, "黑体", Pt(26), True)
        elif text.startswith("实验") and text[2:3].isdigit():
            paragraph.paragraph_format.page_break_before = True
            paragraph.paragraph_format.keep_with_next = True
            for run in paragraph.runs:
                set_run_font(run, "黑体", Pt(15), True)
        elif text.startswith(("一、", "二、", "三、", "四、", "五、")):
            paragraph.paragraph_format.keep_with_next = True
            for run in paragraph.runs:
                set_run_font(run, "黑体", Pt(14), True)
        elif text.startswith("图") and len(text) > 3 and text[1].isdigit():
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_before = Pt(3)
            paragraph.paragraph_format.space_after = Pt(8)
            for run in paragraph.runs:
                set_run_font(run, "宋体", Pt(9.5), False, RGBColor(89, 89, 89))
        elif text.startswith(("姓　　名", "班　　级", "学　　号", "指导老师", "组　　员")):
            for run in paragraph.runs:
                set_run_font(run, "宋体", Pt(14))
        elif text.startswith("重力勘探"):
            for run in paragraph.runs:
                set_run_font(run, "楷体", Pt(13))
        else:
            paragraph.paragraph_format.line_spacing = 1.5
            for run in paragraph.runs:
                set_run_font(run, "宋体", Pt(12))

    add_alt_texts(doc)
    doc.core_properties.title = "重磁电综合实验报告（终审版）"
    doc.core_properties.subject = "重力、磁法、高密度电法与探地雷达综合实验"
    doc.core_properties.comments = "依据原始 XLSX、WDA、SEG-Y 数据完成终审与图件重绘"
    doc.save(OUTPUT)


def replace_media():
    work = Path(tempfile.mkdtemp(prefix="final_report_"))
    rebuilt = work.with_suffix(".docx")
    try:
        with zipfile.ZipFile(OUTPUT) as archive:
            archive.extractall(work)
        for index in range(1, 9):
            shutil.copyfile(MEDIA_DIR / f"image{index}.png", work / "word" / "media" / f"image{index}.png")
        with zipfile.ZipFile(rebuilt, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in work.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(work))
        shutil.move(rebuilt, OUTPUT)
    finally:
        shutil.rmtree(work, ignore_errors=True)
        rebuilt.unlink(missing_ok=True)


def main():
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    save_gravity_chart(MEDIA_DIR / "image1.png")
    save_magnetic_charts(MEDIA_DIR / "image2.png", MEDIA_DIR / "image3.png")
    save_resistivity_charts(MEDIA_DIR / "image4.png", MEDIA_DIR / "image5.png")
    gpr_image(
        GPR_DIR / "DAT_0001.SGY", MEDIA_DIR / "image6.png", 1,
        [(2773, 27, 39, 380), (4936, 27, 39, 380)],
    )
    gpr_image(
        GPR_DIR / "DAT_0002_反向.SGY", MEDIA_DIR / "image7.png", 2,
        [(3241, 80, 132, 400), (5441, 80, 126, 400)], reversed_note=True,
    )
    gpr_image(
        GPR_DIR / "DAT_0003.SGY", MEDIA_DIR / "image8.png", 3,
        [(3221, 9, 55, 420), (5667, 9, 55, 420)],
    )
    build_document()
    replace_media()
    print(OUTPUT)


if __name__ == "__main__":
    main()
