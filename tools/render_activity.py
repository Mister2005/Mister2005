"""Render a 'training curve' styled activity panel from real GitHub data.

Pulls two things from the public GitHub API (no auth needed for a personal
profile at this request volume - 60 req/hour unauthenticated, or 1000/hour
with the Actions-provided GITHUB_TOKEN):

  - GET /users/<user>/events/public   -> commit-ish push events per day,
    last 90 days (that endpoint only returns ~300 events / ~90 days deep,
    which is why the window is capped there).
  - GET /users/<user>/repos           -> primary language per repo, to
    build a language-mix bar.

The panel is drawn to look like an ML training-loss plot (line + soft fill),
because that's the running visual joke of this profile - but the axis label
says exactly what the number is ("push events - last 90 days"), never
"loss" or anything relabelled to sound like something it isn't.

If the events feed comes back thin (new account, mostly-private activity),
the commit curve is dropped and only the language-mix bar is drawn, rather
than padding the curve with invented numbers.

Usage:
    python tools/render_activity.py --user Mister2005
Outputs: assets/activity-light.svg, assets/activity-dark.svg
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import os
import urllib.error
import urllib.request

from common import FONT_STACK, svg_wrapper, write_pair

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

WIDTH = 780
HEIGHT = 320
API_ROOT = "https://api.github.com"

LANGUAGE_COLORS = {
    "Python": "#3572A5",
    "Jupyter Notebook": "#DA5B0B",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Java": "#b07219",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Shell": "#89e051",
    "SQL": "#e38c00",
    "C++": "#f34b7d",
}
DEFAULT_LANG_COLOR = "#8b949e"


def _get_json(url: str, token: str | None):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_daily_pushes(user: str, token: str | None) -> dict[str, int]:
    """Push-event count per day, oldest-first. Empty dict on any API failure."""
    counts: dict[str, int] = {}
    try:
        for page in (1, 2):
            events = _get_json(
                f"{API_ROOT}/users/{user}/events/public?per_page=100&page={page}", token
            )
            if not events:
                break
            for ev in events:
                if ev.get("type") != "PushEvent":
                    continue
                day = ev["created_at"][:10]
                n = len(ev.get("payload", {}).get("commits", [])) or 1
                counts[day] = counts.get(day, 0) + n
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError) as exc:
        print(f"warning: could not fetch events for {user}: {exc}")
        return {}
    return counts


def fetch_language_mix(user: str, token: str | None) -> list[tuple[str, int]]:
    try:
        repos = _get_json(
            f"{API_ROOT}/users/{user}/repos?per_page=100&type=owner", token
        )
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as exc:
        print(f"warning: could not fetch repos for {user}: {exc}")
        return []
    tally: collections.Counter[str] = collections.Counter()
    for repo in repos:
        if repo.get("fork"):
            continue
        lang = repo.get("language")
        if lang:
            tally[lang] += 1
    return tally.most_common(8)


def build_series(counts: dict[str, int], days: int = 90) -> list[int]:
    today = datetime.date.today()
    series = []
    for i in range(days, -1, -1):
        day = (today - datetime.timedelta(days=i)).isoformat()
        series.append(counts.get(day, 0))
    return series


def curve_path(series: list[int], *, x0: float, y0: float, w: float, h: float) -> tuple[str, str]:
    n = len(series)
    peak = max(series) or 1
    step = w / max(n - 1, 1)
    pts = []
    for i, v in enumerate(series):
        x = x0 + i * step
        y = y0 + h - (v / peak) * h
        pts.append((round(x, 1), round(y, 1)))
    line = "M" + " L".join(f"{x},{y}" for x, y in pts)
    fill = line + f" L{pts[-1][0]},{y0 + h} L{pts[0][0]},{y0 + h} Z"
    return line, fill


def render(*, user: str, series: list[int], langs: list[tuple[str, int]], dark: bool) -> str:
    bg = "#0d1117" if dark else "#ffffff"
    fg = "#e6edf3" if dark else "#1f2328"
    muted = "#8b949e" if dark else "#57606a"
    grid = "#21262d" if dark else "#eaeef2"
    line_color = "#3fb950" if dark else "#1a7f37"

    parts = [
        f'<text x="20" y="30" font-family="{FONT_STACK}" font-size="16" '
        f'font-weight="700" fill="{fg}">training curve · @{user}</text>'
    ]

    if series and max(series) > 0:
        cx0, cy0, cw, ch = 20, 50, WIDTH - 40, 120
        for gy in range(4):
            y = cy0 + ch * gy / 3
            parts.append(f'<line x1="{cx0}" y1="{y:.1f}" x2="{cx0+cw}" y2="{y:.1f}" '
                          f'stroke="{grid}" stroke-width="1"/>')
        line, fill = curve_path(series, x0=cx0, y0=cy0, w=cw, h=ch)
        parts.append(f'<path d="{fill}" fill="{line_color}" opacity="0.15"/>')
        parts.append(f'<path d="{line}" fill="none" stroke="{line_color}" stroke-width="2">'
                      f'<animate attributeName="stroke-dasharray" from="0,4000" to="4000,0" '
                      f'dur="2.2s" fill="freeze"/></path>')
        parts.append(
            f'<text x="{cx0}" y="{cy0+ch+22}" font-family="{FONT_STACK}" font-size="12" '
            f'fill="{muted}">push events · last 90 days · peak {max(series)}/day</text>'
        )
        lang_y = cy0 + ch + 46
    else:
        parts.append(
            f'<text x="20" y="80" font-family="{FONT_STACK}" font-size="13" '
            f'fill="{muted}">no public push activity in the last 90 days</text>'
        )
        lang_y = 110

    if langs:
        parts.append(
            f'<text x="20" y="{lang_y}" font-family="{FONT_STACK}" font-size="13" '
            f'font-weight="700" fill="{fg}">language mix · owned repos</text>'
        )
        total = sum(c for _, c in langs) or 1
        bx, by, bw, bh = 20, lang_y + 14, WIDTH - 40, 18
        x = bx
        seen_colors = set()
        for lang, count in langs:
            seg_w = bw * count / total
            color = LANGUAGE_COLORS.get(lang, DEFAULT_LANG_COLOR)
            parts.append(f'<rect x="{x:.1f}" y="{by}" width="{seg_w:.1f}" height="{bh}" '
                         f'fill="{color}"/>')
            x += seg_w
        legend_y = by + bh + 20
        lx = 20
        row = 0
        for lang, count in langs:
            color = LANGUAGE_COLORS.get(lang, DEFAULT_LANG_COLOR)
            label = f"{lang} ({count})"
            seg_width = 16 + len(label) * 6.6 + 14
            if lx + seg_width > WIDTH - 20:
                lx = 20
                row += 1
            y = legend_y + row * 20
            parts.append(f'<circle cx="{lx+5}" cy="{y-4}" r="5" fill="{color}"/>')
            parts.append(f'<text x="{lx+16}" y="{y}" font-family="{FONT_STACK}" '
                         f'font-size="12" fill="{muted}">{label}</text>')
            lx += seg_width

    style = f"<style>text{{font-family:{FONT_STACK};}}</style>"
    body = style + "".join(parts)
    return svg_wrapper(WIDTH, HEIGHT, body, bg=bg, title=f"{user} activity")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="Mister2005")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    daily = fetch_daily_pushes(args.user, token)
    series = build_series(daily) if daily else []
    langs = fetch_language_mix(args.user, token)

    light_svg = render(user=args.user, series=series, langs=langs, dark=False)
    dark_svg = render(user=args.user, series=series, langs=langs, dark=True)
    light_path, dark_path = write_pair("activity", light_svg, dark_svg, ASSETS_DIR)
    for p in (light_path, dark_path):
        print(f"wrote {p} ({os.path.getsize(p)} bytes)")


if __name__ == "__main__":
    main()
