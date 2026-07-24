"""Shared helpers for the SVG generators in this repo.

GitHub's markdown renderer strips inline <svg>, so every generator here emits
standalone .svg files that the README references via <img>/<picture>. Because
those files render through GitHub's camo proxy, <script> never executes -
animation has to be plain CSS @keyframes or SMIL, both of which survive camo.

Two constraints shape everything in this module:

1. `prefers-color-scheme` inside an image-loaded SVG follows the *OS* theme,
   not the GitHub site theme. So every visual ships as a light/dark pair and
   the README switches between them with <picture>, which GitHub does honor.
2. Character-grid alignment cannot rely on font metrics (we don't know what
   monospace font the viewer's OS substitutes). Every text run is emitted with
   an explicit x plus textLength/lengthAdjust so columns land exactly on the
   grid regardless of the substituted font.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape as _xml_escape


FONT_STACK = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def quantize_channel(value: int, levels: int = 6) -> int:
    """Snap an 8-bit channel to one of `levels` evenly spaced values."""
    step = 255 / (levels - 1)
    return round(round(value / step) * step)


def quantize_color(rgb: tuple[int, int, int], levels: int = 6) -> tuple[int, int, int]:
    return tuple(quantize_channel(c, levels) for c in rgb)


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (c / 255 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


@dataclass
class Cell:
    char: str
    rgb: tuple[int, int, int]
    opacity: float = 1.0


@dataclass
class GridRun:
    """A horizontal run of cells sharing a colour, emitted as one <tspan>."""

    col: int
    text: str
    color_hex: str
    opacity: float


def build_runs(row: list[Cell]) -> list[GridRun]:
    """Collapse consecutive same-colour cells in a row into fewer tspans.

    Cuts file size roughly 2-3x versus one <tspan> per character, since large
    flat regions (sky, jacket) are common in a photo-derived grid.
    """
    runs: list[GridRun] = []
    if not row:
        return runs
    start = 0
    cur_hex = rgb_to_hex(row[0].rgb)
    cur_op = row[0].opacity
    buf = [row[0].char]
    for i in range(1, len(row)):
        cell = row[i]
        hexc = rgb_to_hex(cell.rgb)
        if hexc == cur_hex and abs(cell.opacity - cur_op) < 0.01:
            buf.append(cell.char)
        else:
            runs.append(GridRun(start, "".join(buf), cur_hex, cur_op))
            start = i
            cur_hex = hexc
            cur_op = cell.opacity
            buf = [cell.char]
    runs.append(GridRun(start, "".join(buf), cur_hex, cur_op))
    return runs


def text_run_svg(x: float, y: float, cell_w: float, run: GridRun, extra_attrs: str = "") -> str:
    """One <text> element for a run, glyph-width-locked via textLength."""
    n = len(run.text)
    text_length = round(cell_w * n, 2)
    px = round(x + cell_w * run.col, 2)
    escaped = _xml_escape(run.text, quote=False)
    op_attr = f' fill-opacity="{run.opacity:.2f}"' if run.opacity < 1.0 else ""
    return (
        f'<text x="{px}" y="{y}" textLength="{text_length}" '
        f'lengthAdjust="spacingAndGlyphs" fill="{run.color_hex}"{op_attr}{extra_attrs}>'
        f"{escaped}</text>"
    )


def svg_wrapper(width: int, height: int, body: str, *, bg: str, title: str = "") -> str:
    title_tag = f"<title>{_xml_escape(title)}</title>" if title else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img">'
        f"{title_tag}"
        f'<rect width="100%" height="100%" fill="{bg}"/>'
        f"{body}"
        f"</svg>"
    )


def write_pair(basename: str, light_svg: str, dark_svg: str, out_dir: str) -> tuple[str, str]:
    """Write <basename>-light.svg and <basename>-dark.svg into out_dir."""
    import os

    os.makedirs(out_dir, exist_ok=True)
    light_path = os.path.join(out_dir, f"{basename}-light.svg")
    dark_path = os.path.join(out_dir, f"{basename}-dark.svg")
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    return light_path, dark_path


def picture_tag(repo_raw_base: str, basename: str, alt: str, width: str = "100%") -> str:
    """<picture> block for README.md, pointing at raw.githubusercontent.com."""
    light = f"{repo_raw_base}/assets/{basename}-light.svg"
    dark = f"{repo_raw_base}/assets/{basename}-dark.svg"
    return (
        "<picture>\n"
        f'  <source media="(prefers-color-scheme: dark)" srcset="{dark}">\n'
        f'  <source media="(prefers-color-scheme: light)" srcset="{light}">\n'
        f'  <img alt="{_xml_escape(alt)}" src="{light}" width="{width}">\n'
        "</picture>"
    )
