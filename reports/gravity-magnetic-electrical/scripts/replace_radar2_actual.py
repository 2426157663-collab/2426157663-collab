from pathlib import Path
import shutil
import tempfile
import zipfile

from docx import Document
from PIL import Image, ImageDraw, ImageFont


DOCX = Path("重磁电综合实验报告_真实图件标注版.docx")
SOURCE = Path("探地雷达实验/DAT_0002_反向_虚拟机输出.png")
ANNOTATED = Path("探地雷达实验/DAT_0002_反向_虚拟机输出_标注.png")
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


im = Image.open(SOURCE).convert("RGB").resize((1300, 585), Image.Resampling.LANCZOS)
draw = ImageDraw.Draw(im)

# Labels stay in the white margins. Only thin outlines touch the measured data.
draw.text((650, 15), "探地雷达剖面  测线2（8940 道，数据已反向处理）",
          font=font(20), fill="black", anchor="mm")
draw.text((650, 575), "道号（沿测线位置）", font=font(15), fill="black", anchor="ms")
for x, label in ((517, "井盖响应1"), (802, "井盖响应2")):
    draw.text((x, 43), label, font=font(14), fill=(190, 0, 0), anchor="ms")
    draw.ellipse((x - 25, 238, x + 25, 330), outline=(210, 0, 0), width=2)

im.save(ANNOTATED)

doc = Document(DOCX)
for paragraph in doc.paragraphs:
    if "图件已沿测线方向整体翻转" in paragraph.text:
        revised = paragraph.text.replace(
            "图件已沿测线方向整体翻转",
            "原始 SEG-Y 道记录已按测线方向整体倒序处理",
        )
        for run in paragraph.runs:
            run.text = ""
        paragraph.add_run(revised)
    if "图4-2" in paragraph.text and "测线二雷达剖面" in paragraph.text:
        revised = paragraph.text.replace("已反向显示", "原始道数据已反向处理")
        for run in paragraph.runs:
            run.text = ""
        paragraph.add_run(revised)
doc.save(DOCX)

work = Path(tempfile.mkdtemp(prefix="replace_radar2_"))
with zipfile.ZipFile(DOCX) as archive:
    archive.extractall(work)
shutil.copyfile(ANNOTATED, work / "word" / "media" / "image7.png")
with zipfile.ZipFile(DOCX, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in work.rglob("*"):
        if path.is_file():
            archive.write(path, path.relative_to(work))
shutil.rmtree(work)

print(DOCX)
