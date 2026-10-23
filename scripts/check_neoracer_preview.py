#!/usr/bin/env python3
"""Decode and verify the generated NeoRacer preview media; requires Pillow."""
import hashlib
import json
import os
from pathlib import Path
from PIL import Image

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
    for index in range(gif.n_frames):
        gif.seek(index)
        duration += gif.info['duration']
        frame = gif.convert('RGB')
        for view, crop in enumerate([(60, 365, 580, 570), (625, 365, 1140, 570)]):
            hashes[view].add(hashlib.sha256(frame.crop(crop).tobytes()).hexdigest())
        if index in (0, gif.n_frames // 2, gif.n_frames - 1):
            frame.save(root / f'runtime/neoracer-preview/verified-{index}.png')
    assert 19900 <= duration <= 20100
    # A symmetric loop can repeat viewpoints; require scene motion, not a unique image every frame.
    assert all(len(h) > 20 for h in hashes)
    assert not manifest['unmatched_materials']
    assert manifest['aligned_forward_vector'][2] > 0.99
    width, height, length = manifest['size_meters']
    assert 0.2 < width < 0.35 and 0.15 < height < 0.3 and 0.35 < length < 0.55
    result = {'decoded_frames': gif.n_frames, 'duration_ms': duration,
              'distinct_camera_regions': [len(h) for h in hashes], 'loop': 'infinite',
              'artifact_checksums_match': True, 'size': list(gif.size),
              'slurm_job_id': os.environ.get('SLURM_JOB_ID'),
              'partition': os.environ.get('SLURM_JOB_PARTITION'),
              'scope': 'Geometry preview media only; no physical hardware, live bridge or Unity execution.'}
(media / 'neoracer-validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
