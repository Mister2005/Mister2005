"""A plain batch gradient descent fit for linear regression.

This is a real, runnable implementation - not a decoration. Its source text
doubles as the character stream for the code-portrait in assets/portrait-*.svg:
every glyph you see in that portrait is a character copied in order from this
file, tinted with the photo's actual pixel colours.
"""

from __future__ import annotations

import random


def generate_data(n: int = 200, true_w: float = 2.5, true_b: float = -1.0, noise: float = 1.0):
    xs = [random.uniform(-10, 10) for _ in range(n)]
    ys = [true_w * x + true_b + random.gauss(0, noise) for x in xs]
    return xs, ys


def predict(w: float, b: float, x: float) -> float:
    return w * x + b


def mean_squared_error(w: float, b: float, xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    total = 0.0
    for x, y in zip(xs, ys):
        error = predict(w, b, x) - y
        total += error * error
    return total / n


def gradients(w: float, b: float, xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    dw = 0.0
    db = 0.0
    for x, y in zip(xs, ys):
        error = predict(w, b, x) - y
        dw += 2 * error * x
        db += 2 * error
    return dw / n, db / n


def gradient_descent(
    xs: list[float],
    ys: list[float],
    lr: float = 0.01,
    epochs: int = 500,
    w: float = 0.0,
    b: float = 0.0,
):
    history = []
    for epoch in range(epochs):
        dw, db = gradients(w, b, xs, ys)
        w -= lr * dw
        b -= lr * db
        loss = mean_squared_error(w, b, xs, ys)
        history.append(loss)
        if epoch % 50 == 0:
            print(f"epoch {epoch:4d}  loss {loss:.4f}  w {w:.4f}  b {b:.4f}")
    return w, b, history


def main():
    random.seed(2005)
    xs, ys = generate_data()
    w, b, history = gradient_descent(xs, ys)
    print(f"\nfinal fit: y = {w:.4f} * x + {b:.4f}")
    print(f"final loss: {history[-1]:.4f}")


if __name__ == "__main__":
    main()
