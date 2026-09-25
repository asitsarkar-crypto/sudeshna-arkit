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
MUSIC = next(
    (
        path
        for path in (
            ASSETS / "wedding-song.mp3",
            ASSETS / "wedding-music.mp3",
        )
        if path.exists()
    ),
    ASSETS / "wedding-song.mp3",
)
OUT_WIDE = ASSETS / "wedding-ecard.mp4"
OUT_TALL = ASSETS / "wedding-ecard-9x16.mp4"


def run(cmd):
    subprocess.run(cmd, check=True)


def load_font(path, size):
    return ImageFont.truetype(str(path if path.exists() else GEORGIA), size)


def cover(image, size):
    width, height = size
    ratio = width / height
    src = image.width / image.height
    if src > ratio:
        new_w = int(image.height * ratio)
        left = (image.width - new_w) // 2
        box = (left, 0, left + new_w, image.height)
    else:
        new_h = int(image.width / ratio)
        top = max(0, int((image.height - new_h) * 0.16))
        box = (0, top, image.width, min(image.height, top + new_h))
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
        (formal, [("The groom", "kicker"), ("Arkit", "script"), ("আরকিত", "bn")], 6),
        (rings, [("Parents of the bride", "kicker"), ("Mr. Sukhen Dutta", "line"), ("Mrs. Krishna Dutta", "line"), ("শ্রী সুখেন দত্ত ও শ্রীমতি কৃষ্ণা দত্ত", "bn")], 7),
        (palace, [("Parents of the groom", "kicker"), ("Mr. Swapan Kumar Bhandari", "line"), ("Mrs. Sima Bhandari", "line"), ("শ্রী স্বপন কুমার ভাণ্ডারী ও শ্রীমতি সীমা ভাণ্ডারী", "bn")], 7),
        (rings, [("সস্নেহ নিমন্ত্রণ", "bn"), ("সুদেষ্ণা এবং আরকিত", "bn"), ("৫ ডিসেম্বর ২০২৬ · শনিবার", "bn"), ("সন্ধ্যা ৭টা হইতে", "bn"), ("ললিতা ব্যাংকোয়েট, কলকাতা", "bn")], 8),
        (payana, [("Wedding invitation", "kicker"), ("Sudeshna weds Arkit", "script"), ("5 December 2026, Saturday", "line"), ("7 PM onwards", "kicker"), ("Lalita Banquet, Kolkata 700009", "kicker")], 8),
        (formal, [("Sudeshna & Arkit", "script"), ("With love and blessings", "kicker")], 6),
    ]


def render(size, output):
    work = Path(tempfile.mkdtemp(prefix="wedding-ecard-"))
    items = scenes()
    clips = []
    for index, (photo, lines, seconds) in enumerate(items):
        frame = work / f"frame-{index:02d}.jpg"
        clip = work / f"clip-{index:02d}.mp4"
        card(size, lines, photo).save(frame, quality=93)
        scene_clip(frame, seconds, size, clip)
        clips.append(clip)
    silent = work / "silent.mp4"
    concat(clips, [item[2] for item in items], silent)
    add_audio(silent, output)
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {output}")


def main():
    render((1920, 1080), OUT_WIDE)


if __name__ == "__main__":
    main()
