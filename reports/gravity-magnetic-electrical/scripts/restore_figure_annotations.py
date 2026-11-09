from pathlib import Path
import shutil
import tempfile
import zipfile

from PIL import Image, ImageDraw, ImageFont


DOCX = Path("重磁电综合实验报告_真实图件标注版.docx")
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
WORK = Path(tempfile.mkdtemp(prefix="restore_annotations_"))


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def text(draw, xy, value, color, size=17, anchor="ms"):
    draw.text(xy, value, font=font(size), fill=color, anchor=anchor,
              stroke_width=2, stroke_fill="white")


def arrow(draw, start, end, color, width=2):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    mag = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / mag, dy / mag
    px, py = -uy, ux
    size = 7
    draw.polygon((
        end,
        (x2 - ux * size + px * size * 0.5, y2 - uy * size + py * size * 0.5),
        (x2 - ux * size - px * size * 0.5, y2 - uy * size - py * size * 0.5),
    ), fill=color)


def radar(path, points):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    for x, top, bottom, name, label_x in points:
        color = (195, 0, 0)
        d.ellipse((x - 31, top, x + 31, bottom), outline=color, width=2)
        text(d, (label_x, 46), name, color, size=16)
        arrow(d, (label_x, 49), (x, top - 3), color)
    im.save(path)


def electric(path):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    red = (180, 0, 0)
    blue = (0, 70, 180)
    d.rounded_rectangle((385, 55, 735, 330), radius=12, outline=red, width=2)
    d.rounded_rectangle((890, 55, 1138, 330), radius=12, outline=blue, width=2)
    text(d, (560, 48), "高阻异常区", red, size=18)
    text(d, (1014, 48), "低阻异常区", blue, size=18)
    im.save(path)


with zipfile.ZipFile(DOCX) as archive:
    archive.extractall(WORK)

media = WORK / "word" / "media"
electric(media / "image5.png")
radar(media / "image6.png", [
    (440, 305, 405, "井盖响应1", 385),
    (710, 305, 405, "井盖响应2", 765),
])
radar(media / "image8.png", [
    (425, 55, 155, "井盖响应1", 365),
    (695, 55, 155, "井盖响应2", 755),
])

with zipfile.ZipFile(DOCX, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in WORK.rglob("*"):
        if path.is_file():
            archive.write(path, path.relative_to(WORK))

shutil.rmtree(WORK)
print(DOCX)
