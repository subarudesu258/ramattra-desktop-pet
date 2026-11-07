"""Render the sprite sheet and the per-frame PNGs used by the app.

Usage:
    python tools/gen_sprites.py            # write assets/ + assets/preview/
    python tools/gen_sprites.py --preview  # only refresh the preview images
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PREVIEW = ASSETS / "preview"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art  # noqa: E402

SCALE = 3  # sprites are authored at 1:1 and shown at 3x
IDLE_FRAMES = 8
BOB = (0, 0, 1, 1, 1, 0, 0, 0)


def pulse(i: int, frames: int = IDLE_FRAMES) -> float:
    """Triangle wave 0.55 -> 1.0, used for the energy glow."""
    phase = (i % frames) / frames
    return 0.55 + 0.45 * (1 - abs(phase * 2 - 1))


def omnic_frames() -> dict[str, list[Image.Image]]:
    return {
        "omnic_idle": [art.draw_omnic(glow=pulse(i), bob=BOB[i]) for i in range(IDLE_FRAMES)],
        "omnic_blink": [
            art.draw_omnic(glow=0.75, eye_off=True),
            art.draw_omnic(glow=0.75, eye_off=True),
        ],
        "omnic_cast": [
            art.draw_omnic(glow=0.95, cast=1),
            art.draw_omnic(glow=1.0, cast=2),
            art.draw_omnic(glow=1.0, cast=3),
            art.draw_omnic(glow=1.0, cast=2),
            art.draw_omnic(glow=0.9, cast=1),
        ],
        "omnic_sleep": [
            art.draw_omnic(glow=0.3, bob=1, eye_off=True),
            art.draw_omnic(glow=0.22, bob=1, eye_off=True),
            art.draw_omnic(glow=0.3, bob=0, eye_off=True),
            art.draw_omnic(glow=0.22, bob=0, eye_off=True),
        ],
    }


def nemesis_frames() -> dict[str, list[Image.Image]]:
    return {
        "nemesis_idle": [art.draw_nemesis(glow=pulse(i), bob=BOB[i]) for i in range(IDLE_FRAMES)],
        "nemesis_blink": [
            art.draw_nemesis(glow=0.75, eye_off=True),
            art.draw_nemesis(glow=0.75, eye_off=True),
        ],
        "nemesis_roar": [
            art.draw_nemesis(glow=0.95, roar=1),
            art.draw_nemesis(glow=1.0, roar=2),
            art.draw_nemesis(glow=1.0, roar=3),
            art.draw_nemesis(glow=1.0, roar=2),
            art.draw_nemesis(glow=0.9, roar=1),
        ],
        "nemesis_sleep": [
            art.draw_nemesis(glow=0.3, bob=1, eye_off=True),
            art.draw_nemesis(glow=0.22, bob=1, eye_off=True),
            art.draw_nemesis(glow=0.3, bob=0, eye_off=True),
            art.draw_nemesis(glow=0.22, bob=0, eye_off=True),
        ],
    }


def special_frames() -> dict[str, list[Image.Image]]:
    return {
        "special_idle": [
            art.draw_special(glow=pulse(i), bob=BOB[i], cat_blink=(i in (3, 4)))
            for i in range(IDLE_FRAMES)
        ],
        "special_blink": [
            art.draw_special(glow=0.75, eye_off=True),
            art.draw_special(glow=0.75, eye_off=True),
        ],
        "special_aura": [
            art.draw_special(glow=0.95, aura=1),
            art.draw_special(glow=1.0, aura=2),
            art.draw_special(glow=1.0, aura=3),
            art.draw_special(glow=1.0, aura=2),
            art.draw_special(glow=0.9, aura=1),
        ],
        "special_cat": [
            art.draw_special(glow=1.0, cat_blink=False),
            art.draw_special(glow=1.0, cat_blink=True),
            art.draw_special(glow=1.0, cat_blink=False),
        ],
        "special_sleep": [
            art.draw_special(glow=0.3, bob=1, eye_off=True),
            art.draw_special(glow=0.22, bob=1, eye_off=True),
            art.draw_special(glow=0.3, bob=0, eye_off=True),
            art.draw_special(glow=0.22, bob=0, eye_off=True),
        ],
    }


def write_frames(frames: dict[str, list[Image.Image]]) -> dict[str, dict]:
    manifest: dict[str, dict] = {}
    for clip, imgs in frames.items():
        out_dir = ASSETS / clip.split("_")[0]
        out_dir.mkdir(parents=True, exist_ok=True)
        names = []
        for i, img in enumerate(imgs):
            name = f"{clip}_{i}.png"
            img.resize((img.width * SCALE, img.height * SCALE), Image.NEAREST).save(out_dir / name)
            names.append(name)
        manifest[clip] = {
            "dir": out_dir.name,
            "frames": names,
            "size": [imgs[0].width * SCALE, imgs[0].height * SCALE],
            "scale": SCALE,
        }
    return manifest


def _flatten(img: Image.Image, bg: tuple[int, int, int]) -> Image.Image:
    """Replace the colour-key magenta with ``bg`` so previews look like a desktop."""
    out = Image.new("RGB", img.size, bg)
    src = img.load()
    dst = out.load()
    for yy in range(img.height):
        for xx in range(img.width):
            if src[xx, yy] != art.TRANSPARENT:
                dst[xx, yy] = src[xx, yy]
    return out


def write_contact_sheet(frames: dict[str, list[Image.Image]]) -> Path:
    """One big preview sheet so humans (and agents) can eyeball the art."""
    PREVIEW.mkdir(parents=True, exist_ok=True)
    scale = 2
    pad, label_h = 14, 16
    rows = list(frames.items())
    cell_w = max(sum(im.width * scale + 10 for im in imgs) for _, imgs in rows)
    width = cell_w + pad * 2
    height = pad + sum(imgs[0].height * scale + label_h + 12 for _, imgs in rows) + pad

    sheet = Image.new("RGB", (width, height), (22, 20, 28))
    d = ImageDraw.Draw(sheet)
    for yy in range(0, height, 16):
        for xx in range(0, width, 16):
            if (xx // 16 + yy // 16) % 2 == 0:
                d.rectangle((xx, yy, xx + 15, yy + 15), fill=(30, 28, 38))

    y = pad
    for clip, imgs in rows:
        d.text((pad, y), f"{clip}   ({len(imgs)} frames)", fill=(214, 200, 245))
        y += label_h
        x = pad
        for img in imgs:
            big = _flatten(img, sheet.getpixel((x, y))).resize((img.width * scale, img.height * scale), Image.NEAREST)
            sheet.paste(big, (x, y))
            x += big.width + 10
        y += imgs[0].height * scale + 12

    path = PREVIEW / "sprite-sheet.png"
    sheet.save(path)
    return path


def write_zoom(frames: dict[str, list[Image.Image]]) -> list[Path]:
    """Big 8x renders of one frame per form, for close-up review."""
    PREVIEW.mkdir(parents=True, exist_ok=True)
    out = []
    for clip in ("omnic_idle", "nemesis_idle", "special_idle"):
        img = frames[clip][2]
        big = _flatten(img, (24, 22, 30)).resize((img.width * 8, img.height * 8), Image.NEAREST)
        path = PREVIEW / f"zoom-{clip.split('_')[0]}.png"
        big.save(path)
        out.append(path)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="only regenerate the preview images")
    args = ap.parse_args()

    frames = {**omnic_frames(), **nemesis_frames(), **special_frames()}
    if not args.preview:
        ASSETS.mkdir(parents=True, exist_ok=True)
        manifest = write_frames(frames)
        (ASSETS / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"wrote {sum(len(v) for v in frames.values())} frames")
    print(write_contact_sheet(frames))
    for p in write_zoom(frames):
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
