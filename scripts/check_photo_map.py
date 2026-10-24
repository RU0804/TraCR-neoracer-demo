#!/usr/bin/env python3
"""Check photo-map topology and shared sampled geometry without Unity."""
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'configs/map.photo-v1.json'
m=json.loads((ROOT/'configs/map.photo-v1.geometry.json').read_text())
assert m['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert not m['measured']
assert {p['id'] for p in m['markings'] if p['kind']=='stop'}=={'S1','S2','S3','S4','S5','S6'}
for line in m['markings']:
    assert all(0<=p['x']<=m['width_m'] and 0<=p['y']<=m['height_m'] for p in line['points'])
    if line['closed']:
        assert line['points'][0] == line['points'][-1], (line['id'], 'open seam')

def orient(a,b,c):
    return (b['x']-a['x'])*(c['y']-a['y'])-(b['y']-a['y'])*(c['x']-a['x'])

def crosses(a,b,c,d):
    if (max(a['x'], b['x']) < min(c['x'], d['x']) or
        max(c['x'], d['x']) < min(a['x'], b['x']) or
        max(a['y'], b['y']) < min(c['y'], d['y']) or
        max(c['y'], d['y']) < min(a['y'], b['y'])):
        return False
    return orient(a,b,c)*orient(a,b,d)<-1e-14 and orient(c,d,a)*orient(c,d,b)<-1e-14

boundaries=[line for line in m['markings'] if line['kind']!='stop']

def point_segment_distance(p, a, b):
    dx, dy = b['x'] - a['x'], b['y'] - a['y']
    length2 = dx*dx + dy*dy
    assert length2 > 0, 'Duplicate consecutive geometry points'
    t = max(0, min(1, ((p['x']-a['x'])*dx + (p['y']-a['y'])*dy) / length2))
    return math.hypot(p['x'] - a['x'] - t*dx, p['y'] - a['y'] - t*dy)

def distance_to_lines(point, lines):
    return min(point_segment_distance(point, a, b) for line in lines
               for a, b in zip(line['points'], line['points'][1:]))

# Stops must terminate on a boundary/divider, and the branch must meet the loop.
stop_anchor_error = max(distance_to_lines(p, boundaries) for line in m['markings']
                        if line['kind']=='stop' for p in line['points'])
assert stop_anchor_error < .00001, ('Detached stop endpoint', stop_anchor_error)
branch = next(line for line in boundaries if line['id']=='branch-divider')
divider = next(line for line in boundaries if line['id']=='main-divider')
assert all(distance_to_lines(p, [divider]) < .00001 for p in (branch['points'][0], branch['points'][-1]))
for first,second in itertools.combinations(boundaries,2):
    for a,b in zip(first['points'],first['points'][1:]):
        for c,d in zip(second['points'],second['points'][1:]):
            assert not crosses(a,b,c,d),(first['id'],second['id'],'crossing')
for line in boundaries:
    segments=list(zip(line['points'],line['points'][1:]))
    for i,(a,b) in enumerate(segments):
        for j in range(i+2,len(segments)):
            if line['closed'] and i==0 and j==len(segments)-1: continue
            assert not crosses(a,b,*segments[j]),(line['id'],'self-intersection')
# Generated dash lengths must be finite and never extend beyond a full dash.
for strip in m['strips']:
    assert len(strip['points'])>=2
    if strip['kind']=='yellow':
        length=sum(((b['x']-a['x'])**2+(b['y']-a['y'])**2)**.5 for a,b in zip(strip['points'],strip['points'][1:]))
        assert 0<length<=.0751
print(json.dumps({'markings':len(m['markings']),'stop_lines':6,'paint_strips':len(m['strips']),
                  'source_hash_matches':True,'boundary_crossings':0,'self_intersections':0,
                  'maximum_stop_endpoint_error_m':stop_anchor_error,'branch_connected':True,
                  'scope':'Map data checks only; no Unity compilation or execution.'},indent=2))
