"""The pet window: transparency, dragging, animation, menus and speech bubbles.

Windows-specific tricks used here:

* ``wm_attributes("-transparentcolor", ...)`` makes the magenta background of the
  sprite PNG fully transparent *and* click-through, so the pet looks like it is
  sitting on the desktop rather than inside a window.
* ``overrideredirect(True)`` removes the title bar and the taskbar button.
* ``-topmost`` keeps the pet above normal windows (toggleable from the menu).
"""

from __future__ import annotations

import ctypes
import logging
import os
import random
import time
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox

from . import config as config_mod
from . import hotspots, quotes
from .sprites import COLOUR_KEY, SpriteLibrary

log = logging.getLogger(__name__)

VERSION = "1.0.0"

PANEL_BG = "#14101c"
PANEL_FG = "#e6dcff"
ACCENT = "#8c50f0"


@dataclass(frozen=True)
class Clip:
    name: str
    fps: int
    loop: bool


CLIPS: dict[str, dict[str, Clip]] = {
    "omnic": {
        "idle": Clip("omnic_idle", 6, True),
        "blink": Clip("omnic_blink", 9, False),
        "action": Clip("omnic_cast", 11, False),
        "sleep": Clip("omnic_sleep", 2, True),
    },
    "nemesis": {
        "idle": Clip("nemesis_idle", 6, True),
        "blink": Clip("nemesis_blink", 9, False),
        "action": Clip("nemesis_roar", 11, False),
        "sleep": Clip("nemesis_sleep", 2, True),
    },
    "special": {
        "idle": Clip("special_idle", 6, True),
        "blink": Clip("special_blink", 9, False),
        "action": Clip("special_aura", 11, False),
        "sleep": Clip("special_sleep", 2, True),
        "cat": Clip("special_cat", 9, False),
    },
}


def enable_dpi_awareness() -> None:
    """Make Tk work in physical pixels so the sprite stays pixel-perfect."""
    if os.name != "nt":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:  # pragma: no cover - older Windows
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def virtual_screen() -> tuple[int, int, int, int] | None:
    """(x, y, width, height) of the whole virtual desktop, or None if unknown."""
    if os.name != "nt":
        return None
    try:
        u = ctypes.windll.user32
        # SM_XVIRTUALSCREEN, SM_YVIRTUALSCREEN, SM_CXVIRTUALSCREEN, SM_CYVIRTUALSCREEN
        vx, vy, vw, vh = u.GetSystemMetrics(76), u.GetSystemMetrics(77), u.GetSystemMetrics(78), u.GetSystemMetrics(79)
        if vw > 0 and vh > 0:
            return vx, vy, vw, vh
    except Exception:
        pass
    return None


class SpeechBubble:
    """A small dark panel that pops up above the pet and fades away."""

    def __init__(self, master: tk.Misc) -> None:
        self.win = tk.Toplevel(master)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.wm_attributes("-topmost", True)
        self.win.configure(bg=PANEL_BG)
        try:
            self.win.wm_attributes("-alpha", 0.0)
        except tk.TclError:
            pass

        self.frame = tk.Frame(self.win, bg=PANEL_BG, bd=0, highlightthickness=1, highlightbackground=ACCENT)
        self.frame.pack(fill="both", expand=True)
        self.label = tk.Label(
            self.frame,
            text="",
            bg=PANEL_BG,
            fg=PANEL_FG,
            font=("Microsoft YaHei UI", 9),
            justify="left",
            wraplength=196,
            padx=11,
            pady=8,
        )
        self.label.pack()

        self._hide_job: str | None = None
        self._fade_job: str | None = None
        self.visible = False

    # -- geometry ----------------------------------------------------------
    def place_above(self, pet_x: int, pet_y: int, pet_w: int) -> None:
        self.win.update_idletasks()
        w = max(self.win.winfo_reqwidth(), 60)
        h = self.win.winfo_reqheight()
        x = pet_x + pet_w // 2 - w // 2
        y = pet_y - h - 8
        box = virtual_screen()
        if box:
            vx, vy, vw, vh = box
            x = max(vx + 2, min(vx + vw - w - 2, x))
            y = max(vy + 2, min(vy + vh - h - 2, y))
        self.win.geometry(f"+{x}+{y}")

    # -- lifecycle ---------------------------------------------------------
    def show(self, text: str, pet_x: int, pet_y: int, pet_w: int, seconds: float = 3.2) -> None:
        if not text:
            return
        self._cancel()
        self.label.configure(text=text)
        self.place_above(pet_x, pet_y, pet_w)
        self.win.deiconify()
        self.win.lift()
        self.visible = True
        self._fade(0.0, 0.95)
        delay = int(max(1.2, seconds + len(text) * 0.045) * 1000)
        self._hide_job = self.win.after(delay, self.hide)

    def _fade(self, start: float, end: float, steps: int = 5) -> None:
        try:
            self.win.wm_attributes("-alpha", start)
        except tk.TclError:
            return

        def step(i: int = 0) -> None:
            if i > steps:
                self._fade_job = None
                return
            value = start + (end - start) * (i / steps)
            try:
                self.win.wm_attributes("-alpha", value)
            except tk.TclError:
                return
            self._fade_job = self.win.after(16, lambda: step(i + 1))

        step()

    def _cancel(self) -> None:
        for job in (self._hide_job, self._fade_job):
            if job:
                try:
                    self.win.after_cancel(job)
                except tk.TclError:
                    pass
        self._hide_job = self._fade_job = None

    def hide(self) -> None:
        self._cancel()
        self.visible = False
        self.win.withdraw()


