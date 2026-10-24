"""Exact straights, explicit sharp vertices and continuous quintic corner fillets.

Input points are tangent-intersection vertices, not interpolation knots.
Positive cuts trim both incident straights; a zero cut keeps the sharp vertex.
The first and last three Bezier controls are collinear with equal spacing:
second derivatives vanish at each end, so curvature joins continuously to zero.
"""
import math


def mix(a, b, t):
    return {axis: a[axis] + (b[axis] - a[axis]) * t for axis in ('x', 'y')}


def distance(a, b):
    return math.hypot(b['x'] - a['x'], b['y'] - a['y'])


def evaluate(controls, t):
    points = controls
    while len(points) > 1:
        points = [mix(a, b, t) for a, b in zip(points, points[1:])]
    return points[0]


def derivatives(controls):
    degree = len(controls) - 1
    return [{axis: degree * (b[axis] - a[axis]) for axis in ('x', 'y')}
            for a, b in zip(controls, controls[1:])]


def segments(line):
    points = line['points']
    cuts = line['corner_cut_m']
    closed = line.get('closed', False)
    count = len(points)
    if count < 2 or len(cuts) != count:
        raise ValueError('Every vertex needs one corner cut distance.')
    if any(not math.isfinite(v) or v < 0 for v in cuts):
        raise ValueError('Corner cuts must be finite and nonnegative.')
    if not closed and (cuts[0] or cuts[-1]):
        raise ValueError('Open path endpoints must have zero corner cuts.')
    for i in range(count if closed else count - 1):
        j = (i + 1) % count
        if distance(points[i], points[j]) <= cuts[i] + cuts[j]:
            raise ValueError(f'Overlapping corner cuts at vertices {i}/{j}.')
    entries, exits = [], []
    for i, vertex in enumerate(points):
        if cuts[i] == 0:
            entries.append(vertex)
            exits.append(vertex)
            continue
        before, after = points[(i - 1) % count], points[(i + 1) % count]
        entries.append(mix(vertex, before, cuts[i] / distance(vertex, before)))
        exits.append(mix(vertex, after, cuts[i] / distance(vertex, after)))
    result = []
    for i in range(count):
        if cuts[i]:
            a, b, vertex = entries[i], exits[i], points[i]
            # 0.30 gives a near-circular quarter turn without curvature spikes.
            result.append([a, mix(a, vertex, .30), mix(a, vertex, .60),
                           mix(b, vertex, .60), mix(b, vertex, .30), b])
        if closed or i < count - 1:
            result.append([exits[i], entries[(i + 1) % count]])
    return result


def sample(line, spacing=.008):
    if not math.isfinite(spacing) or spacing <= 0:
        raise ValueError('Sampling spacing must be finite and positive.')
    result = []
    for controls in segments(line):
        # The derivative is in the convex hull of derivative control vectors.
        # This speed bound makes every exported chord no longer than spacing.
        bound = max(math.hypot(v['x'], v['y']) for v in derivatives(controls))
        steps = max(1, math.ceil(bound / spacing))
        result.extend(evaluate(controls, i / steps) for i in range(steps))
    result.append(dict(segments(line)[-1][-1]))
    return [{axis: round(p[axis], 8) for axis in ('x', 'y')} for p in result]
