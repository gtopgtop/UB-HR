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