class PetApp:
    """Owns the window, the animation clock and the interaction state machine."""

    def __init__(self, cfg: config_mod.Config) -> None:
        self.cfg = cfg
        self.rng = random.Random()

        self.root = tk.Tk()
        self.root.title("Ramattra Pet")
        self.root.overrideredirect(True)
        self.root.configure(bg=COLOUR_KEY)
        self.root.wm_attributes("-transparentcolor", COLOUR_KEY)
        self.root.wm_attributes("-topmost", bool(cfg.topmost))

        self.lib = SpriteLibrary(master=self.root)
        self.label = tk.Label(self.root, bd=0, highlightthickness=0, bg=COLOUR_KEY, cursor="hand2")
        self.label.pack()

        self.form = cfg.form
        self.x = self.y = 0
        self._w = self._h = 0
        self._sleeping = False
        self._drag: dict | None = None
        self._moved = False
        self._click_job: str | None = None
        self._anim_job: str | None = None
        self._blink_job: str | None = None
        self._talk_job: str | None = None
        self._nap_job: str | None = None
        self._on_end = None
        self._frames: list[tk.PhotoImage] = []
        self._idx = 0
        self._fps = 6
        self._loop = True
        self._scale = 3          # sprite upscale, refreshed from the manifest
        self._hot: str | None = None
        self._last_interaction = time.monotonic()
        self._bubble = SpeechBubble(self.root)

        self._place_initial()
        self._bind_events()
        self._play("idle")
        self._schedule_blink()
        self._schedule_talk()
        self._watch_nap()

    # ------------------------------------------------------------------
    # placement
    # ------------------------------------------------------------------
    def _place_initial(self) -> None:
        self.root.update_idletasks()
        w, h = self.lib.size(CLIPS[self.form]["idle"].name)
        if self.cfg.x is None or self.cfg.y is None:
            box = virtual_screen() or (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
            vx, vy, vw, vh = box
            x = vx + vw - w - 90
            y = vy + vh - h - 70
        else:
            x, y = self.cfg.x, self.cfg.y
        self._place(w, h, x, y)

    def _clamp(self, x: int, y: int, w: int, h: int) -> tuple[int, int]:
        box = virtual_screen() or (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        vx, vy, vw, vh = box
        x = max(vx, min(vx + vw - w, x))
        y = max(vy, min(vy + vh - h, y))
        return x, y

    def _place(self, w: int, h: int, x: int, y: int) -> None:
        x, y = self._clamp(x, y, w, h)
        self.x, self.y, self._w, self._h = x, y, w, h
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        if self._bubble.visible:
            self._bubble.place_above(self.x, self.y, self._w)

    def _move_to(self, x: int, y: int) -> None:
        x, y = self._clamp(x, y, self._w, self._h)
        self.x, self.y = x, y
        self.root.geometry(f"+{x}+{y}")
        if self._bubble.visible:
            self._bubble.place_above(self.x, self.y, self._w)

    # ------------------------------------------------------------------
    # animation
    # ------------------------------------------------------------------
    def _play(self, key: str, on_end=None) -> None:
        clip = CLIPS[self.form][key]
        frames = self.lib.frames(clip.name)
        w, h = self.lib.size(clip.name)
        self._scale = self.lib.scale(clip.name)
        changed_size = (w, h) != (self._w, self._h)
        self._frames, self._idx = frames, 0
        self._fps, self._loop, self._on_end = clip.fps, clip.loop, on_end
        self.label.configure(image=frames[0])
        if changed_size:
            # keep the feet planted when the sprite changes size
            anchor_x = self.x + self._w // 2
            anchor_y = self.y + self._h
            self._place(w, h, anchor_x - w // 2, anchor_y - h)
        self._restart_anim()

    def _restart_anim(self) -> None:
        if self._anim_job:
            try:
                self.root.after_cancel(self._anim_job)
            except tk.TclError:
                pass
        self._anim_job = self.root.after(max(30, int(1000 / self._fps)), self._tick_anim)

    def _tick_anim(self) -> None:
        self._anim_job = None
        n = len(self._frames)
        if self._loop:
            self._idx = (self._idx + 1) % n
        elif self._idx + 1 < n:
            self._idx += 1
        else:
            callback, self._on_end = self._on_end, None
            if callback:
                callback()
            return
        self.label.configure(image=self._frames[self._idx])
        self._anim_job = self.root.after(max(30, int(1000 / self._fps)), self._tick_anim)

    def _go_idle(self) -> None:
        self._play("idle")

    def _blink(self) -> None:
        if self._sleeping or self._drag:
            return
        self._play("blink", on_end=self._go_idle)

    def _schedule_blink(self) -> None:
        self._blink_job = self.root.after(self.rng.randint(4000, 9000), self._auto_blink)

    def _auto_blink(self) -> None:
        self._blink()
        self._schedule_blink()

    # ------------------------------------------------------------------
    # speech
    # ------------------------------------------------------------------
    def say(self, text: str, seconds: float | None = None) -> None:
        self._bubble.show(
            text,
            self.x,
            self.y,
            self._w,
            seconds if seconds is not None else self.cfg.bubble_seconds,
        )

    def say_something(self, kind: str = "idle") -> None:
        self.say(quotes.pick(self.form, kind, self.rng))
        self._last_interaction = time.monotonic()

    def _schedule_talk(self) -> None:
        delay = self.rng.randint(self.cfg.idle_talk_min, self.cfg.idle_talk_max) * 1000
        self._talk_job = self.root.after(delay, self._auto_talk)

    def _auto_talk(self) -> None:
        if not self._sleeping and not self._drag and not self._bubble.visible:
            self.say_something("idle")
        self._schedule_talk()

    # ------------------------------------------------------------------
    # sleep / wake
    # ------------------------------------------------------------------
    def _watch_nap(self) -> None:
        idle_for = time.monotonic() - self._last_interaction
        if not self._sleeping and idle_for > self.cfg.idle_sleep_seconds and not self._drag:
            self.nap()
        self._nap_job = self.root.after(5000, self._watch_nap)

    def nap(self, announce: bool = True) -> None:
        if self._sleeping:
            return
        self._sleeping = True
        self._play("sleep")
        if announce and not self.cfg.muted:
            self.say(quotes.pick(self.form, "sleep", self.rng), 2.4)

    def wake(self, announce: bool = False) -> None:
        if not self._sleeping:
            return
        self._sleeping = False
        self._play("idle")
        self._last_interaction = time.monotonic()
        if announce:
            self.say(quotes.pick(self.form, "wake", self.rng), 2.2)

    def toggle_sleep(self) -> None:
        if self._sleeping:
            self.wake(announce=True)
        else:
            self.nap()

    # ------------------------------------------------------------------
    # interaction
    # ------------------------------------------------------------------
    def _bind_events(self) -> None:
        self.label.bind("<ButtonPress-1>", self._on_press)
        self.label.bind("<B1-Motion>", self._on_drag)
        self.label.bind("<ButtonRelease-1>", self._on_release)
        self.label.bind("<Double-Button-1>", self._on_double_click)
        self.label.bind("<Button-3>", self._on_menu)

    def _on_press(self, event: tk.Event) -> None:
        self._drag = {"sx": event.x_root, "sy": event.y_root, "wx": self.x, "wy": self.y}
        self._moved = False
        self._hot = hotspots.hit(self.form, event.x // self._scale, event.y // self._scale)
        self._last_interaction = time.monotonic()

    def _on_drag(self, event: tk.Event) -> None:
        if not self._drag:
            return
        dx = event.x_root - self._drag["sx"]
        dy = event.y_root - self._drag["sy"]
        if abs(dx) > 3 or abs(dy) > 3:
            self._moved = True
        self._move_to(self._drag["wx"] + dx, self._drag["wy"] + dy)

    def _on_release(self, event: tk.Event) -> None:
        dragged = self._moved
        self._drag = None
        self._moved = False
        self._last_interaction = time.monotonic()
        if dragged:
            self.cfg.x, self.cfg.y = self.x, self.y
            self._save_quietly()
            if self._sleeping:
                self.wake()
            return
        # delay so a double-click can cancel the single-click reaction
        self._click_job = self.root.after(260, self._single_click)

    def _single_click(self) -> None:
        self._click_job = None
        hot, self._hot = self._hot, None
        if self._sleeping:
            self.wake(announce=True)
            return
        if hot and self.form == "special":
            # poking a cat gets a cat reaction, not a Ramattra one
            self._play("cat", on_end=self._go_idle)
            self.say(quotes.pick("special", "cat", self.rng))
            return
        self._play("action", on_end=self._go_idle)
        self.say_something("click")

    def _on_double_click(self, event: tk.Event) -> None:
        if self._click_job:
            try:
                self.root.after_cancel(self._click_job)
            except tk.TclError:
                pass
            self._click_job = None
        if self._sleeping:
            self.wake()
        self.set_form(quotes.other_form(self.form))

    def _on_menu(self, event: tk.Event) -> None:
        self._last_interaction = time.monotonic()
        menu = self._build_menu()
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _build_menu(self) -> tk.Menu:
        menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=PANEL_BG,
            fg=PANEL_FG,
            activebackground=ACCENT,
            activeforeground="#ffffff",
            bd=0,
            font=("Microsoft YaHei UI", 9),
        )
        menu.add_command(label="说句话", command=lambda: self.say_something("click"))
        menu.add_separator()
        labels = {"omnic": "◈ Omnic 形态", "nemesis": "◈ Nemesis 形态", "special": "◈ 特殊形态 (九尾)"}
        for form in quotes.FORMS:
            menu.add_command(
                label=labels[form] + ("  ✓" if self.form == form else ""),
                command=lambda f=form: self.set_form(f),
            )
        menu.add_separator()
        menu.add_command(label="叫醒它" if self._sleeping else "让它打个盹", command=self.toggle_sleep)
        self._topmost_var = tk.BooleanVar(value=bool(self.cfg.topmost))
        menu.add_checkbutton(label="总在最前", variable=self._topmost_var, command=self._toggle_topmost)
        menu.add_separator()
        menu.add_command(label="关于…", command=self._about)
        menu.add_command(label="退出", command=self.quit)
        return menu

    def _toggle_topmost(self) -> None:
        self.cfg.topmost = bool(self._topmost_var.get())
        self.root.wm_attributes("-topmost", self.cfg.topmost)
        self._save_quietly()

    def _about(self) -> None:
        messagebox.showinfo(
            "Ramattra Pet",
            f"Ramattra 桌宠 v{VERSION}\n\n"
            "单击：说句话 · 双击：切换形态（Omnic → Nemesis → 特殊形态）\n"
            "拖拽：移动 · 右键：菜单\n"
            "特殊形态下点肩上那两只猫，它们会理你。\n\n"
            "纯标准库 + tkinter，精灵图由 tools/gen_sprites.py 生成。\n"
            "同人作品，与 Blizzard 无关。",
            parent=self.root,
        )

    # ------------------------------------------------------------------
    # forms
    # ------------------------------------------------------------------
    def set_form(self, form: str, announce: bool = True) -> None:
        if form not in CLIPS:
            form = "omnic"
        was_sleeping = self._sleeping
        self.form = form
        self.cfg.form = form
        self._play("sleep" if was_sleeping else "idle")
        if announce:
            self.say(quotes.pick(form, "transform", self.rng), 2.4)
        self._save_quietly()

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------
    def _save_quietly(self) -> None:
        try:
            config_mod.save(self.cfg)
        except OSError as exc:  # pragma: no cover - disk full / permissions
            log.warning("could not save config: %s", exc)

    def quit(self) -> None:
        self.cfg.x, self.cfg.y = self.x, self.y
        self._save_quietly()
        for job in (self._anim_job, self._blink_job, self._talk_job, self._nap_job, self._click_job):
            if job:
                try:
                    self.root.after_cancel(job)
                except tk.TclError:
                    pass
        self._bubble.hide()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
