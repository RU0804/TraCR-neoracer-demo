"""Regression checks for the distorted-straight and discontinuous-bend defects."""
import importlib.util
import json
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('map_curves', ROOT / 'scripts/map_curves.py')
curves = importlib.util.module_from_spec(spec)
spec.loader.exec_module(curves)
draft = json.loads((ROOT / 'configs/map.photo-v1.json').read_text())
paths = [line for line in draft['markings'] if line['kind'] != 'stop'] + [draft['preview_route']]


@pytest.mark.parametrize('line', paths, ids=lambda line: line.get('id', 'preview-route'))
def test_joins_preserve_declared_sharp_corners_and_smooth_fillets(line):
    parts = curves.segments(line)
    sharp = {tuple(point[axis] for axis in ('x', 'y'))
             for i, (point, cut) in enumerate(zip(line['points'], line['corner_cut_m']))
             if cut == 0 and (line.get('closed') or 0 < i < len(line['points']) - 1)}
    seen_sharp = set()
    pairs = list(zip(parts, parts[1:]))
    if line.get('closed'):
        pairs.append((parts[-1], parts[0]))
    for a, b in pairs:
        assert curves.distance(a[-1], b[0]) < 1e-12
        vertex = tuple(a[-1][axis] for axis in ('x', 'y'))
        if vertex in sharp:
            assert len(a) == len(b) == 2
            seen_sharp.add(vertex)
            continue
        da, db = curves.derivatives(a)[-1], curves.derivatives(b)[0]
        assert abs(da['x'] * db['y'] - da['y'] * db['x']) < 1e-12
        assert da['x'] * db['x'] + da['y'] * db['y'] > 0
    assert seen_sharp == sharp
    for part in parts:
        if len(part) == 6:
            second = curves.derivatives(curves.derivatives(part))
            assert all(math.hypot(p['x'], p['y']) < 1e-12 for p in (second[0], second[-1]))
    points = curves.sample(line)
    lengths = [curves.distance(a, b) for a, b in zip(points, points[1:])]
    assert min(lengths) > 0
    assert max(lengths) <= .00800002
    if line.get('closed'):
        assert points[0] == points[-1]


@pytest.mark.parametrize('name,x_left,x_right,y_bottom,y_min,y_max,x_min,x_max', [
    ('outer-edge', .25, 4.45, 4.45, 2.7, 3.4, 1.3, 3.4),
    ('main-divider', .65, 4.05, 4.05, 2.95, 3.4, 1.3, 3.4),
])
def test_main_long_sides_are_exact_straights(name, x_left, x_right, y_bottom, y_min, y_max, x_min, x_max):
    line = next(line for line in paths if line.get('id') == name)
    points = curves.sample(line)
    for x in (x_left, x_right):
        side = [p for p in points if abs(p['x'] - x) < .05 and y_min <= p['y'] <= y_max]
        assert len(side) > 50
        assert max(abs(p['x'] - x) for p in side) < 1e-8
    bottom = [p for p in points if abs(p['y'] - y_bottom) < .05 and x_min <= p['x'] <= x_max]
    assert len(bottom) > 50
    assert max(abs(p['y'] - y_bottom) for p in bottom) < 1e-8


def test_overlapping_corner_cuts_are_rejected():
    invalid = dict(points=[dict(x=0, y=0), dict(x=1, y=0), dict(x=1, y=1)],
                   corner_cut_m=[0, 1.1, 0], closed=False)
    with pytest.raises(ValueError, match='Overlapping'):
        curves.sample(invalid)


@pytest.mark.parametrize('closed', [False, True])
def test_zero_cuts_keep_square_corners_including_the_closed_seam(closed):
    vertices = [dict(x=0, y=0), dict(x=1, y=0), dict(x=1, y=1), dict(x=0, y=1)]
    line = dict(points=vertices, corner_cut_m=[0, 0, 0, 0], closed=closed)
    parts = curves.segments(line)
    edges = list(zip(vertices, vertices[1:] + vertices[:1])) if closed else list(zip(vertices, vertices[1:]))
    assert parts == [list(edge) for edge in edges]
    points = curves.sample(line)
    assert all(vertex in points for vertex in vertices)
    assert all(p['x'] in (0, 1) or p['y'] in (0, 1) for p in points)
