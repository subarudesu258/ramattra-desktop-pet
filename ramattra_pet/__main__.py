"""Command line entry point: ``python -m ramattra_pet``.

Flags exist mostly so the app can be smoke-tested from a script:

    python -m ramattra_pet --demo 3          # run three seconds, then quit
    python -m ramattra_pet --selftest        # load every asset, open + close
    python -m ramattra_pet --snapshot out.png --snapshot-delay 1500
"""

from __future__ import annotations

import argparse
import logging
import sys
import traceback
from pathlib import Path

from . import config as config_mod
from .app import VERSION, PetApp, enable_dpi_awareness


def _setup_logging() -> Path:
    log_path = config_mod.data_dir() / "pet.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=str(log_path),
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            encoding="utf-8",
        )
    except OSError:
        pass
    return log_path


def _install_crash_handler(log_path: Path) -> None:
    """With pythonw there is no console, so surface crashes in a message box."""

    def hook(exc_type, exc, tb) -> None:
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        logging.error("unhandled exception:\n%s", text)
        try:
            import tkinter.messagebox as mb

            mb.showerror("Ramattra Pet 崩溃了", f"{exc}\n\n详细日志：{log_path}")
        except Exception:
            pass

    sys.excepthook = hook


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ramattra_pet", description="Ramattra 桌面宠物")
    p.add_argument("--version", action="version", version=f"Ramattra Pet {VERSION}")
    p.add_argument("--reset", action="store_true", help="忘记保存的位置，回到默认角落")
    p.add_argument("--form", choices=("omnic", "nemesis", "special"), help="启动时的形态")
    p.add_argument("--no-topmost", action="store_true", help="不要总在最前")
    p.add_argument("--demo", type=float, metavar="SECONDS", help="运行若干秒后自动退出（自测用）")
    p.add_argument("--selftest", action="store_true", help="加载全部素材后立即退出，返回码表示成败")
    p.add_argument("--snapshot", metavar="PATH", help="截取宠物窗口到 PNG 后退出（需要 Pillow）")
    p.add_argument("--snapshot-delay", type=int, default=1200, metavar="MS")
    p.add_argument("--say", metavar="TEXT", help="启动时先说一句（方便截气泡图）")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    log_path = _setup_logging()
    _install_crash_handler(log_path)

    cfg = config_mod.Config() if args.reset else config_mod.load()
    if args.form:
        cfg.form = args.form
    if args.no_topmost:
        cfg.topmost = False

    enable_dpi_awareness()
    app = PetApp(cfg)

    if args.selftest:
        app.root.update()
        for clip in app.lib.clip_names():
            app.lib.frames(clip)
        logging.info("selftest ok: %d clips", len(app.lib.clip_names()))
        app.root.destroy()
        return 0

    if args.snapshot:
        def grab() -> None:
            try:
                from PIL import ImageGrab

                pad = 8
                boxes = [(app.x, app.y, app.x + app._w, app.y + app._h)]
                if app._bubble.visible:
                    b = app._bubble.win
                    boxes.append((b.winfo_x(), b.winfo_y(), b.winfo_x() + b.winfo_width(), b.winfo_y() + b.winfo_height()))
                x0 = min(b[0] for b in boxes) - pad
                y0 = min(b[1] for b in boxes) - pad
                x1 = max(b[2] for b in boxes) + pad
                y1 = max(b[3] for b in boxes) + pad
                img = ImageGrab.grab(bbox=(x0, y0, x1, y1), all_screens=True)
                Path(args.snapshot).parent.mkdir(parents=True, exist_ok=True)
                img.save(args.snapshot)
                logging.info("snapshot saved to %s (%sx%s)", args.snapshot, img.width, img.height)
            except Exception as exc:  # pragma: no cover - display dependent
                logging.error("snapshot failed: %s", exc)
            finally:
                app.quit()

        app.root.after(args.snapshot_delay, grab)

    if args.say:
        app.root.after(350, lambda: app.say(args.say, 8.0))

    if args.demo:
        app.root.after(int(args.demo * 1000), app.quit)

    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
