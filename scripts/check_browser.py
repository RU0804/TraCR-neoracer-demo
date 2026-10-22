#!/usr/bin/env python3
"""Run only on a workstation or Slurm allocation, with servers at 8080 and 8081."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

out=Path(os.environ.get('TRACR_TEST_OUTPUT','runtime/validation'));out.mkdir(parents=True,exist_ok=True)
errors=[]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1440,'height':1080})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8080')
    page.wait_for_function("document.querySelector('#pairs').textContent !== '0'")
    page.wait_for_function("!document.querySelector('#sim').hidden && document.querySelector('#sim').naturalWidth > 0")
    assert 'SYNTHETIC' in page.locator('#notice').inner_text()
    assert 'NOT AUTODRIVE' in page.locator('#sim-state').inner_text()
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.screenshot(path=str(out/'selftest-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.wait_for_timeout(250)
    assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
    page.screenshot(path=str(out/'selftest-mobile.png'),full_page=True)
    # Exercise heartbeat beyond a whole heartbeat period (requires server WS receive loop).
    start=int(page.locator('#pairs').inner_text())
    page.wait_for_timeout(16000)
    assert int(page.locator('#pairs').inner_text())>start+70
    assert 'connected' in page.locator('#connection').inner_text()
    page.evaluate('socket.onclose = null; socket.close();')
    page.wait_for_timeout(1800)
    assert 'STALE' in page.locator('#sim-state').inner_text()
    assert 'frozen' in page.locator('#notice').inner_text()
    page.goto('http://127.0.0.1:8081')
    page.wait_for_function("document.querySelector('#mode').textContent === 'LIVE INPUT MODE'")
    assert page.locator('#sim').is_hidden()
    assert page.locator('#real').is_hidden()
    assert 'missing' in page.locator('#notice').inner_text()
    page.set_viewport_size({'width':1440,'height':1080})
    page.screenshot(path=str(out/'live-awaiting-hardware.png'),full_page=True)
    assert not errors,errors
    browser.close()
result={'passed':True,'selftest_images_labeled':True,'desktop_and_mobile_no_overflow':True,
        'heartbeat_16s':True,'disconnect_marks_frozen_images_stale':True,
        'live_mode_does_not_fabricate_input':True,'javascript_errors':errors,
        'hardware_tested':False,'unity_tested':False}
(out/'browser.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
