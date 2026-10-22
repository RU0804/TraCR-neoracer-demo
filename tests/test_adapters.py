import ast
import base64
import importlib.util
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
import pytest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from apriltag import tag_pose
from ros2_readonly import image_jpeg


def test_ros_adapter_has_no_publishers_or_control_clients():
    tree=ast.parse((ROOT/'adapters/ros2_readonly.py').read_text())
    calls={n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
    assert not calls.intersection({'create_publisher','create_client','publish'})


def test_ros_jpeg_inside_image_and_bgr_step_supported():
    im=Image.new('RGB',(32,24),'red');out=io.BytesIO();im.save(out,format='JPEG')
    jpeg=image_jpeg(SimpleNamespace(data=out.getvalue(),encoding='jpeg',width=0,height=0,step=0))
    assert Image.open(io.BytesIO(base64.b64decode(jpeg))).size==(32,24)
    pixels=bytes([0,0,255]*32+[0,0,0,0])*24
    jpeg=image_jpeg(SimpleNamespace(data=pixels,encoding='bgr8',width=32,height=24,step=100))
    pixel=Image.open(io.BytesIO(base64.b64decode(jpeg))).getpixel((10,10))
    assert pixel[0]>240 and pixel[2]<10


def test_tag_heading_and_body_offset():
    corners=np.array([[[0,0],[2,0],[2,2],[0,2]]],dtype=np.float32)
    cal={'camera_matrix':[[1,0,0],[0,1,0],[0,0,1]],'distortion':[0,0,0,0,0],
         'pixel_to_map':[[1,0,0],[0,-1,2],[0,0,1]],'yaw_offset_rad':0,
         'tag_to_base_xy_m':[.2,0], 'base_z_m':.1}
    pose=tag_pose(corners,cal)
    assert pose['x']==pytest.approx(1)
    assert pose['y']==pytest.approx(1.2)
    assert pose['yaw']==pytest.approx(np.pi/2)
