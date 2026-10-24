#!/usr/bin/env python3
"""Decode and verify the generated NeoRacer preview media; requires Pillow."""
import hashlib
import json
import math
import os
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

root = Path(__file__).resolve().parents[1]
media = root / 'docs/media'
(root / 'runtime/neoracer-preview').mkdir(parents=True, exist_ok=True)
manifest = json.loads((media / 'neoracer-preview.json').read_text())
for name, details in manifest['artifacts'].items():
    data = (media / name).read_bytes()
    assert len(data) == details['bytes']
    assert hashlib.sha256(data).hexdigest() == details['sha256']
with Image.open(media / 'neoracer-preview.gif') as gif:
    assert gif.info['loop'] == 0
    assert gif.size == tuple(manifest['size'])
    assert gif.n_frames == manifest['frames']
    duration = 0
    hashes = [set(), set()]
    windows = {stage['id']: (math.ceil(stage['start'] * manifest['fps']), math.ceil(stage['end'] * manifest['fps']))
               for stage in manifest['geometry_checks']['stages'] if stage['kind'] == 'stop'}
    references = {}
    stop_errors = {key: [0., 0.] for key in windows}
    stopped_frames = {key: 0 for key in windows}
    for index in range(gif.n_frames):
        gif.seek(index)
        duration += gif.info['duration']
        frame = gif.convert('RGB')
        stop_id = next((key for key, (start, end) in windows.items() if start <= index < end), None)
        if stop_id:
            stopped_frames[stop_id] += 1
        for view, crop in enumerate([(60, 365, 580, 570), (625, 365, 1140, 570)]):
            digest = hashlib.sha256(frame.crop(crop).tobytes()).hexdigest()
            hashes[view].add(digest)
            if stop_id:
                region = frame.crop(crop)
                key = (stop_id, view)
                if key not in references:
                    references[key] = region
                else:
                    mae = sum(ImageStat.Stat(ImageChops.difference(region, references[key])).mean) / 3
                    stop_errors[stop_id][view] = max(stop_errors[stop_id][view], mae)
        if index in (0, gif.n_frames // 2, gif.n_frames - 1):
            frame.save(root / f'runtime/neoracer-preview/verified-{index}.png')
    assert abs(duration - manifest["duration_seconds"] * 1000) <= 100
    # Stops intentionally repeat viewpoints; require motion elsewhere in both views.
    assert all(len(h) > 20 for h in hashes)
    assert not manifest['unmatched_materials']
    assert manifest['aligned_forward_vector'][2] > 0.99
    width, height, length = manifest['size_meters']
    assert 0.2 < width < 0.35 and 0.15 < height < 0.3 and 0.35 < length < 0.55
    checks = manifest['geometry_checks']
    assert checks['minimum_paint_clearance_m'] >= .015
    assert checks['sample_spacing_m'] <= .01
    assert checks['tire_contact_method'] == 'Transformed tire mesh vertices'
    assert len(checks['tire_contacts']) == 4
    assert max(abs(t['bottom']) for t in checks['tire_contacts']) <= .002
    assert checks['traffic_side'] == 'right'
    assert checks['minimum_divider_left_offset_m'] > 0
    assert [s['id'] for s in checks['stops']] == ['S6','S2']
    assert all(stage['to'] > stage['from'] and stage['end'] > stage['start']
               for stage in checks['stages'] if stage['kind'] == 'drive')
    for stop in checks['stops']:
        assert stop['front_bumper_clearance_m'] >= checks['required_bumper_gap_m'] - 1e-6
        assert stop['dwell_seconds'] == 2
    assert checks['map_source_sha256'] == hashlib.sha256((root/'configs/map.photo-v1.json').read_bytes()).hexdigest()
    # SwiftShader/antialiasing can vary a few channel values by 1; GIF quantization can amplify them.
    # Bound mean absolute image change tightly (0.001 on a 0-255 channel scale).
    assert all(count >= 2 * manifest['fps'] - 1 for count in stopped_frames.values())
    assert all(max(errors) <= .001 for errors in stop_errors.values()), stop_errors
    result = {'stopped_camera_frames': stopped_frames, 'maximum_stopped_image_mae': stop_errors,
              'stopped_image_mae_limit': .001, 'geometry_checks': checks, 'decoded_frames': gif.n_frames, 'duration_ms': duration,
              'distinct_camera_regions': [len(h) for h in hashes], 'loop': 'infinite',
              'artifact_checksums_match': True, 'size': list(gif.size),
              'slurm_job_id': os.environ.get('SLURM_JOB_ID'),
              'partition': os.environ.get('SLURM_JOB_PARTITION'),
              'scope': 'Geometry preview media only; no physical hardware, live bridge or Unity execution.'}
(media / 'neoracer-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
