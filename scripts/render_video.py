import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
GEORGIA = Path(r"C:\Windows\Fonts\georgia.ttf")
GEORGIA_I = Path(r"C:\Windows\Fonts\georgiai.ttf")
MUSIC = ASSETS / "wedding-song.mp3"
OUT_WIDE = ASSETS / "wedding-ecard.mp4"
OUT_TALL = ASSETS / "wedding-ecard-9x16.mp4"
VENUE_PHOTO = ASSETS / "venue-google-place.jpg"
INK = (26, 14, 12, 236)
IVORY = (247, 241, 232, 255)
ROSE = (232, 196, 176, 255)
GOLD = (199, 146, 108, 255)


def run(cmd):
    subprocess.run(cmd, check=True)


def font(path, size, index=0):
    if path.exists() and path.suffix.lower() == ".ttc":
        return ImageFont.truetype(str(path), size, index=index)
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.truetype(str(GEORGIA), size)


def contain(image, size, fill=(16, 8, 6)):
    canvas = Image.new("RGB", size, fill)
    ratio = min(size[0] / image.width, size[1] / image.height)
    new = image.resize((max(1, int(image.width * ratio)), max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)
    canvas.paste(new, ((size[0] - new.width) // 2, (size[1] - new.height) // 2))
    return canvas


def wrap_draw(draw, text, used, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textbbox((0, 0), trial, font=used)[2] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def side_card(size, photo, lines, motif=None):
    width, height = size
    landscape = width >= height
    image = Image.new("RGB", size, (16, 8, 6))
    if landscape:
        photo_box = (int(width * 0.62), height)
        panel = (int(width * 0.62), 0, width, height)
        text_x = int(width * 0.655)
        text_w = int(width * 0.31)
        text_y = int(height * 0.16)
    else:
        photo_box = (width, int(height * 0.62))
        panel = (0, int(height * 0.62), width, height)
        text_x = int(width * 0.08)
        text_w = int(width * 0.84)
        text_y = int(height * 0.655)

    if photo:
        fitted = contain(ImageEnhance.Contrast(Image.open(photo).convert("RGB")).enhance(1.06), photo_box)
        image.paste(fitted, (0, 0))

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle(panel, fill=INK)
    if landscape:
        draw.line((panel[0], int(height * 0.08), panel[0], int(height * 0.92)), fill=GOLD, width=2)
    else:
        draw.line((int(width * 0.08), panel[1], int(width * 0.92), panel[1]), fill=GOLD, width=2)

    if motif and Path(motif).exists():
        mark = Image.open(motif).convert("RGBA")
        mark.thumbnail((int(min(width, height) * 0.08), int(min(width, height) * 0.08)))
        overlay.alpha_composite(mark, (text_x, text_y - mark.height - 12))

    y = text_y
    for text, kind in lines:
        if kind == "name":
            used = font(GEORGIA_I if GEORGIA_I.exists() else GEORGIA, int(height * (0.048 if landscape else 0.036)))
            fill = IVORY
        elif kind == "kicker":
            used = font(GEORGIA, int(height * 0.02))
            fill = GOLD
            text = text.upper()
        else:
            used = font(GEORGIA, int(height * (0.026 if landscape else 0.022)))
            fill = IVORY
        for part in wrap_draw(draw, text, used, text_w):
            draw.text((text_x, y), part, font=used, fill=fill)
            box = draw.textbbox((0, 0), part, font=used)
            y += (box[3] - box[1]) + int(height * 0.012)
        y += int(height * 0.012)

    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def song_seconds():
    probe = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(MUSIC)],
        text=True,
    ).strip()
    return float(probe)


def scene_clip(image_path, seconds, output):
    fade_out = max(seconds - 0.55, 0.2)
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        "-vf", f"fade=t=in:st=0:d=0.45,fade=t=out:st={fade_out}:d=0.45,format=yuv420p",
        "-t", str(seconds), "-r", "30", "-an", str(output),
    ])


def concat(clips, output):
    listing = output.with_suffix(".txt")
    listing.write_text("".join(f"file '{clip.as_posix()}'\n" for clip in clips), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(output)])


