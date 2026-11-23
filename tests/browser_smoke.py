"""Run with a running local server and optional playwright dependency.
python -m pip install playwright && python -m playwright install chromium
python tests/browser_smoke.py
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
    errors=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto('http://127.0.0.1:8000/',wait_until='networkidle')
    page.evaluate('localStorage.clear()');page.reload(wait_until='networkidle')
    assert page.get_by_text('YOUR ARK.').count() == 1
    Path('docs/screenshots').mkdir(parents=True,exist_ok=True)
    page.screenshot(path='docs/screenshots/overview.png',full_page=True)
    page.goto('http://127.0.0.1:8000/#calculators',wait_until='networkidle')
    page.locator('#ingot-form button').click();page.wait_for_function("document.querySelector('#ingot-result').textContent.includes('30 METAL')")
    page.locator('#recipe').select_option('narcotic_chemistry');page.locator('#craft-quantity').fill('7');page.locator('#craft-form button').click()
    page.wait_for_function("document.querySelector('#craft-result').textContent.includes('40')")
    assert '12' in page.locator('#craft-result').inner_text()
    page.locator('#recipe').select_option('smithy');page.locator('#craft-quantity').fill('2');page.locator('#craft-stock').fill('{"Stone":100,"Metal Ingot":3,"Metal":4}');page.locator('#expand-ingots').check();page.locator('#craft-form button').click()
    page.wait_for_function("document.querySelector('#craft-result').textContent.includes('Metal: 14 → 10')")
    page.locator('#roi-name-1').fill('Anky');page.locator('#roi-utility-1').fill('60');page.locator('#roi-hours-1').fill('2')
    page.locator('#roi-name-2').fill('Argy');page.locator('#roi-utility-2').fill('80');page.locator('#roi-hours-2').fill('2');page.locator('#roi-form button').click()
    page.wait_for_function("document.querySelector('#roi-result').textContent.includes('Argy')")
    assert page.locator('#roi-result li').first.inner_text().startswith('Argy')
    page.locator('#inherit-stats').fill('2');page.locator('#inherit-events').fill('1');page.locator('#inherit-form button').click()
    page.wait_for_function("document.querySelector('#inherit-result').textContent.includes('30.25%')")
    page.locator('#forge-ingots').fill('150');page.locator('#forge-fuel').select_option('wood');page.locator('#forge-form button').click()
    page.wait_for_function("document.querySelector('#forge-result').textContent.includes('100 WOOD')")
    page.locator('#queue-recipe-1').select_option('narcotic_chemistry');page.locator('#queue-qty-1').fill('3')
    page.locator('#queue-recipe-2').select_option('narcotic_chemistry');page.locator('#queue-qty-2').fill('3')
    page.locator('#queue-stock').fill('{"Narcoberry":5}');page.locator('#queue-form button').click()
    page.wait_for_function("document.querySelector('#queue-result').textContent.includes('Narcoberry: 20 → 15')")
    page.screenshot(path='docs/screenshots/calculators.png',full_page=True)
    page.goto('http://127.0.0.1:8000/#operations',wait_until='networkidle')
    page.locator('#readiness-form input').first.check();page.locator('#readiness-form button').click();page.wait_for_function("document.querySelector('#readiness-result').textContent.includes('20 / 100')")
    page.locator('#rate-taming').fill('5');page.locator('#config-form button').click();page.wait_for_function("document.querySelector('#config-result').textContent.includes('TamingSpeedMultiplier=5')")
    page.goto('http://127.0.0.1:8000/#atlas',wait_until='networkidle')
    forms=page.locator('.board-form');forms.first.locator('[name=entry-name]').fill('Metal run');forms.first.locator('[name=entry-note]').fill('The Island 25, 45');forms.first.locator('button').click()
    assert page.get_by_text('Metal run').count() == 1
    page.reload(wait_until='networkidle');assert page.get_by_text('Metal run').count() == 1
    page.locator('[data-type="waypoints"]').locator('..').locator('[data-del="0"]').click();assert page.get_by_text('Metal run').count()==0
    page.locator('#pin-name').fill('Demo waypoint');page.locator('#pin-lat').fill('25.3');page.locator('#pin-lon').fill('73.1');page.locator('#pin-form button').click()
    assert page.locator('.grid-pin').count()==1
    assert '25.3' in page.locator('.grid-key').inner_text()
    page.locator('#grid-world').select_option('Ragnarok');assert page.locator('.grid-pin').count()==0
    page.locator('#grid-world').select_option('The Island');assert page.locator('.grid-pin').count()==1
    page.reload(wait_until='networkidle');assert page.locator('.grid-pin').count()==1
    page.screenshot(path='docs/screenshots/atlas.png',full_page=True)
    page.goto('http://127.0.0.1:8000/#expedition',wait_until='networkidle')
    page.locator('#tribute-difficulty').select_option('beta');page.locator('#tribute-runs').fill('2');page.locator('summary').click();page.locator('#tribute-stock-3').fill('4');page.locator('#tribute-form button').click()
    page.wait_for_function("document.querySelector('#tribute-result').textContent.includes('Argentavis Talon: 10 → 6')")
    page.locator('#egg-name-1').fill('Demo egg A');page.locator('#egg-low-1').fill('10');page.locator('#egg-high-1').fill('20')
    page.locator('#egg-name-2').fill('Demo egg B');page.locator('#egg-low-2').fill('20');page.locator('#egg-high-2').fill('30');page.locator('#mixer-form button').click()
    page.wait_for_function("document.querySelector('#mixer-result').textContent.includes('20 °C · 2/2')")
    page.locator('#route-lat').fill('0');page.locator('#route-lon').fill('0');page.locator('#route-form button').click()
    page.wait_for_function("document.querySelector('#route-result').textContent.includes('Demo waypoint')")
    page.locator('#window-name-1').fill('Demo raid');page.locator('#window-start-1').fill('2026-11-24T10:00');page.locator('#window-end-1').fill('2026-11-24T12:00')
    page.locator('#window-name-2').fill('Demo hatch');page.locator('#window-start-2').fill('2026-11-24T11:00');page.locator('#window-end-2').fill('2026-11-24T13:00');page.locator('#windows-form button[value=compare]').click()
    page.wait_for_function("document.querySelector('#windows-result').textContent.includes('1 CONFLICT(S)')")
    assert '60 min overlap' in page.locator('#windows-result').inner_text()
    assert '<t:1795514400:F>' in page.locator('#windows-result').inner_text()
    assert page.locator('.route-plot').count()==1 and 'Leg 1:' in page.locator('#route-result').inner_text()
    page.locator('#windows-form button[value=save]').click();page.wait_for_function("document.querySelector('#windows-result').textContent.includes('Set saved in this browser')")
    page.screenshot(path='docs/screenshots/expedition.png',full_page=True)
    page.reload(wait_until='networkidle');assert page.locator('#window-name-1').input_value()=='Demo raid'
    page.locator('#window-name-1').fill('Compare only');page.locator('#windows-form button[value=compare]').click()
    page.wait_for_function("document.querySelector('#windows-result').textContent.includes('saved set unchanged')")
    page.reload(wait_until='networkidle');assert page.locator('#window-name-1').input_value()=='Demo raid'
    page.locator('#window-end-1').fill('2026-11-24T09:00');page.locator('#windows-form button[value=save]').click()
    page.wait_for_function("document.querySelector('#windows-result').textContent.includes('End must be later than start')")
    page.reload(wait_until='networkidle');assert page.locator('#window-end-1').input_value().startswith('2026-11-24T12:00')
    page.locator('#window-name-2').fill('');page.locator('#window-start-2').fill('');page.locator('#window-end-2').fill('')
    page.locator('#window-name-4').fill('Fourth window');page.locator('#window-start-4').fill('2026-11-24T11:00');page.locator('#window-end-4').fill('2026-11-24T13:00')
    page.locator('#windows-form button[value=compare]').click();page.wait_for_function("document.querySelector('#windows-result').textContent.includes('Fourth window (event 4)')")
    page.goto('http://127.0.0.1:8000/#atlas',wait_until='networkidle')
    page.locator('#pin-name').fill('Second demo');page.locator('#pin-lat').fill('10');page.locator('#pin-lon').fill('15');page.locator('#pin-form button').click()
    page.goto('http://127.0.0.1:8000/#expedition',wait_until='networkidle')
    assert page.locator('[name=route-pin]').count()==2
    page.locator('[name=route-pin]').first.uncheck();page.locator('#route-lat').fill('0');page.locator('#route-lon').fill('0');page.locator('#route-form button').click()
    page.wait_for_function("document.querySelector('#route-result').textContent.includes('Second demo')")
    assert 'Demo waypoint' not in page.locator('#route-result').inner_text()
    # More than eight saved pins are usable by selecting a subset, including later pins.
    page.evaluate("""() => {let d=JSON.parse(localStorage.getItem('omnisuite.records.v1')); for(let i=0;i<8;i++) d.waypoints.push({name:'Extra demo '+i,note:'test',world:'The Island',lat:i+1,lon:i+1});localStorage.setItem('omnisuite.records.v1',JSON.stringify(d))}""")
    page.reload(wait_until='networkidle');assert page.locator('[name=route-pin]').count()==10
    assert page.locator('[name=route-pin]:checked').count()==8
    page.locator('[name=route-pin]:checked').first.uncheck();page.locator('[name=route-pin]').last.check()
    page.locator('#route-lat').fill('0');page.locator('#route-lon').fill('0');page.locator('#route-form button').click()
    page.wait_for_function("document.querySelector('#route-result').textContent.includes('Extra demo 7')")
    page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.set_viewport_size({'width':1440,'height':1000})

    # Export a new backup; malformed or cancelled imports must not replace it.
    page.goto('http://127.0.0.1:8000/#boards',wait_until='networkidle')
    with page.expect_download() as download_info: page.locator('#export').click()
    backup=json.loads(Path(download_info.value.path()).read_text())
    assert len(backup['savedWindows'])==2 and backup['savedWindows'][0]['name']=='Demo raid'
    def upload(obj):
        page.locator('#import').set_input_files({'name':'records.json','mimeType':'application/json','buffer':json.dumps(obj).encode()})
    bad=dict(backup);bad['savedWindows']=[{'name':'bad','start':'not a date','end':'2027-01-01T00:00:00.000Z'}]
    upload(bad);page.wait_for_function("document.querySelector('#import-status').textContent.includes('Invalid saved event windows')")
    assert len(page.evaluate("JSON.parse(localStorage.getItem('omnisuite.records.v1')).savedWindows"))==2
    legacy=dict(backup);legacy.pop('savedWindows')
    with page.expect_event('dialog') as prompt: upload(legacy)
    prompt.value.dismiss()
    assert len(page.evaluate("JSON.parse(localStorage.getItem('omnisuite.records.v1')).savedWindows"))==2
    with page.expect_event('dialog') as prompt: upload(legacy)
    prompt.value.accept()
    page.wait_for_function("JSON.parse(localStorage.getItem('omnisuite.records.v1')).savedWindows.length===0")
    assert len(page.evaluate("JSON.parse(localStorage.getItem('omnisuite.records.v1')).waypoints"))==len(legacy['waypoints'])
    with page.expect_event('dialog') as prompt: upload(backup)
    prompt.value.accept()
    page.wait_for_function("JSON.parse(localStorage.getItem('omnisuite.records.v1')).savedWindows.length===2")
    page.goto('http://127.0.0.1:8000/#expedition',wait_until='networkidle');assert page.locator('#window-name-1').input_value()=='Demo raid'
    page.once('dialog',lambda dialog: dialog.dismiss());page.locator('#windows-clear').click();assert page.locator('#window-name-1').input_value()=='Demo raid'
    page.once('dialog',lambda dialog: dialog.accept());page.locator('#windows-clear').click()
    assert page.locator('#window-name-1').input_value()==''
    assert len(page.evaluate("JSON.parse(localStorage.getItem('omnisuite.records.v1')).waypoints"))==len(backup['waypoints'])
    page.locator('#theme').click();assert page.locator('html').get_attribute('data-theme')=='light'
    page.reload(wait_until='networkidle');assert page.locator('html').get_attribute('data-theme')=='light'
    page.set_viewport_size({'width':390,'height':844});page.goto('http://127.0.0.1:8000/#overview',wait_until='networkidle');page.screenshot(path='docs/screenshots/mobile.png',full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors, errors
    print('Browser smoke passed: event saving, legacy/new backup import and export, route legs and diagram, pin selection, tribute, incubation, routing, recipes, queue, inheritance, forge, ROI, readiness, configuration, grid plotting, world filtering, persistence, deletion, theme, mobile, no page errors.')
    browser.close()
