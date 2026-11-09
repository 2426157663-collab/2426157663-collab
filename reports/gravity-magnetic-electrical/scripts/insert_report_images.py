from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "重磁电综合实验报告_终审版.docx"
OUTPUT = ROOT / "重磁电综合实验报告_插图版.docx"
FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"


def font(size: int):
    return ImageFont.truetype(FONT_PATH, size)


def fit_contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    target_w, target_h = size
    scale = min(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h), "white")
    canvas.paste(resized, ((target_w - resized.width) // 2, (target_h - resized.height) // 2))
    return canvas


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def make_plate(items, out_path: Path, columns: int = 2, cell=(920, 620)):
    gap = 28
    label_h = 70
    rows = (len(items) + columns - 1) // columns
    w = columns * cell[0] + (columns + 1) * gap
    h = rows * (cell[1] + label_h) + (rows + 1) * gap
    plate = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(plate)
    label_font = font(34)
    small_font = font(28)

    for idx, item in enumerate(items):
        path, label = item[:2]
        mode = item[2] if len(item) > 2 else "cover"
        row, col = divmod(idx, columns)
        x = gap + col * (cell[0] + gap)
        y = gap + row * (cell[1] + label_h + gap)
        fitter = fit_contain if mode == "contain" else fit_cover
        im = fitter(Image.open(path), cell)
        plate.paste(im, (x, y))
        draw.rectangle((x, y, x + cell[0], y + cell[1]), outline=(180, 180, 180), width=2)
        tag = chr(ord("A") + idx)
        draw.rounded_rectangle((x + 14, y + 14, x + 64, y + 58), radius=8, fill=(32, 76, 118))
        draw.text((x + 39, y + 36), tag, anchor="mm", fill="white", font=small_font)
        draw.text((x, y + cell[1] + 18), f"{tag}. {label}", fill=(30, 30, 30), font=label_font)

    plate.save(out_path, quality=94)


def make_wide_bottom_plate(items, out_path: Path):
    gap = 28
    label_h = 70
    top_cell = (920, 620)
    bottom_cell = (1868, 460)
    w = bottom_cell[0] + 3 * gap
    h = top_cell[1] + bottom_cell[1] + 2 * label_h + 3 * gap
    plate = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(plate)
    label_font = font(34)
    small_font = font(28)

    slots = [
        (gap, gap, top_cell, "cover"),
        (2 * gap + top_cell[0], gap, top_cell, "cover"),
        (gap, top_cell[1] + label_h + 2 * gap, bottom_cell, "contain"),
    ]
    for idx, ((path, label), (x, y, cell, mode)) in enumerate(zip(items, slots)):
        fitter = fit_contain if mode == "contain" else fit_cover
        im = fitter(Image.open(path), cell)
        plate.paste(im, (x, y))
        draw.rectangle((x, y, x + cell[0], y + cell[1]), outline=(180, 180, 180), width=2)
        tag = chr(ord("A") + idx)
        draw.rounded_rectangle((x + 14, y + 14, x + 64, y + 58), radius=8, fill=(32, 76, 118))
        draw.text((x + 39, y + 36), tag, anchor="mm", fill="white", font=small_font)
        draw.text((x, y + cell[1] + 18), f"{tag}. {label}", fill=(30, 30, 30), font=label_font)

    plate.save(out_path, quality=94)


def paragraph_after(paragraph, text="", style=None):
    new_para = paragraph.insert_paragraph_before(text, style=style)
    paragraph._p.addnext(new_para._p)
    return new_para


def insert_picture_after(doc: Document, marker: str, picture: Path, caption: str):
    for para in doc.paragraphs:
        if marker in para.text:
            pic_para = paragraph_after(para)
            pic_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = pic_para.add_run()
            run.add_picture(str(picture), width=Cm(15.2))

            cap_para = paragraph_after(pic_para, caption)
            cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap_para.paragraph_format.space_after = Pt(8)
            for run in cap_para.runs:
                run.font.name = "宋体"
                run.font.size = Pt(9)
            return
    raise ValueError(f"Cannot find insertion marker: {marker}")


def main():
    gravity = [
        (ROOT / "重力仪测量实验/微信图片_20260603145920_247_816.jpg", "测点处安置重力仪并调平"),
        (ROOT / "重力仪测量实验/微信图片_20260603150001_249_816.jpg", "井盖测点读数观测"),
        (ROOT / "重力仪测量实验/微信图片_20260603150004_250_816.jpg", "重力仪面板与读数状态"),
        (ROOT / "重力仪测量实验/微信图片_20260603150013_253_816.jpg", "测点复核与现场记录"),
    ]
    electric = [
        (ROOT / " 直流电高密度勘探实验/微信图片_20260615182937_396_816.jpg", "高密度电法主机与参数设置"),
        (ROOT / " 直流电高密度勘探实验/微信图片_20260615182938_397_816.jpg", "电极、电缆连接与接地检查"),
        (ROOT / " 直流电高密度勘探实验/微信图片_20260615170441_391_816.png", "视电阻率拟断面成图结果"),
    ]
    radar = [
        (ROOT / "探地雷达实验/微信图片_20260610101739_269_816.jpg", "测线经过井盖的连续采集"),
        (ROOT / "探地雷达实验/微信图片_20260610101827_271_816.jpg", "2000 MHz 雷达天线"),
        (ROOT / "探地雷达实验/微信图片_20260610101859_273_816.jpg", "雷达主机与采集软件操作"),
        (ROOT / "探地雷达实验/微信图片_20260610101948_276_816.jpg", "天线连接与采集前检查"),
    ]

    with TemporaryDirectory(prefix="lab_report_images_") as tmp:
        tmp_path = Path(tmp)
        gravity_plate = tmp_path / "gravity_plate.jpg"
        electric_plate = tmp_path / "electric_plate.jpg"
        radar_plate = tmp_path / "radar_plate.jpg"
        make_plate(gravity, gravity_plate, columns=2)
        make_wide_bottom_plate(electric, electric_plate)
        make_plate(radar, radar_plate, columns=2)

        doc = Document(INPUT)
        insert_picture_after(
            doc,
            "原始数据未包含仪器格值、观测时间和测点高程",
            gravity_plate,
            "照片1-1  重力仪测量实验现场观测记录",
        )
        insert_picture_after(
            doc,
            "随后按质量筛选条件成图",
            electric_plate,
            "照片3-1  直流电高密度勘探实验采集、转换与成图记录",
        )
        insert_picture_after(
            doc,
            "再按统一灰度规则显示",
            radar_plate,
            "照片4-1  探地雷达实验现场采集与剖面处理记录",
        )
        doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
