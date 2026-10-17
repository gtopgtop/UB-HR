"""Server-side geometry for the small inline charts (sparklines, meters).

Templates draw the SVG; these helpers only compute coordinates and percentages,
so a chart needs no JavaScript and no chart library.
"""


def meter(value, total):
    """A part-of-whole figure for a meter track."""
    pct = round(value / total * 100) if total else 0
    return {"value": value, "total": total, "pct": max(0, min(100, pct))}


def sparkline(points, width=160, height=44, pad=7):
    """Polyline and dot coordinates for [(label, value), ...], scaled to the data's own range.

    `pad` keeps the r=4 end-dot and its 2px surface ring inside the viewBox.
    """
    values = [value for _, value in points]
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    step = (width - 2 * pad) / max(len(points) - 1, 1)
    dots = [
        {
            "label": label,
            "value": value,
            "x": round(pad + i * step, 1),
            "y": round(pad + (hi - value) / span * (height - 2 * pad), 1),
        }
        for i, (label, value) in enumerate(points)
    ]
    return {
        "width": width,
        "height": height,
        "points": " ".join(f"{d['x']},{d['y']}" for d in dots),
        "dots": dots,
        "summary": ", ".join(f"{label} {value}" for label, value in points),
    }


def columns(points, width=320, height=150, top=18, bottom=22, bar=24):
    """Vertical bars for [(label, value), ...], grown from a zero baseline.

    Bars are at most `bar` px wide and centred in their band, with a 4px rounded top and a
    square foot (the path's corners). `top` leaves room for the value label over the tallest bar.
    """
    hi = max(value for _, value in points) or 1
    band = width / len(points)
    w = min(bar, band - 8)
    base = height - bottom
    out = []
    for i, (label, value) in enumerate(points):
        h = (value / hi) * (base - top)
        x = round(i * band + (band - w) / 2, 1)
        y = round(base - h, 1)
        r = min(4, h / 2, w / 2)
        path = (f"M{x},{base} V{y + r:.1f} Q{x},{y} {x + r:.1f},{y} H{x + w - r:.1f} "
                f"Q{x + w},{y} {x + w},{y + r:.1f} V{base} Z") if h else ""
        out.append({"label": label, "value": value, "x": x, "y": y, "w": round(w, 1), "h": round(h, 1),
                    "cx": round(x + w / 2, 1), "path": path, "peak": value == hi,
                    "band_x": round(i * band, 1), "band_w": round(band, 1)})
    return {"width": width, "height": height, "base": base, "bars": out,
            "summary": ", ".join(f"{label} {value}" for label, value in points)}


def linechart(points, lo, hi, width=320, height=150, pad_x=12, top=12, bottom=22, ticks=()):
    """A line with dots for [(label, value), ...] on a fixed lo..hi scale, plus y gridlines at `ticks`."""
    span = (hi - lo) or 1
    base = height - bottom
    step = (width - 2 * pad_x) / max(len(points) - 1, 1)
    y_of = lambda v: round(top + (hi - v) / span * (base - top), 1)  # noqa: E731
    dots = [{"label": label, "value": value, "x": round(pad_x + i * step, 1), "y": y_of(value)}
            for i, (label, value) in enumerate(points)]
    return {"width": width, "height": height, "base": base, "dots": dots,
            "points": " ".join(f"{d['x']},{d['y']}" for d in dots),
            "ticks": [{"value": t, "y": y_of(t)} for t in ticks],
            "summary": ", ".join(f"{label} {value}" for label, value in points)}
