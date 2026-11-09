from pathlib import Path
import shutil
import tempfile
import zipfile

from docx import Document
from PIL import Image, ImageDraw, ImageFont


DOCX = Path("重磁电综合实验报告_真实图件标注版.docx")
TMP_DOCX = Path("重磁电综合实验报告_中文化临时版.docx")
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"

TEXT_REPLACEMENTS = {
    "重力 mg": "重力 m·g",
    "WDA 格式": "WDA 数据格式",
    "→三列文本→Surfer 网格 grd": "→三列文本→配套绘图软件网格",
    "导入 Surfer 生成 grd 网格": "导入配套绘图软件生成网格",
    "GPR": "探地雷达",
    "Prism2 采集软件": "配套采集软件",
    "雷达剖面（radargram）": "雷达剖面",
    "Zond-12e 雷达主机": "探地雷达主机",
    "以 SEG-Y 格式导出": "以 SEG-Y 数据格式导出",
    "（dewow）": "",
    "log₁₀ρ_s": "视电阻率常用对数",
}


def fnt(size):
    return ImageFont.truetype(FONT_PATH, size)


def cover_text(draw, box, text, size, anchor="mm", fill="black"):
    draw.rectangle(box, fill="white")
    x = (box[0] + box[2]) // 2
    y = (box[1] + box[3]) // 2
    draw.text((x, y), text, font=fnt(size), fill=fill, anchor=anchor)


def vertical_text(im, box, text, size):
    target_w, target_h = box[2] - box[0], box[3] - box[1]
    layer = Image.new("RGB", (target_h, target_w), "white")
    d = ImageDraw.Draw(layer)
    d.text((layer.width // 2, layer.height // 2), text, font=fnt(size),
           fill="black", anchor="mm")
    layer = layer.rotate(90, expand=True)
    layer = layer.resize((target_w, target_h))
    im.paste(layer, (box[0], box[1]))


def localize_image(path, number):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    w, h = im.size

    if number == 1:
        cover_text(d, (170, 15, 610, 55), "三个测点相对重力对比", 18)
        cover_text(d, (0, 235, 200, 285), "相对重力仪读数", 15)
        cover_text(d, (300, 470, 550, 515), "测点序号", 15)
        for x, text in [(210, "测点1"), (420, "测点2"), (630, "测点3")]:
            cover_text(d, (x - 50, 440, x + 50, 475), text, 14)
        cover_text(d, (500, 95, 750, 122), "背景参考值 = 5709.1", 13,
                   fill="#c00000")
    elif number == 2:
        cover_text(d, (420, 5, 790, 48), "椭圆闭合测线磁场周向变化", 22)
        cover_text(d, (480, 730, 740, 775), "沿椭圆周向的测点序号", 18)
        vertical_text(im, (0, 105, 36, 315), "总磁场强度（nT）", 13)
        vertical_text(im, (0, 450, 36, 665), "相对磁异常（nT）", 13)
        cover_text(d, (110, 315, 420, 355), "背景值 = 53538 nT", 16)
    elif number == 3:
        cover_text(d, (390, 5, 850, 45), "磁梯度通道周向变化", 21)
        cover_text(d, (470, 410, 750, 450), "沿椭圆周向的测点序号", 17)
        vertical_text(im, (0, 115, 40, 315), "磁梯度通道（nT）", 13)
    elif number == 4:
        cover_text(d, (320, 5, 1010, 48), "不同隔离系数下的视电阻率变化", 22)
        cover_text(d, (430, 450, 880, 520), "测线位置（米）", 17)
        d.rectangle((0, 100, 48, 380), fill="white")
        vertical_text(im, (0, 105, 46, 355), "视电阻率（欧姆·米）", 13)
    elif number == 5:
        cover_text(d, (250, 0, 1080, 48), "视电阻率拟断面图", 22)
        cover_text(d, (450, 365, 850, 410), "测线位置（米）", 17)
        vertical_text(im, (0, 85, 42, 290), "拟深度（米）", 13)
    elif number in (6, 7, 8):
        trace_counts = {6: "8995 道", 7: "8940 道（已反向显示）", 8: "10602 道"}
        cover_text(d, (250, 5, 1050, 48),
                   f"探地雷达剖面  测线{number - 5}（{trace_counts[number]}）", 21)
        cover_text(d, (430, 540, 880, 585), "道号（沿测线位置）", 17)
        d.rectangle((0, 120, 46, 455), fill="white")
        d.rectangle((1250, 120, 1300, 455), fill="white")
        vertical_text(im, (0, 190, 44, 405), "等效深度（米）", 12)
        vertical_text(im, (1254, 190, 1300, 405), "双程走时（ns）", 12)

    im.save(path)


doc = Document(DOCX)
for p in doc.paragraphs:
    text = p.text
    revised = text
    for old, new in TEXT_REPLACEMENTS.items():
        revised = revised.replace(old, new)
    if revised != text:
        for run in p.runs:
            run.text = ""
        p.add_run(revised)
doc.save(TMP_DOCX)

work = Path(tempfile.mkdtemp(prefix="localized_report_"))
with zipfile.ZipFile(TMP_DOCX) as z:
    z.extractall(work)
for number in range(1, 9):
    localize_image(work / "word" / "media" / f"image{number}.png", number)
with zipfile.ZipFile(DOCX, "w", zipfile.ZIP_DEFLATED) as z:
    for path in work.rglob("*"):
        if path.is_file():
            z.write(path, path.relative_to(work))

TMP_DOCX.unlink()
shutil.rmtree(work)
print(DOCX)
