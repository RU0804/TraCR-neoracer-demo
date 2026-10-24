#!/usr/bin/env python3
"""Build map-only and same-scale comparison SVGs from the exported geometry."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'docs/media'


def stop_labels(geometry, x, y, scale):
    """Keep stable source IDs beside the tape, with leaders to avoid covering it."""
    result = []
    for line in geometry['markings']:
        if line['kind'] != 'stop':
            continue
        a, b = line['points']
        px = x + (a['x'] + b['x']) * scale / 2
        py = y + (a['y'] + b['y']) * scale / 2
        vertical = abs(b['y'] - a['y']) >= abs(b['x'] - a['x'])
        lx, ly = (px + 34, py) if vertical else (px, py - 30)
        result.append(f'<g aria-label="Stop line {escape(line["id"])}">'
                      f'<path d="M {px:.2f},{py:.2f} L {lx:.2f},{ly:.2f}" stroke="#eaf0f2" stroke-width="1.2"/>'
                      f'<rect x="{lx-18:.2f}" y="{ly-13:.2f}" width="36" height="26" rx="6" fill="#142027" stroke="#ff8b79"/>'
                      f'<text x="{lx:.2f}" y="{ly+5:.2f}" text-anchor="middle" font-size="14" font-weight="bold" fill="#ffffff">{escape(line["id"])}</text></g>')
    return '\n'.join(result)


def panel(geometry, x, y, size=760, stops=True):
    scale = size / max(geometry['width_m'], geometry['height_m'])
    result = [f'<rect x="{x}" y="{y}" width="{geometry["width_m"] * scale}" '
              f'height="{geometry["height_m"] * scale}" rx="4" fill="#45494c"/>']
    colors = {'white': '#f4f5ef', 'yellow': '#f5dc39', 'stop': '#ff503b'}
    for strip in geometry['strips']:
        if not stops and strip['kind'] == 'stop':
            continue
        closed = len(strip['points']) > 2 and strip['points'][0] == strip['points'][-1]
        points = strip['points'][:-1] if closed else strip['points']
        path = 'M ' + ' L '.join(f'{x + p["x"] * scale:.3f},{y + p["y"] * scale:.3f}' for p in points)
        if closed:
            path += ' Z'
        result.append(f'<path d="{path}" fill="none" stroke="{colors[strip["kind"]]}" '
                      f'stroke-width="{strip["width_m"] * scale:.3f}" stroke-linejoin="miter" stroke-miterlimit="2"/>')
    if stops:
        result.append(stop_labels(geometry, x, y, scale))
    return '\n'.join(result)


def document(width, height, content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#10191f"/>'
            f'<g font-family="Arial,sans-serif" fill="#eaf0f2">{content}</g></svg>\n')


def main():
    current = json.loads((ROOT / 'configs/map.photo-v1.geometry.json').read_text())
    previous = json.loads((MEDIA / 'map-revision-7/map.photo-v1.geometry.json').read_text())
    for suffix, stops in [('', True), ('-shape', False)]:
        title = 'TraCR / Revised map' if stops else 'TraCR / Road geometry only'
        content = (f'<text x="45" y="54" font-size="28" font-weight="bold">{title}</text>'
                   f'<text x="45" y="87" font-size="17" fill="#a8bbc7">Revision {current["revision"]} / Four square corners matched to the physical layout</text>'
                   + panel(current, 45, 118, stops=stops)
                   + '<text x="45" y="914" font-size="16" fill="#a8bbc7">4.75 m square assumed / Dimensions and stop positions unmeasured</text>')
        (MEDIA / f'field-map-only{suffix}.svg').write_text(document(850, 950, content))
    content = ('<text x="45" y="52" font-size="30" font-weight="bold">TraCR / Map geometry comparison</text>'
               '<text x="45" y="86" font-size="17" fill="#a8bbc7">Same scale and orientation / No vehicle or preview route</text>'
               f'<text x="45" y="131" font-size="22">Before / Revision {previous["revision"]}</text>'
               f'<text x="850" y="131" font-size="22" fill="#65e0c7">After / Revision {current["revision"]}</text>'
               + panel(previous, 45, 153) + panel(current, 850, 153)
               + '<text x="45" y="951" font-size="17" fill="#a8bbc7">Previous rounded island corners</text>'
               '<text x="850" y="951" font-size="17" fill="#a8bbc7">Square corners above S1/S5 and on the small island</text>'
               '<text x="45" y="994" font-size="16" fill="#a8bbc7">Both maps use a provisional 4.75 m square. Red stop locations remain provisional.</text>')
    (MEDIA / 'field-map-comparison.svg').write_text(document(1655, 1025, content))


if __name__ == '__main__':
    main()
