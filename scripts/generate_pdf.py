import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "print-card.html"
OUT = ROOT / "assets" / "wedding-invitation.pdf"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def main():
    if not HTML.exists():
        raise SystemExit(f"missing {HTML}")
    if not EDGE.exists():
        raise SystemExit("Microsoft Edge is required to print Bengali-shaped invitation pages")
    html_uri = HTML.resolve().as_uri()
    cmd = [
        str(EDGE),
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-pdf-header-footer",
        "--virtual-time-budget=20000",
        f"--print-to-pdf={OUT.resolve()}",
        html_uri,
    ]
    subprocess.run(cmd, check=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
