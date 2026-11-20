#!/usr/bin/env python3
"""Render the 20 November 2026 world-news poster as a fixed 1024x1024 PNG.

Deterministic newspaper front page built with PIL only: no network, no clock,
no randomness — the same run always produces the same bytes. Every fact on
the page comes from the research note (news-image-20261120-research.md);
nothing is invented. Run: python3 gen_poster.py  ->  entry.png (this folder).
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT_FILE = HERE / "entry.png"

PAGE = 1024
EDGE = 42
GUTTER = 20

PAPER = (250, 246, 238)
INK = (18, 18, 18)
MID = (96, 96, 92)
FAINT = (178, 172, 164)
RED = (163, 22, 33)
NAVY = (31, 56, 100)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
_fonts = {}


def typeface(style, size):
    key = (style, size)
    if key not in _fonts:
        filename = {
            "serif": "DejaVuSerif.ttf",
            "serif_b": "DejaVuSerif-Bold.ttf",
            "sans": "DejaVuSans.ttf",
            "sans_b": "DejaVuSans-Bold.ttf",
        }[style]
        _fonts[key] = ImageFont.truetype(str(FONT_DIR / filename), size)
    return _fonts[key]


def split_lines(text, font, width):
    """Greedy word wrap: lines that fit inside width pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if font.getlength(trial) <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def fit(text, font, width, max_lines):
    """Wrap text and clip to max_lines, adding an ellipsis when clipped."""
    lines = split_lines(text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines


def hline(draw, x, y, width, color=INK, weight=2):
    draw.rectangle([x, y, x + width, y + weight - 1], fill=color)


def draw_masthead(draw):
    title = "THE WORLD TODAY"
    font = typeface("serif_b", 58)
    tw = font.getlength(title)
    draw.text(((PAGE - tw) / 2, 26), title, font=font, fill=INK)
    date_font = typeface("sans", 19)
    date = "FRIDAY · 20 NOVEMBER 2026"
    dw = date_font.getlength(date)
    draw.text(((PAGE - dw) / 2, 100), date, font=date_font, fill=MID)
    hline(draw, EDGE, 132, PAGE - 2 * EDGE, INK, 3)
    hline(draw, EDGE, 138, PAGE - 2 * EDGE, FAINT, 1)


def draw_lead(draw):
    x = EDGE
    y = 154
    width = PAGE - 2 * EDGE
    kick = typeface("sans_b", 15)
    draw.text((x, y), "SHENZHEN · THE LEAD", font=kick, fill=RED)
    head = typeface("serif_b", 33)
    headline = "Trump, Xi and Putin sign four-point peace declaration"
    lines = fit(headline, head, width, 2)
    hy = y + 26
    for line in lines:
        draw.text((x, hy), line, font=head, fill=INK)
        hy += 40
    body = typeface("sans", 18)
    text = (
        "The three leaders met in Shenzhen on Thursday, the first trilateral of its kind, "
        "and pledged UN reform, more fuel supply, limits on the ICC and a dialogue on nuclear "
        "risk. The text says nothing of Ukraine, Iran or North Korea — and sets no date for "
        "the nuclear talks."
    )
    by = hy + 6
    for line in fit(text, body, width, 3):
        draw.text((x, by), line, font=body, fill=INK)
        by += 24
    rule_y = by + 6
    hline(draw, EDGE, rule_y, width, INK, 2)
    return rule_y


def draw_card(draw, x, y, width, kicker, headline, body_text):
    hline(draw, x, y, width, FAINT, 1)
    kick = typeface("sans_b", 13)
    draw.text((x, y + 8), kicker, font=kick, fill=RED)
    head = typeface("sans_b", 21)
    hy = y + 30
    for line in fit(headline, head, width, 2):
        draw.text((x, hy), line, font=head, fill=INK)
        hy += 26
    body = typeface("sans", 15)
    by = hy + 4
    for line in fit(body_text, body, width, 4):
        draw.text((x, by), line, font=body, fill=INK)
        by += 20


CARDS = [
    (
        "THE HAGUE · JUSTICE",
        "World court: Myanmar guilty of Rohingya genocide",
        "The ICJ ruled 9–6 that Myanmar committed genocide in 2017 — the first time the "
        "court has held a state responsible. About 10,000 were killed; reparations ordered.",
    ),
    (
        "MARKETS · ASIA",
        "Asia's AI rout: worst week since 2020",
        "Nikkei −4.8%, Taiwan −6.6%, Kospi −5.2% on Friday as doubts over AI spending "
        "deepened. Anthropic's record IPO failed to lift the sector.",
    ),
    (
        "NEW YORK · IPO",
        "Anthropic's $81bn debut: open +34%, close +17%",
        "Shares priced at $83 opened at $111.50 and closed at $97.17 — the largest IPO "
        "ever, ahead of SpaceX's $75bn.",
    ),
    (
        "KYIV · CRIMEA",
        "Bridge war: Kerch hit a third time",
        "Ukraine's Neptune missiles damaged the Kerch rail span; rail traffic halted. "
        "Russia answered overnight, damaging three Kyiv bridges and killing three.",
    ),
    (
        "RIYADH · CONFLICT",
        "Houthi missile damages Saudi wealth-fund tower",
        "A missile hit the Public Investment Fund tower in Riyadh's financial district, "
        "breaking windows on several floors. Saudi defences intercepted others.",
    ),
    (
        "NAIROBI · HEALTH",
        "Kenya discharges its last Ebola patient",
        "Thirty-seven days after the first case, Kenya's outbreak is over — the last "
        "patient went home, a rare piece of good news on a grim day.",
    ),
]

BRIEF = (
    "US Senate rejects Iran war-powers bid 51–48 · Trump pardons Pete Rose · "
    "UK pledges 1,000+ drones for Ukraine · COP31: Africa seeks tripled climate finance · "
    "Bukele registers for third term · Cyclone Xavier tracked near Fiji"
)


def draw_brief(draw, y):
    hline(draw, EDGE, y, PAGE - 2 * EDGE, INK, 2)
    label = typeface("sans_b", 14)
    draw.text((EDGE, y + 10), "IN BRIEF", font=label, fill=RED)
    font = typeface("sans", 14)
    width = PAGE - 2 * EDGE
    by = y + 34
    for line in fit(BRIEF, font, width, 2):
        draw.text((EDGE, by), line, font=font, fill=INK)
        by += 19
    return by


def render():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    lead_end = draw_lead(draw)
    col_w = (PAGE - 2 * EDGE - GUTTER) // 2
    row_y = [lead_end + 14, lead_end + 194, lead_end + 374]
    for i, (kicker, headline, body_text) in enumerate(CARDS):
        col = i % 2
        row = i // 2
        x = EDGE + col * (col_w + GUTTER)
        draw_card(draw, x, row_y[row], col_w, kicker, headline, body_text)
    end = draw_brief(draw, 902)
    foot = typeface("sans", 12)
    note = "Sources: Reuters, BBC, AP, HRW, CNN, WSJ, Le Monde, Morningstar — 20 Nov 2026"
    draw.text((EDGE, end + 8), note, font=foot, fill=MID)
    img.save(OUT_FILE, "PNG")
    print("wrote %s (%dx%d)" % (OUT_FILE, PAGE, PAGE))


if __name__ == "__main__":
    render()
