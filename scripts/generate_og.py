from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUT = ASSETS / "og.jpg"
PHOTO = ASSETS / "couple-formal.jpeg"
WIDTH, HEIGHT = 1200, 630


def cover_crop(image, width, height):
    ratio = width / height
    src_ratio = image.width / image.height
    if src_ratio > ratio:
        new_width = int(image.height * ratio)
        left = (image.width - new_width) // 2
        box = (left, 0, left + new_width, image.height)
    else:
        new_height = int(image.width / ratio)
        top = max(0, int((image.height - new_height) * 0.18))
        box = (0, top, image.width, top + new_height)
    return image.crop(box).resize((width, height), Image.Resampling.LANCZOS)


def font(path, size):
    return ImageFont.truetype(str(path), size)


def main():
    photo = cover_crop(Image.open(PHOTO).convert("RGB"), WIDTH, HEIGHT)
    photo = ImageEnhance.Contrast(photo).enhance(1.08)
    photo = ImageEnhance.Color(photo).enhance(0.92)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(22, 12, 20, 78))
    draw.rectangle((0, 360, WIDTH, HEIGHT), fill=(22, 12, 20, 120))

    georgia = Path(r"C:\Windows\Fonts\georgia.ttf")
    script = ASSETS / "fonts" / "GreatVibes-Regular.ttf"
    serif = georgia if georgia.exists() else script
    title = font(serif, 28)
    names = font(script, 86) if script.exists() else font(serif, 72)
    date = font(serif, 30)

    ivory = (247, 241, 246, 255)
    blush = (231, 195, 200, 255)

    def center(text, y, used_font, fill):
        box = draw.textbbox((0, 0), text, font=used_font)
        x = (WIDTH - (box[2] - box[0])) / 2
        draw.text((x, y), text, font=used_font, fill=fill)

    center("WEDDING INVITATION", 390, title, blush)
    center("Sudeshna  &  Arkit", 430, names, ivory)
    center("5 DECEMBER 2026", 545, date, ivory)

    composed = Image.alpha_composite(photo.convert("RGBA"), overlay).convert("RGB")
    composed = composed.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=2))
    composed.save(OUT, "JPEG", quality=92, optimize=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
