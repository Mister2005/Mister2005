#!/usr/bin/env python3
"""Run this after cloning the repo: python varun.py

Prints the code-portrait (see assets/portrait-*.svg for the README version)
as 24-bit ANSI truecolor in the terminal, generated live from profile-pic.jpg
plus tools/gradient_descent.py, followed by the same fields as the README's
model card.

Deliberately not a `curl | python` one-liner - clone the repo and run it
locally instead.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))

import ascii_portrait  # noqa: E402  (path insert must happen first)

RESET = "\033[0m"


def print_portrait():
    img = ascii_portrait.prepare_image()
    grid = ascii_portrait.sample_grid(img)
    for row in grid:
        line = []
        for cell in row:
            r, g, b = cell.rgb
            # Blend toward black by opacity so the silhouette still reads
            # as a darker cutout in a terminal, same as in the SVG.
            r = round(r * (0.25 + 0.75 * cell.opacity))
            g = round(g * (0.25 + 0.75 * cell.opacity))
            b = round(b * (0.25 + 0.75 * cell.opacity))
            line.append(f"\033[38;2;{r};{g};{b}m{cell.char}")
        print("".join(line) + RESET)


MODEL_CARD = """
Model: varun-gupta-2005
Architecture: human / AI & Data Science Engineering student
Params: CGPA 8.71/10.0 - cohort 2023-2027
Training data: B.E. in AI & Data Science, Dwarkadas J Sanghvi College of
               Engineering, Mumbai
Intended use: ML pipelines, data visualization, large action models
Contact: https://www.linkedin.com/in/varun-yogesh-gupta
         varunygupta123@gmail.com
"""


def main():
    print_portrait()
    print(MODEL_CARD)


if __name__ == "__main__":
    main()
