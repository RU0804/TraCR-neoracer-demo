#!/usr/bin/env python3
"""Build shared browser/Unity polylines and an English plan from the photo draft."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def smooth(points, closed, steps=16):
    result = []
    count = len(points)
    def at(i):
        return points[i % count] if closed else points[max(0, min(count - 1, i))]
    for i in range(count if closed else count - 1):
        a, b, c, d = [at(j) for j in (i-1, i, i+1, i+2)]
        for step in range(steps):
            t = step / steps
            result.append({axis: round(.5 * (2*b[axis] + (-a[axis]+c[axis])*t +
                (2*a[axis]-5*b[axis]+4*c[axis]-d[axis])*t*t +
                (-a[axis]+3*b[axis]-3*c[axis]+d[axis])*t*t*t), 6) for axis in ('x','y')})
    result.append(dict(points[0] if closed else points[-1]))
    return result


def split_dashes(points, dash=.075, gap=.055):
    # Split by distance, so browser, SVG and Unity show exactly the same tape.
    strips, current = [], []
    traveled = 0.
    for a, b in zip(points, points[1:]):
        length = math.hypot(b['x']-a['x'], b['y']-a['y'])
        used = 0.
        while used < length - 1e-10:
            phase = traveled % (dash + gap)
            on = phase < dash - 1e-9
            left = (dash if on else dash+gap) - phase
            if left < 1e-9:
                traveled += 1e-8
                continue
            take = min(left, length-used)
            def point(offset):
                f = offset / length
                return {axis: round(a[axis] + (b[axis]-a[axis])*f, 6) for axis in ('x','y')}
            if on:
                if not current:
                    current.append(point(used))
                current.append(point(used+take))
            elif current:
                strips.append(current)
                current = []
            used += take
            traveled += take
    if current:
        strips.append(current)
    return strips


def main():
    source = ROOT/'configs/map.photo-v1.json'
    draft = json.loads(source.read_text())
    geometry = {key: draft[key] for key in ('schema_version','label','measured','width_m','height_m','ground_color','coordinates')}
    geometry['revision'] = draft.get('revision', 1)
    geometry['stop_line_status'] = draft.get('stop_line_status', 'Unmeasured')
    geometry.update(source='configs/map.photo-v1.json', source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), markings=[], strips=[])
    for line in draft['markings']:
        points = line['points'] if line['kind']=='stop' else smooth(line['points'],line['closed'])
        geometry['markings'].append({**line,'points':points})
        parts = split_dashes(points) if line['kind']=='yellow' else [points]
        for part in parts:
            geometry['strips'].append(dict(id=line['id'],kind=line['kind'],width_m=line['width_m'],points=part))
    geometry['preview_route']={**draft['preview_route'],'points':smooth(draft['preview_route']['points'],False)}
    (ROOT/'configs/map.photo-v1.geometry.json').write_text(json.dumps(geometry,separators=(',',':'))+'\n')
    colors={'white':'#f4f5ef','yellow':'#f5dc39','stop':'#ff503b'}
    scale = min(665/draft['width_m'], 665/draft['height_m'])
    mat_width, mat_height = draft['width_m']*scale, draft['height_m']*scale
    def path(points):
        return 'M '+' L '.join(f"{70+p['x']*scale:.2f},{130+p['y']*scale:.2f}" for p in points)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="880" viewBox="0 0 1100 880">',
         '<rect width="1100" height="880" fill="#10191f"/>',
         '<g font-family="Arial,sans-serif" fill="#eaf0f2">',
         '<text x="56" y="54" font-size="29" font-weight="bold">TraCR / Foam-mat course</text>',
         '<text x="56" y="87" font-size="17" fill="#a8bbc7">Sketch-guided draft / Dimensions and stop positions pending</text>',
         f'<rect x="70" y="130" width="{mat_width:g}" height="{mat_height:g}" rx="3" fill="#4b4d4e"/>']
    for i in range(1,10):
        q=70+i*mat_width/10; r=130+i*mat_height/10
        svg += [f'<path d="M {q} 130 V {130+mat_height:g} M 70 {r} H {70+mat_width:g}" stroke="#444647" stroke-width="1"/>']
    for line in geometry['strips']:
        svg += [f'<path d="{path(line["points"])}" fill="none" stroke="{colors[line["kind"]]}" stroke-width="{line["width_m"]*scale:.2f}" stroke-linejoin="round"/>']
    svg += [f'<path d="{path(geometry["preview_route"]["points"])}" fill="none" stroke="#65e0c7" stroke-width="2" stroke-dasharray="5 6"/>']
    for line in draft['markings']:
        if line['kind']!='stop': continue
        a,b=line['points']; x=70+(a['x']+b['x'])*scale/2; y=130+(a['y']+b['y'])*scale/2
        svg += [f'<circle cx="{x}" cy="{y}" r="13" fill="#16242b"/><text x="{x}" y="{y+4}" font-size="12" text-anchor="middle">{line["id"]}</text>']
    svg += [f'<path d="M 70 815 V 830 H {70+mat_width:g} V 815" fill="none" stroke="#91a8b5"/>',
            f'<text x="{70+mat_width/2:g}" y="855" text-anchor="middle" font-size="17">{draft["width_m"]:g} m provisional</text>']
    notes=[('THE SKETCH',144),('White / Road edges',184),('Yellow / Lane divider',218),('Red / Provisional stops',252),('THE PREVIEW',322),('Lower + left outer lane',362),('Stop at S2, then S6',396),('2 s dwell at each line',430),('Front bumper stays back',464),('Cyan / Scripted route',498),('SCOPE',568),('Approximate geometry',608),('No full-lap validation',642),('No physical car control',676),('No executed Unity scene',710)]
    for text,y in notes:
        title=text in ('THE SKETCH','THE PREVIEW','SCOPE')
        svg += [f'<text x="770" y="{y}" font-size="{14 if title else 18}" fill="{"#65e0c7" if title else "#d3dee5"}">{text}</text>']
    svg += ['</g></svg>']
    (ROOT/'docs/media/field-map-plan.svg').write_text('\n'.join(svg)+'\n')
    print(f'Built {len(geometry["strips"])} paint strips and the map plan.')


if __name__=='__main__': main()
