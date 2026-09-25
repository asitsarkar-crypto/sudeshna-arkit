import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCRIPT = ASSETS / "fonts" / "GreatVibes-Regular.ttf"
GEORGIA = Path(r"C:\Windows\Fonts\georgia.ttf")
NIRMALA = Path(r"C:\Windows\Fonts\nirmala.ttf")
MUSIC = ASSETS / "wedding-song.mp3"
OUT_WIDE = ASSETS / "wedding-ecard.mp4"
OUT_TALL = ASSETS / "wedding-ecard-9x16.mp4"
VENUE_PHOTO = ASSETS / "venue-google-place.jpg"


def run(cmd):
    subprocess.run(cmd, check=True)


def load_font(path, size):
    return ImageFont.truetype(str(path if path.exists() else GEORGIA), size)


def cover(image, size, top=0.16):
    width, height = size
    ratio = width / height
    src = image.width / image.height
    if src > ratio:
        new_w = int(image.height * ratio)
        left = (image.width - new_w) // 2
        box = (left, 0, left + new_w, image.height)
    else:
        new_h = int(image.width / ratio)
        top_px = max(0, int((image.height - new_h) * top))
        box = (0, top_px, image.width, min(image.height, top_px + new_h))
    return image.crop(box).resize(size, Image.Resampling.LANCZOS)


def card(size, lines, photo=None):
    width, height = size
    if photo:
        base = cover(Image.open(photo).convert("RGB"), size)
        base = ImageEnhance.Contrast(base).enhance(1.06)
        layer = Image.new("RGBA", size, (16, 10, 14, 120))
        image = Image.alpha_composite(base.convert("RGBA"), layer)
    else:
        image = Image.new("RGBA", size, (33, 21, 31, 255))
    draw = ImageDraw.Draw(image)
    y = height * 0.52 if photo else height * 0.28
    for text, kind in lines:
        if kind == "script":
            used = load_font(SCRIPT, int(height * 0.08))
            fill = (247, 241, 246, 255)
        elif kind == "bn":
            used = load_font(NIRMALA, int(height * 0.032))
            fill = (231, 195, 200, 255)
        elif kind == "kicker":
            used = load_font(GEORGIA, int(height * 0.026))
            fill = (231, 195, 200, 255)
            text = text.upper()
        else:
            used = load_font(GEORGIA, int(height * 0.036))
            fill = (247, 241, 246, 255)
        box = draw.textbbox((0, 0), text, font=used)
        x = (width - (box[2] - box[0])) / 2
        draw.text((x, y), text, font=used, fill=fill)
        y += (box[3] - box[1]) + height * 0.02
    return image.convert("RGB")


def venue_location_card(size):
    width, height = size
    photo = cover(Image.open(VENUE_PHOTO).convert("RGB"), size, top=0.08)
    photo = ImageEnhance.Contrast(photo).enhance(1.08)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, width, height), fill=(16, 10, 14, 70))
    panel_top = int(height * 0.52)
    draw.rounded_rectangle(
        (int(width * 0.07), panel_top, int(width * 0.93), int(height * 0.94)),
        radius=int(height * 0.02),
        fill=(26, 14, 12, 214),
        outline=(199, 146, 108, 180),
        width=2,
    )

    pin_x = int(width * 0.13)
    pin_y = int(height * 0.62)
    pin_r = int(height * 0.028)
    draw.ellipse((pin_x - pin_r, pin_y - pin_r, pin_x + pin_r, pin_y + pin_r), fill=(196, 57, 45, 255))
    draw.ellipse(
        (pin_x - int(pin_r * 0.38), pin_y - int(pin_r * 0.38), pin_x + int(pin_r * 0.38), pin_y + int(pin_r * 0.38)),
        fill=(247, 241, 246, 255),
    )

    kicker = load_font(GEORGIA, int(height * 0.022))
    title = load_font(GEORGIA, int(height * 0.038))
    bn = load_font(NIRMALA, int(height * 0.034))
    body = load_font(GEORGIA, int(height * 0.024))
    x = int(width * 0.18)
    y = int(height * 0.56)
    lines = [
        ("GOOGLE MAPS LOCATION", kicker, (231, 195, 200, 255)),
        ("Lalita Banquet", title, (247, 241, 246, 255)),
        ("ললিতা ভবন", bn, (231, 195, 200, 255)),
        ("97, Keshab Chandra Sen Street", body, (247, 241, 246, 255)),
        ("City College, College Street, Kolkata 700009", body, (247, 241, 246, 255)),
        ("৯৭, কেশব চন্দ্র সেন স্ট্রিট, কলকাতা ৭০০০০৯", bn, (231, 195, 200, 255)),
        ("GET DIRECTIONS  ·  দিকনির্দেশ", kicker, (199, 146, 108, 255)),
    ]
    for text, used, fill in lines:
        draw.text((x, y), text, font=used, fill=fill)
        box = draw.textbbox((0, 0), text, font=used)
        y += (box[3] - box[1]) + int(height * 0.012)

    composed = Image.alpha_composite(photo.convert("RGBA"), overlay)
    return composed.convert("RGB")


