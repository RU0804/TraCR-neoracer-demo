import math
import pytest
from tracr_demo.core import Pairer, Invalid, unity_pose, cosim_payload, Pose
from tracr_demo.server import DEFAULT


def pose(t=100., **changes):
    return {"id":str(t),"capture_time":t,"time_basis":"capture","frame_id":"map",
            "x":1.,"y":2.,"z":.2,"yaw":0.,"quality":"localized","source":"test-input",**changes}


def video(t=100., **changes):
    return {"id":"f"+str(t),"capture_time":t,"time_basis":"capture","source":"test-input",**changes}


@pytest.fixture
def rig():
    clock=[100.]
    return Pairer(DEFAULT,clock=lambda:clock[0]),clock


def test_cardinal_axes_and_yaw():
    p=Pose.parse(pose(yaw=math.pi/2),100,2)
    converted=unity_pose(p)
    assert (converted['ux'],converted['uy'],converted['uz']) == (-2,.2,1)
    assert converted['qy'] == pytest.approx(-math.sqrt(.5))
    payload=cosim_payload(p)
    assert all(isinstance(v,str) for v in payload.values())
    assert payload['V1 PosY']=='2.0'  # No double Unity-axis conversion on Socket wire.


def test_pair_uses_nearest_source_time_and_rejects_duplicate_reply(rig):
    p,clock=rig
    p.add_pose(pose(99.96)); p.add_pose(pose(100.))
    p.add_frame(video(99.98),b'jpeg')
    offer=p.offer()
    assert offer and p.offer() is None
    f,po=p.finish(offer['ticket'],offer['frame_id'],offer['pose_id'])
    assert abs(f.capture_time-po.capture_time) <= .021
    with pytest.raises(Invalid): p.finish(offer['ticket'],offer['frame_id'],offer['pose_id'])


def test_wrong_render_ids_do_not_consume_valid_ticket(rig):
    p,_=rig; p.add_pose(pose());p.add_frame(video(),b'jpeg'); o=p.offer()
    with pytest.raises(Invalid): p.finish(o['ticket'],'wrong',o['pose_id'])
    p.finish(o['ticket'],o['frame_id'],o['pose_id'])


def test_skew_and_stale_sources_never_offer(rig):
    p,clock=rig;p.add_pose(pose(99.8));p.add_frame(video(),b'jpeg')
    assert p.offer() is None
    clock[0]=101
    assert not p.status()['video_fresh'] and not p.status()['pose_fresh']
    assert p.offer() is None


def test_loss_invalidates_pending_and_cannot_resurrect_old_pose(rig):
    p,clock=rig;p.add_pose(pose());p.add_frame(video(),b'jpeg');o=p.offer()
    clock[0]=100.1;p.add_pose({"capture_time":100.1,"time_basis":"capture","quality":"lost"})
    with pytest.raises(Invalid):p.finish(o['ticket'],o['frame_id'],o['pose_id'])
    with pytest.raises(Invalid):p.add_pose(pose(100.05))
    assert p.offer() is None and not p.status()['pose_fresh']


def test_late_render_rejected_then_new_frame_recovers(rig):
    p,clock=rig;p.add_pose(pose());p.add_frame(video(),b'jpeg');o=p.offer()
    clock[0]=100.7
    with pytest.raises(Invalid):p.finish(o['ticket'],o['frame_id'],o['pose_id'])
    p.add_pose(pose(100.7));p.add_frame(video(100.7),b'jpeg')
    assert p.offer()


@pytest.mark.parametrize('changes',[{'x':float('nan')},{'yaw':float('inf')},{'x':True},
    {'frame_id':'odom'},{'time_basis':'unknown'},{'capture_time':103},{'capture_time':97},
    {'quality':'valid'},{'id':''},{'x':'1.0'}])
def test_invalid_pose_rejected(rig,changes):
    with pytest.raises(Invalid):rig[0].add_pose(pose(**changes))


def test_out_of_order_input_rejected(rig):
    p,_=rig;p.add_pose(pose());p.add_frame(video(),b'jpeg')
    with pytest.raises(Invalid):p.add_pose(pose(99.99))
    with pytest.raises(Invalid):p.add_frame(video(99.99),b'jpeg')


def test_bounded_memory_and_receipt_time_never_verified(rig):
    p,clock=rig
    for i in range(200):
        clock[0]=100+i*.01
        p.add_pose(pose(clock[0],time_basis='receipt'))
        p.add_frame(video(clock[0],time_basis='receipt'),b'jpeg')
    assert len(p.poses)==len(p.frames)==DEFAULT['buffer_size']
    assert not p.status()['timing_verified']


def test_render_freshness_uses_source_age_and_loss_not_receipt_time(rig):
    p,clock=rig;p.add_pose(pose());p.add_frame(video(),b'jpeg');o=p.offer()
    clock[0]=100.5;p.finish(o['ticket'],o['frame_id'],o['pose_id'])
    assert p.status()['render_fresh']
    clock[0]=100.8
    assert not p.status()['render_fresh']
    p.add_pose(pose(100.8));p.add_frame(video(100.8),b'jpeg');o=p.offer()
    p.finish(o['ticket'],o['frame_id'],o['pose_id'])
    p.add_pose({'capture_time':100.8,'time_basis':'receipt','quality':'lost'})
    assert not p.status()['render_fresh']
