"""Compose the README preview images (fake desktop with the real sprites).

The sprites and the bubble here are the same assets and colours the app uses;
only the wallpaper is synthetic, so the screenshots look tidy instead of showing
whatever is on the author's desktop.

Usage:  python tools/mock_desktop.py
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DOCS = ROOT / "docs"

KEY = (255, 0, 254)
PANEL = (20, 16, 28)
BORDER = (140, 80, 240)
TEXT = (230, 220, 255)
MUTED = (150, 140, 175)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for name in (("msyhbd.ttc" if bold else "msyh.ttc"), "segoeui.ttf"):
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def sprite(name: str) -> Image.Image:
    img = Image.open(ASSETS / name).convert("RGB")
    out = img.convert("RGBA")
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            if px[x, y][:3] == KEY:
                px[x, y] = (0, 0, 0, 0)
    return out


def wallpaper(w: int, h: int) -> Image.Image:
    bg = Image.new("RGB", (w, h), (10, 9, 16))
    d = ImageDraw.Draw(bg)
    for y in range(h):
        t = y / h
        d.line((0, y, w, y), fill=(int(22 - 10 * t), int(19 - 8 * t), int(34 - 14 * t)))
    # violet glow behind the pet
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((w - 520, h - 520, w + 120, h + 120), fill=(46, 22, 92))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    bg = Image.blend(bg, Image.new("RGB", (w, h), (12, 10, 18)), 0.0)
    bg = Image.composite(glow, bg, glow.convert("L").point(lambda v: min(255, v * 3)))
    # faint dot grid
    d = ImageDraw.Draw(bg)
    for y in range(0, h, 32):
        for x in range(0, w, 32):
            d.point((x, y), fill=(38, 34, 52))
    return bg


def shadow(w: int, h: int = 26) -> Image.Image:
    s = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.ellipse((4, 4, w - 4, h - 4), fill=(0, 0, 0, 150))
    return s.filter(ImageFilter.GaussianBlur(7))


def wrap_px(text: str, fnt: ImageFont.FreeTypeFont, max_px: int) -> list[str]:
    """Character-wise wrap that measures real glyph widths (CJK is double-wide)."""
    lines: list[str] = []
    current = ""
    for ch in text:
        if not current or fnt.getlength(current + ch) <= max_px:
            current += ch
        else:
            lines.append(current)
            current = ch
    if current:
        lines.append(current)
    return lines


def bubble(text: str, max_width: int = 190) -> Image.Image:
    body = font(15)
    lines = wrap_px(text, body, max_width)
    pad_x, pad_y, gap = 13, 10, 5
    line_h = 21
    w = max(body.getlength(line) for line in lines) + pad_x * 2
    h = line_h * len(lines) + pad_y * 2
    img = Image.new("RGBA", (int(w) + 4, int(h) + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((1, 1, w + 2, h + 2), radius=9, fill=PANEL + (235,), outline=BORDER + (255,), width=1)
    for i, line in enumerate(lines):
        d.text((pad_x + 1, pad_y + i * line_h), line, font=body, fill=TEXT)
    return img


def compose(form: str, line: str, out: Path) -> Path:
    W, H = 960, 600
    canvas = wallpaper(W, H).convert("RGBA")

    clip = {"omnic": "omnic/omnic_idle_2.png",
            "nemesis": "nemesis/nemesis_idle_2.png",
            "special": "special/special_idle_2.png"}[form]
    body = sprite(clip)
    scale = 1.25 if form != "special" else 1.05
    body = body.resize((int(body.width * scale), int(body.height * scale)), Image.NEAREST)

    feet_x, feet_y = W - 300, H - 66
    x = feet_x - body.width // 2
    y = feet_y - body.height

    sh = shadow(int(body.width * 0.72))
    canvas.alpha_composite(sh, (feet_x - sh.width // 2, feet_y - sh.height // 2 + 6))
    canvas.alpha_composite(body, (x, y))

    b = bubble(line)
    bx = feet_x - b.width // 2
    by = y - b.height - 12
    canvas.alpha_composite(b, (max(20, min(W - b.width - 20, bx)), max(20, by)))

    d = ImageDraw.Draw(canvas)

    # a hint of a taskbar so the image reads as "sitting on the desktop"
    bar_h = 46
    canvas.alpha_composite(Image.new("RGBA", (W, bar_h), (12, 10, 18, 210)), (0, H - bar_h))
    d.line((0, H - bar_h, W, H - bar_h), fill=(46, 40, 62, 255))
    for i in range(4):
        ix = 24 + i * 38
        d.rounded_rectangle((ix, H - bar_h + 13, ix + 22, H - bar_h + 33), radius=5, outline=(70, 62, 92), width=1)
    d.text((W - 78, H - bar_h + 14), "20:24", font=font(12), fill=(120, 112, 145))

    title = {"omnic": "Ramattra 桌宠", "nemesis": "Ramattra 桌宠 · Nemesis",
             "special": "Ramattra 桌宠 · 特殊形态"}[form]
    d.text((44, H - 104), title, font=font(26, bold=True), fill=(238, 232, 255))
    d.text((46, H - 66), "纯 tkinter · 零第三方依赖 · 颜色键真透明悬浮", font=font(14), fill=MUTED)
    d.text((W - 150, H - 60), "v1.0.0", font=font(13), fill=(96, 88, 122))

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out)
    return out


def forms(out: Path) -> Path:
    W, H = 940, 430
    canvas = wallpaper(W, H).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    pair = [
        ("omnic/omnic_idle_2.png", "Omnic", "权杖 · 米色兜帽 · 说教", 1.1),
        ("nemesis/nemesis_idle_2.png", "Nemesis", "青铜护肩 · 紫宝石 · 没耐心", 1.1),
        ("special/special_idle_2.png", "特殊形态", "九点面具 · 两只猫 · 节日", 0.92),
    ]
    slot = W // 3
    for i, (path, label, sub, zoom) in enumerate(pair):
        body = sprite(path)
        body = body.resize((int(body.width * zoom), int(body.height * zoom)), Image.NEAREST)
        cx = slot * i + slot // 2
        feet_y = H - 92
        sh = shadow(int(body.width * 0.7))
        canvas.alpha_composite(sh, (cx - sh.width // 2, feet_y - 14))
        canvas.alpha_composite(body, (cx - body.width // 2, feet_y - body.height))
        d.text((cx - 34, feet_y + 12), label, font=font(17, bold=True), fill=(236, 230, 255))
        d.text((cx - 74, feet_y + 40), sub, font=font(12), fill=MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out)
    return out


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    print(compose("omnic", "和平，从来不是单方面的让步。", DOCS / "preview.png"))
    print(compose("nemesis", "我受够了忍耐。", DOCS / "preview-nemesis.png"))
    print(compose("special", "它们俩今天心情不错。", DOCS / "preview-special.png"))
    print(forms(DOCS / "forms.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
