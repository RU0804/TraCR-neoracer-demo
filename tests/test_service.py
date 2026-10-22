import asyncio
import base64
import time
import pytest
from aiohttp.test_utils import TestServer, TestClient
from tracr_demo.server import create_app, test_image as make_image
from tracr_demo.core import Invalid
from test_pairing import pose,video


@pytest.fixture
async def client():
    async with TestClient(TestServer(create_app())) as c:
        yield c


async def test_camera_pose_unity_round_trip(client):
    now=time.time(); jpeg=base64.b64encode(make_image(0)).decode()
    assert (await client.post('/api/camera',json={**video(now),'jpeg':jpeg})).status==200
    assert (await client.post('/api/pose',json=pose(now))).status==200
    target=await (await client.get('/api/unity/next')).json()
    assert target['ux']==-2
    response=await client.post('/api/unity/frame',json={**target,'jpeg':jpeg})
    assert response.status==200,await response.text()
    async with client.ws_connect('/ws') as ws:
        await ws.send_json({'token':''})
        status=await ws.receive_json(); pair=await ws.receive_json()
        assert status['accepted_pairs']==1 and not status['timing_verified']
        assert pair['renderer']=='autodrive' and pair['frame_id']==target['frame_id']
        assert pair['pose_id']==target['pose_id'] and pair['left']==jpeg
    assert (await client.post('/api/unity/frame',json={**target,'jpeg':jpeg})).status==400


async def test_missing_pose_never_fabricates_simulator(client):
    jpeg=base64.b64encode(make_image(0)).decode()
    await client.post('/api/camera',json={**video(time.time()),'jpeg':jpeg})
    assert (await client.get('/api/unity/next')).status==204
    async with client.ws_connect('/ws') as ws:
        await ws.send_json({'token':''})
        await ws.receive_json()
        frame=await ws.receive_json()
        assert frame['type']=='video' and 'right' not in frame


async def test_malformed_input_and_wrong_origin(client):
    assert (await client.post('/api/pose',json=[])).status==400
    assert (await client.post('/api/camera',json={**video(time.time()),'jpeg':'bad'})).status==400
    assert (await client.post('/api/pose',json=pose(time.time()),headers={'Origin':'http://evil.example'})).status==403
    assert (await client.get('/static/missing')).status==404


async def test_auth_required_for_lan_and_ws():
    with pytest.raises(Invalid):create_app({'host':'0.0.0.0'})
    async with TestClient(TestServer(create_app(token='test-token'))) as c:
        assert (await c.get('/api/status')).status==401
        assert (await c.get('/api/status',headers={'Authorization':'Bearer test-token'})).status==200
        async with c.ws_connect('/ws') as ws:
            await ws.send_json({'token':'wrong'})
            await ws.receive()
            assert ws.close_code==1008


async def test_selftest_is_labeled_and_rejects_physical_input():
    async with TestClient(TestServer(create_app(self_test=True))) as c:
        await asyncio.sleep(.15)
        status=await (await c.get('/api/status')).json()
        assert status['mode']=='self-test' and status['pose_quality']=='test'
        assert not status['timing_verified'] and status['accepted_pairs']>0
        assert (await c.post('/api/pose',json=pose(time.time()))).status==409
        assert (await c.get('/api/unity/next')).status==409


async def test_unexpected_host_rejected(client):
    response=await client.get('/api/status',headers={'Host':'untrusted.example'})
    assert response.status==403
