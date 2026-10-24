#!/usr/bin/env python3
"""Rasterize the standalone SVG map views without loading a vehicle or Unity."""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    if 'gilbreth' in str(ROOT) and not os.environ.get('SLURM_JOB_ID'):
        raise SystemExit('Use Slurm for browser rendering on Gilbreth.')
    if os.environ.get('SLURM_JOB_PARTITION', '') not in ('', 'a100-40gb', 'a30'):
        raise SystemExit('Use an allowed A100-40GB or A30 allocation.')
    with sync_playwright() as pw:
        # These SVGs need only 2D rasterization; avoid node-specific GPU capture failures.
        browser = pw.chromium.launch(headless=True, args=['--disable-dev-shm-usage', '--disable-gpu'])
        for name, width, height in [('field-map-only', 850, 950),
                                    ('field-map-only-shape', 850, 950),
                                    ('field-map-comparison', 1655, 1025)]:
            page = browser.new_page(viewport=dict(width=width, height=height))
            page.goto((ROOT / f'docs/media/{name}.svg').as_uri())
            page.screenshot(path=str(ROOT / f'docs/media/{name}.png'))
            page.close()
        browser.close()


if __name__ == '__main__':
    main()