def scene_clip(image_path, seconds, size, output):
    width, height = size
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        "-vf",
        f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},"
        f"zoompan=z='min(zoom+0.0007,1.1)':d={seconds * 30}:s={width}x{height}:fps=30,format=yuv420p",
        "-t", str(seconds), "-an", str(output),
    ])


def concat(clips, durations, output):
    inputs = []
    filters = []
    for index, clip in enumerate(clips):
        fade_out = max(durations[index] - 0.7, 0.1)
        inputs += ["-i", str(clip)]
        filters.append(f"[{index}:v]fade=t=in:st=0:d=0.6,fade=t=out:st={fade_out}:d=0.6[v{index}]")
    chain = "".join(f"[v{i}]" for i in range(len(clips)))
    filters.append(f"{chain}concat=n={len(clips)}:v=1:a=0[v]")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[v]", "-r", "30", str(output)])


def add_audio(video, output):
    if MUSIC.exists():
        run([
            "ffmpeg", "-y", "-i", str(video), "-i", str(MUSIC),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart", str(output),
        ])
    else:
        run([
            "ffmpeg", "-y", "-i", str(video),
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(output),
        ])


def scenes():
    formal = ASSETS / "couple-formal.jpeg"
    rings = ASSETS / "rings.jpeg"
    palace = ASSETS / "couple-palace.jpeg"
    payana = ASSETS / "couple-payana.jpeg"
    return [
        (formal, [("শুভ বিবাহ", "bn"), ("A wedding story", "line")], 5),
        (formal, [("The bride", "kicker"), ("Sudeshna", "script"), ("সুদেষ্ণা", "bn")], 6),
        (formal, [("The groom", "kicker"), ("Arkit", "script"), ("অর্কিত", "bn")], 6),
        (rings, [("Parents of the bride", "kicker"), ("Mr. Sukhen Dutta", "line"), ("Mrs. Krishna Dutta", "line"), ("শ্রী সুখেন দত্ত ও শ্রীমতি কৃষ্ণা দত্ত", "bn")], 7),
        (palace, [("Parents of the groom", "kicker"), ("Mr. Swapan Kumar Bhandari", "line"), ("Mrs. Sima Bhandari", "line"), ("শ্রী স্বপন কুমার ভাণ্ডারী ও শ্রীমতি সীমা ভাণ্ডারী", "bn")], 7),
        (rings, [("সস্নেহ নিমন্ত্রণ", "bn"), ("সুদেষ্ণা এবং অর্কিত", "bn"), ("৫ ডিসেম্বর ২০২৬ · শনিবার", "bn"), ("সন্ধ্যা ৭টা হইতে", "bn")], 7),
        (payana, [("Together", "kicker"), ("Sudeshna weds Arkit", "script"), ("5 December 2026, Saturday", "line"), ("7 PM onwards", "kicker")], 7),
        ("venue", None, 8),
        (formal, [("Sudeshna & Arkit", "script"), ("With love and blessings", "kicker")], 6),
    ]


def render(size, output):
    work = Path(tempfile.mkdtemp(prefix="wedding-ecard-"))
    items = scenes()
    clips = []
    durations = []
    for index, (photo, lines, seconds) in enumerate(items):
        frame = work / f"frame-{index:02d}.jpg"
        clip = work / f"clip-{index:02d}.mp4"
        if photo == "venue":
            venue_location_card(size).save(frame, quality=93)
        else:
            card(size, lines, photo).save(frame, quality=93)
        scene_clip(frame, seconds, size, clip)
        clips.append(clip)
        durations.append(seconds)
    silent = work / "silent.mp4"
    concat(clips, durations, silent)
    add_audio(silent, output)
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {output}")


def main():
    if not VENUE_PHOTO.exists():
        raise SystemExit(f"missing venue photo {VENUE_PHOTO}")
    render((1920, 1080), OUT_WIDE)
    render((1080, 1920), OUT_TALL)


if __name__ == "__main__":
    main()
