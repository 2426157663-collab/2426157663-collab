from pathlib import Path
import shutil
import tempfile
import zipfile

from PIL import Image, ImageDraw, ImageFont


DOCX = Path("重磁电综合实验报告_优化版.docx")
OUT = Path("重磁电综合实验报告_真实图件标注版.docx")
WORK = Path(tempfile.mkdtemp(prefix="lab_annotate_"))
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def label(draw, xy, text, color, anchor="la", size=25):
    f = font(size)
    box = draw.textbbox(xy, text, font=f, anchor=anchor, stroke_width=1)
    pad = 6
    draw.rounded_rectangle(
        (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad),
        radius=6,
        fill=(255, 255, 255, 225),
        outline=color,
        width=2,
    )
    draw.text(xy, text, font=f, fill=color, anchor=anchor, stroke_width=1,
              stroke_fill="white")


def arrow(draw, start, end, color, width=4):
    draw.line((start, end), fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    mag = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / mag, dy / mag
    px, py = -uy, ux
    size = 14
    p1 = (x2 - ux * size + px * size * 0.55, y2 - uy * size + py * size * 0.55)
    p2 = (x2 - ux * size - px * size * 0.55, y2 - uy * size - py * size * 0.55)
    draw.polygon((end, p1, p2), fill=color)


def annotate_electric(src, dst):
    im = Image.open(src).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    # Thin outlines only. Interpretation stays in the caption/body so the
    # measured colors and point markers remain unobscured.
    d.rounded_rectangle((385, 55, 735, 330), radius=12,
                        outline=(190, 0, 0, 180), width=2)
    d.rounded_rectangle((890, 55, 1138, 330), radius=12,
                        outline=(0, 75, 200, 180), width=2)
    im.convert("RGB").save(dst, quality=95)


def annotate_radar(src, dst, anomalies, strong_y, anomaly_text):
    im = Image.open(src).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    # Only thin anomaly outlines; no labels/arrows/lines over the radar data.
    for x, y in anomalies:
        d.ellipse((x - 32, y - 45, x + 32, y + 55),
                  outline=(220, 0, 0, 190), width=2)
    im.convert("RGB").save(dst, quality=95)


def flip_radar_plot(src, dst):
    """Flip only the radar data plot horizontally, preserving axes and labels."""
    im = Image.open(src).convert("RGBA")
    # Plot bounds in the original 1300 x 585 exported radargram.
    left, top, right, bottom = 86, 49, 1222, 510
    plot = im.crop((left, top, right, bottom)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    im.paste(plot, (left, top))
    im.convert("RGB").save(dst, quality=95)


with zipfile.ZipFile(DOCX) as z:
    z.extractall(WORK)

media = WORK / "word" / "media"
annotate_electric(media / "image5.png", media / "image5.png")
annotate_radar(media / "image6.png", media / "image6.png",
               [(440, 350), (710, 350)], 338, "信号扰动")
flip_radar_plot(media / "image7.png", media / "image7.png")
annotate_radar(media / "image7.png", media / "image7.png",
               [(508, 270), (783, 270)], 255, "绕射/振铃")
annotate_radar(media / "image8.png", media / "image8.png",
               [(425, 100), (695, 100)], 78, "绕射/振铃")

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for path in WORK.rglob("*"):
        if path.is_file():
            z.write(path, path.relative_to(WORK))

shutil.rmtree(WORK)
print(OUT)