def mux_looped(video, output):
    run([
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", str(video),
        "-i", str(MUSIC),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(output),
    ])


def scenes():
    formal = ASSETS / "couple-formal.jpeg"
    rings = ASSETS / "rings.jpeg"
    palace = ASSETS / "couple-palace.jpeg"
    payana = ASSETS / "couple-payana.jpeg"
    venue = VENUE_PHOTO
    sindur = ASSETS / "ritual-sindur.jpg"
    varmala = ASSETS / "ritual-varmala.jpg"
    kalash = ASSETS / "motif-kalash.png"
    shankha = ASSETS / "motif-shankha.png"
    topor = ASSETS / "motif-topor.png"
    return [
        (formal, kalash, [
            ("A wedding film", "kicker"),
            ("Sudeshna & Arkit", "name"),
            ("Saturday · 5 December 2026", "line"),
        ], 7),
        (formal, None, [
            ("The bride", "kicker"),
            ("Sudeshna", "name"),
        ], 7),
        (formal, topor, [
            ("The groom", "kicker"),
            ("Arkit", "name"),
        ], 7),
        (rings, None, [
            ("Parents of the bride", "kicker"),
            ("Mr. Sukhen Dutta", "line"),
            ("Mrs. Krishna Dutta", "line"),
        ], 8),
        (palace, None, [
            ("Parents of the groom", "kicker"),
            ("Mr. Swapan Kumar Bhandari", "line"),
            ("Mrs. Sima Bhandari", "line"),
        ], 8),
        (rings, kalash, [
            ("With love", "kicker"),
            ("You are invited", "name"),
            ("Saturday · 5 December 2026", "line"),
            ("7 PM onwards", "line"),
        ], 8),
        (payana, None, [
            ("Together", "kicker"),
            ("Sudeshna weds Arkit", "name"),
        ], 7),
        (venue, shankha, [
            ("The wedding place", "kicker"),
            ("Lalita Banquet", "name"),
            ("97, Keshab Chandra Sen Street", "line"),
            ("Kolkata 700009", "line"),
        ], 8),
        (sindur, None, [
            ("Sindur daan", "kicker"),
            ("The sacred vermilion", "line"),
        ], 8),
        (varmala, None, [
            ("Varmala", "kicker"),
            ("Exchange of garlands", "line"),
        ], 8),
        (formal, kalash, [
            ("A blessing", "kicker"),
            ("May these two lives", "line"),
            ("be blessed", "line"),
        ], 8),
        (payana, shankha, [
            ("With love", "kicker"),
            ("We seek your blessings", "line"),
        ], 8),
        (formal, kalash, [
            ("Sudeshna & Arkit", "name"),
            ("With love and blessings", "line"),
        ], 7),
    ]


def render(size, output):
    work = Path(tempfile.mkdtemp(prefix="wedding-ecard-"))
    clips = []
    for index, (photo, motif, lines, seconds) in enumerate(scenes()):
        frame = work / f"frame-{index:02d}.jpg"
        clip = work / f"clip-{index:02d}.mp4"
        side_card(size, photo, lines, motif).save(frame, quality=94)
        scene_clip(frame, seconds, clip)
        clips.append(clip)
    silent = work / "silent.mp4"
    concat(clips, silent)
    mux_looped(silent, output)
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {output}")


def write_qc_frames():
    qa = ASSETS / "qa-frames"
    qa.mkdir(exist_ok=True)
    for index, (photo, motif, lines, _seconds) in enumerate(scenes()):
        path = qa / f"slide-{index:02d}.jpg"
        side_card((1920, 1080), photo, lines, motif).save(path, quality=92)
        print(f"wrote {path}")


def main():
    if not VENUE_PHOTO.exists():
        raise SystemExit(f"missing venue photo {VENUE_PHOTO}")
    if "--qc" in __import__("sys").argv:
        write_qc_frames()
        return
    render((1920, 1080), OUT_WIDE)
    render((1080, 1920), OUT_TALL)
    print("song seconds", song_seconds())


if __name__ == "__main__":
    main()
