# TraCR-neoracer-demo

NeoRacer V1 现场展示软件：**左侧车载视频，右侧跟随实测位姿的 AutoDRIVE 虚拟视角**。目标部署是师兄的笔记本和现场局域网，场地约 5 m × 5 m。

**当前为可运行的软件原型，尚未完成 NeoRacer 实车与 Unity 联调。** 自检模式中的两幅图均为合成测试画面，不是实车录像，也不是 AutoDRIVE 渲染。已有 Nigel 离线仿真属于此前的独立成果。

## 当前状态

| 内容 | 状态 |
|---|---|
| 本地双画面、时间配对、断流提示、全屏与手机布局 | 已实现；验证记录见 [VALIDATION](docs/VALIDATION.md) |
| 有限视频/位姿缓冲、单个在途渲染请求、回执校验 | 已实现，协议测试覆盖 |
| USB / RTSP / HTTP MJPEG 视频适配器 | 已实现；尚未接真实相机 |
| ROS 2 相机与位姿只读适配器 | 已实现；JPEG 解码有测试，ROS 运行时未验证 |
| 可选 AprilTag 俯视定位与标定工具 | 已实现；几何单元测试，实际相机与检测性能待验证 |
| AutoDRIVE CoSim 跟随及渲染回执组件 | 已提供 C# 源码；尚未在 Unity 编译/运行 |
| 5 m × 5 m 道路导入器 | 已提供；示例布局不代表真实泡沫板地图 |
| NeoRacer 实车同屏同步、真实延迟和空间误差 | **未验证，需现场设备** |
| 自动驾驶控制、SLAM、新车辆动力学验证 | 不在当前实现范围 |

## 不接硬件先运行

建议笔记本使用 Python 3.10 或 3.11。当前自动检查环境为 Linux / Python 3.9；Windows 与 macOS 尚未实机验证。前端没有 CDN、Node 或云服务依赖。

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell 改用：.venv\Scripts\Activate.ps1
python -m pip install -e ".[camera,test]"
tracr-demo --self-test
```

浏览器打开 <http://127.0.0.1:8080>。屏幕会持续显示 **SYNTHETIC SELF-TEST**。退出服务用 Ctrl+C。

正式输入模式：

```bash
tracr-demo --config configs/demo.json
```

没有真实数据时会显示等待状态，不会自动切换成假车或历史录像。

## 接入现场设备

1. **相机**：在第二个终端启动适配器。例如 USB 摄像头 `python adapters/camera.py --source 0`；已有 RTSP 则 `python adapters/camera.py --source rtsp://CAMERA_HOST/STREAM`。后者必须换成真实地址。编码格式、驱动、网络连通性待现场核验。
2. **定位**：输入地图坐标中的实测位置、朝向。已有可靠 ROS 2 定位时使用 `adapters/ros2_readonly.py`；可安装俯视相机时使用 `adapters/apriltag.py`。单独车载前视视频不会自动得到绝对位姿。详见 [接车与标定](docs/CALIBRATION.md)。
3. **AutoDRIVE**：按 [Unity 接入](docs/UNITY.md) 获取锁定源码，配置 NeoRacer prefab、相机、场景和 `TraCRPoseFollower`，在笔记本运行 Editor 或构建的程序。
4. **场地**：按 [泡沫板地图制作流程](docs/MAP_WORKFLOW.md) 测量道路，建立对应 Unity 场景。当前导入器支持直线矩形道路段；示例不是实测地图，弯道、标线和立体边界需继续制作。
5. **彩排**：按 [现场运行手册](docs/RUNBOOK.md) 验证直行、转向、断流恢复、空间对齐和两路延迟。

相机、定位和 Unity 可以独立启动。只有时间差在容差内、Unity 回执对应正确视频/位姿 ID 时，才显示配对双画面。详见 [协议](docs/PROTOCOL.md)。

## 仓库结构

```text
tracr_demo/        Python 服务和无外部资源依赖的浏览器界面
adapters/          视频、ROS 2 只读和俯视 AprilTag 适配器
unity/             AutoDRIVE 跟随、渲染回执和道路导入源码
configs/           配置与未标定示例
scripts/           标定、数据统计、上游获取、Slurm 验证
tests/            协议、时间异常、断流和坐标转换测试
docs/             部署、接车、验证、来源和发布说明
upstream.lock.json 固定上游源码与 Unity 版本
```

运行 `python -m pytest -q` 检查软件逻辑。浏览器检查见 `docs/VALIDATION.md`。`requirements-tested-linux-py39.txt` 记录本次 Linux 的精确依赖；其他平台按 `pyproject.toml` 安装并重新验收。

## Gilbreth 与 GitHub

Gilbreth 上的实质计算和浏览器渲染通过 Slurm；优先 `sukkusur / a100-40gb / normal`，额度占用或排队时才选 `a30 / standby`。完整演示禁止 A10。`scripts/submit_validation.sh` 每次读取组内额度，A30 配额变化时停止并要求重新核查。见 [GPU 约束](docs/GILBRETH.md)。这不代表 AutoDRIVE 的 Vulkan 路径已在 A100/A30 验证。

仓库不包含 Unity 二进制、大型上游资产、实车录像、网络密码或虚构的实体测试结果。GitHub 发布步骤与许可证状态见 [PUBLISH](docs/PUBLISH.md)。来源边界见 [PROVENANCE](docs/PROVENANCE.md)。
