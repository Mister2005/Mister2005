"""Self-hosted hero banner for the README.

Replaces the old typing-SVG badge, which pointed at
readme-typing-svg.herokuapp.com - a host that stopped serving after Heroku
retired free dynos in Nov 2022. This generator produces the same "cycling
subtitle" effect with a plain CSS animation, self-hosted, so it can't rot the
same way.

Usage:
    python tools/render_hero.py
Outputs: assets/hero-light.svg, assets/hero-dark.svg
"""

from __future__ import annotations

import os

from html import escape as _xml_escape

from common import FONT_STACK, svg_wrapper, write_pair

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

WIDTH = 780
HEIGHT = 180

SUBTITLES = [
    "AI & Data Science Student",
    "Machine Learning Enthusiast",
    "Data Scientist",
    "Python Developer",
]
STEP_SECONDS = 2.6
TOTAL_SECONDS = STEP_SECONDS * len(SUBTITLES)


def ridge_path() -> str:
    """A low-amplitude ridge line echoing the mountain photo, along the bottom."""
    points = [
        (0, 150), (60, 130), (120, 142), (180, 108), (240, 122),
        (300, 96), (360, 118), (420, 90), (480, 112), (540, 100),
        (600, 124), (660, 104), (720, 128), (780, 116),
    ]
    d = f"M{points[0][0]},{HEIGHT} L{points[0][0]},{points[0][1]} "
    d += " ".join(f"L{x},{y}" for x, y in points[1:])
    d += f" L{points[-1][0]},{HEIGHT} Z"
    return d


def subtitle_spans(dark: bool) -> str:
    color = "#8b949e" if dark else "#57606a"
    spans = []
    for i, text in enumerate(SUBTITLES):
        delay = round(i * STEP_SECONDS, 2)
        spans.append(
            f'<text x="20" y="118" font-family="{FONT_STACK}" font-size="20" '
            f'fill="{color}" class="sub" style="animation-delay:{delay}s">'
            f"{_xml_escape(text)}</text>"
        )
    return "".join(spans)


def render(*, dark: bool) -> str:
    bg = "#0d1117" if dark else "#ffffff"
    ridge_fill = "#1f2733" if dark else "#dbe4ee"
    grad_stops = (
        '<stop offset="0%" stop-color="#58a6ff"/>'
        '<stop offset="55%" stop-color="#79c0ff"/>'
        '<stop offset="100%" stop-color="#a5d6ff"/>'
        if dark
        else '<stop offset="0%" stop-color="#0969da"/>'
        '<stop offset="55%" stop-color="#218bff"/>'
        '<stop offset="100%" stop-color="#54aeff"/>'
    )

    body = f"""
    <defs>
      <linearGradient id="nameGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        {grad_stops}
      </linearGradient>
    </defs>
    <path d="{ridge_path()}" fill="{ridge_fill}" opacity="0.6"/>
    <text x="20" y="72" font-family="{FONT_STACK}" font-size="42" font-weight="700"
          fill="url(#nameGrad)">Hi, I&#39;m Varun Gupta</text>
    <g>{subtitle_spans(dark)}</g>
    <style>
      .sub {{
        opacity: 0;
        animation-name: cycle;
        animation-duration: {TOTAL_SECONDS}s;
        animation-iteration-count: infinite;
        animation-timing-function: ease-in-out;
      }}
      @keyframes cycle {{
        0% {{ opacity: 0; }}
        4% {{ opacity: 1; }}
        {round(100 / len(SUBTITLES) - 4, 1)}% {{ opacity: 1; }}
        {round(100 / len(SUBTITLES), 1)}% {{ opacity: 0; }}
        100% {{ opacity: 0; }}
      }}
    </style>
    """
    return svg_wrapper(WIDTH, HEIGHT, body, bg=bg, title="Varun Gupta")


def main():
    light_svg = render(dark=False)
    dark_svg = render(dark=True)
    light_path, dark_path = write_pair("hero", light_svg, dark_svg, ASSETS_DIR)
    for p in (light_path, dark_path):
        print(f"wrote {p} ({os.path.getsize(p)} bytes)")


if __name__ == "__main__":
    main()
