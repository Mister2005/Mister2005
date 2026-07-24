"""Rebuild profile-pic.jpg as an SVG 'code portrait'.

Each grid cell is filled with the next character from gradient_descent.py's
source text (an honest, runnable implementation - see that file), tinted with
that cell's own pixel colour from the photo. Glyph identity carries the code;
colour and opacity carry the image. Brightness drives opacity so the dark
silhouette in the source photo recedes and the lit sky/ridge behind it carries
the facial outline.

Usage:
    python tools/ascii_portrait.py
Outputs (all under assets/):
    portrait-light.svg, portrait-dark.svg, portrait.txt, portrait-preview.png
"""

from __future__ import annotations

import itertools
import os

from PIL import Image, ImageOps

from common import (
    Cell,
    build_runs,
    luminance,
    picture_tag,
    quantize_color,
    svg_wrapper,
    text_run_svg,
    write_pair,
    FONT_STACK,
)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_IMAGE = os.path.join(REPO_ROOT, "profile-pic.jpg")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
CODE_SOURCE = os.path.join(REPO_ROOT, "tools", "gradient_descent.py")

# Grid geometry. Character cells are roughly twice as tall as wide, so the
# vertical sample step is doubled relative to the horizontal one to avoid
# vertically stretching the face.
COLS = 130
CELL_W = 6.6
CELL_H = 12.6
ASPECT_CORRECTION = 0.52  # rows sampled per column-equivalent of image height

PALETTE_LEVELS = 5
MIN_OPACITY = 0.05
OPACITY_POWER = 2.4  # > 1 pushes the dark silhouette toward near-invisible,
# so the head/jacket read as a clean negative-space cutout against the bright,
# fully-opaque sky/ridge text rather than as a soup of dim grey glyphs
GAMMA = 0.75  # < 1 lifts shadow detail (sunglasses/hair/jaw) without blowing the sky


def load_source_chars() -> itertools.cycle:
    with open(CODE_SOURCE, "r", encoding="utf-8") as f:
        text = f.read()
    # Collapse whitespace runs to single spaces so the grid doesn't fill with
    # long blank stretches from indentation/blank lines - we want a dense,
    # visibly "codey" texture across the whole face.
    chars = [c for c in text if not c.isspace()] or list(text)
    return itertools.cycle(chars)


def prepare_image() -> Image.Image:
    img = Image.open(SOURCE_IMAGE).convert("RGB")
    w, h = img.size

    # Head-and-shoulders crop: the subject is upper-centre of the frame.
    # Tuned by eye against portrait-preview.png.
    left = int(w * 0.33)
    right = int(w * 0.61)
    top = int(h * 0.255)
    bottom = int(h * 0.50)
    img = img.crop((left, top, right, bottom))

    # Lift shadow detail: autocontrast first, then a gamma curve.
    img = ImageOps.autocontrast(img, cutoff=1)
    lut = [round(255 * ((i / 255) ** GAMMA)) for i in range(256)]
    img = img.point(lut * 3)
    return img


def sample_grid(img: Image.Image) -> list[list[Cell]]:
    w, h = img.size
    cell_px_w = w / COLS
    rows_count = int(h / (cell_px_w / ASPECT_CORRECTION))
    chars = load_source_chars()

    small = img.resize((COLS, rows_count), Image.LANCZOS)
    pixels = small.load()

    grid: list[list[Cell]] = []
    for y in range(rows_count):
        row: list[Cell] = []
        for x in range(COLS):
            rgb = pixels[x, y]
            q = quantize_color(rgb, PALETTE_LEVELS)
            lum = luminance(rgb)
            opacity = round(MIN_OPACITY + (1 - MIN_OPACITY) * (lum ** OPACITY_POWER), 2)
            row.append(Cell(char=next(chars), rgb=q, opacity=opacity))
        grid.append(row)
    return grid


def render_svg(grid: list[list[Cell]], *, dark: bool) -> str:
    rows = len(grid)
    width = round(COLS * CELL_W) + 20
    height = round(rows * CELL_H) + 20
    bg = "#0d1117" if dark else "#ffffff"

    body_parts = []
    for row_idx, row in enumerate(grid):
        runs = build_runs(row)
        y = 10 + (row_idx + 1) * CELL_H - CELL_H * 0.25
        delay = round(row_idx * 0.012, 3)
        class_name = f"r{row_idx}"
        for run in runs:
            body_parts.append(
                text_run_svg(10, y, CELL_W, run, extra_attrs=f' class="{class_name}"')
            )
        body_parts.append(
            f"<style>.{class_name}{{animation-delay:{delay}s}}</style>"
        )

    style = (
        "<style>"
        f"text{{font-family:{FONT_STACK};font-size:12px;"
        "animation:reveal 0.6s ease-out both;}"
        "@keyframes reveal{from{opacity:0}to{opacity:1}}"
        "</style>"
    )
    body = style + "".join(body_parts)
    title = "Varun Gupta, rendered from the source of gradient_descent.py"
    return svg_wrapper(width, height, body, bg=bg, title=title)


def render_txt(grid: list[list[Cell]]) -> str:
    ramp = " .:-=+*#%@"
    lines = []
    for row in grid:
        chars = []
        for cell in row:
            level = min(len(ramp) - 1, int(cell.opacity * (len(ramp) - 1)))
            chars.append(ramp[level] if cell.opacity < 0.5 else cell.char)
        lines.append("".join(chars))
    return "\n".join(lines)


def render_preview_png(grid: list[list[Cell]], out_path: str) -> None:
    from PIL import ImageDraw, ImageFont

    rows = len(grid)
    scale = 3
    width = round(COLS * CELL_W * scale)
    height = round(rows * CELL_H * scale)
    canvas = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("consola.ttf", int(CELL_H * scale * 0.85))
    except OSError:
        font = ImageFont.load_default()

    for row_idx, row in enumerate(grid):
        for col_idx, cell in enumerate(row):
            x = col_idx * CELL_W * scale
            y = row_idx * CELL_H * scale
            shade = tuple(round(c * (0.35 + 0.65 * cell.opacity)) for c in cell.rgb)
            draw.text((x, y), cell.char, fill=shade, font=font)

    canvas.save(out_path)


def main():
    img = prepare_image()
    grid = sample_grid(img)

    light_svg = render_svg(grid, dark=False)
    dark_svg = render_svg(grid, dark=True)
    write_pair("portrait", light_svg, dark_svg, ASSETS_DIR)

    txt_path = os.path.join(ASSETS_DIR, "portrait.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(render_txt(grid))

    preview_path = os.path.join(ASSETS_DIR, "portrait-preview.png")
    render_preview_png(grid, preview_path)

    print(f"grid: {COLS} cols x {len(grid)} rows")
    print("wrote:")
    for name in ("portrait-light.svg", "portrait-dark.svg", "portrait.txt", "portrait-preview.png"):
        path = os.path.join(ASSETS_DIR, name)
        print(f"  {path}  ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
