"""Voice lines.

Fan-written paraphrases inspired by Ramattra's characterisation. Three moods:

* **omnic**   — the monk: patient, tired, tries to talk you down.
* **nemesis** — the tank who stopped pretending to be patient.
* **special** — festival form: older, amused, and very fond of the two cats.

Short on purpose: a desktop pet should mutter, not monologue.
"""

from __future__ import annotations

import random

FORMS = ("omnic", "nemesis", "special")

LINES = {
    "omnic": {
        "click": [
            "你想说什么？",
            "我在听。慢慢说。",
            "冷静。先把事情说清楚。",
            "别急，我们还活着，这就够了。",
            "我见过更糟的，所以别慌。",
            "耐心是一种武器。",
        ],
        "idle": [
            "和平，从来不是单方面的让步。",
            "沉默也是一种回答。",
            "你们人类总在匆忙，我们也是。",
            "我数过很多次日落，没有一次是重复的。",
            "秩序不是压迫，是呼吸的节奏。",
            "如果没人听，那就说大声一点。",
            "袍子很重，但我背着它走了很久。",
            "今天也要记得喝水。",
        ],
        "transform": ["站起来吧。", "让他们听听我们的声音。"],
        "wake": ["我醒着。", "别担心，我没有真的睡着。"],
        "sleep": ["我打个盹……", "有事再叫我。"],
    },
    "nemesis": {
        "click": [
            "别碰。",
            "说重点。",
            "你最好有一个好理由。",
            "我数到三。",
            "又是你。",
        ],
        "idle": [
            "我受够了忍耐。",
            "苦难不需要翻译。",
            "拳头也是一种语言。",
            "你们怕的不是我，是镜子。",
            "我仍然是我，只是不再客气。",
            "再靠近一点试试。",
        ],
        "transform": ["既然讲道理没用。", "那就换个说法。"],
        "wake": ["谁在吵？", "我醒着。"],
        "sleep": ["别来打扰我。", "三分钟。"],
    },
    "special": {
        "click": [
            "嘘。别吵醒它们。",
            "这套衣服？借来的。",
            "九次日出，九次日落。",
            "你看，它们也在看你。",
            "别摸面具，会掉漆。",
            "节日才穿这个。",
        ],
        "idle": [
            "狐狸会等，等得比人久。",
            "猫比人先学会安静。",
            "别把我当神，我只是一台旧机器。",
            "面具是给别人看的，脸才是给自己的。",
            "它们俩今天心情不错。",
            "风把围巾吹过来了。",
        ],
        "transform": ["换个场合，换身衣服。", "节日到了。"],
        "wake": ["……我没睡，我在算。", "嗯。"],
        "sleep": ["让它们守着就好。", "我闭一会儿眼。"],
        "cat": [
            "喵。",
            "别戳猫。",
            "它比你有耐心。",
            "那只猫是先来的。",
            "轻一点，它戴着兜帽。",
            "喵——（翻译：别烦我）",
        ],
    },
}

GENERIC = ["……", "嗯。"]


def pick(form: str, kind: str, rng: random.Random | None = None) -> str:
    """Return one line for ``form`` and ``kind`` (click/idle/.../cat)."""
    rng = rng or random
    pool = LINES.get(form, {}).get(kind) or LINES["omnic"].get(kind) or GENERIC
    return rng.choice(pool)


def other_form(form: str) -> str:
    """Next form in the carousel: omnic -> nemesis -> special -> omnic."""
    try:
        return FORMS[(FORMS.index(form) + 1) % len(FORMS)]
    except ValueError:
        return FORMS[0]
