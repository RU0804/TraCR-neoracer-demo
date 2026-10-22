# AutoDRIVE / NeoRacer Unity 接入

**交付的是集成源码，当前环境没有 Unity Editor，尚未编译、构建或运行 NeoRacer 场景。** HTTP 协议测试使用仿造 Unity 客户端；它不能替代这一节的验收。

## 版本与导入

1. 在笔记本仓库根目录运行 `python scripts/fetch_autodrive.py`。它只下载 `upstream.lock.json` 中的固定源码，不安装系统包、不执行厂商一键安装脚本。Unity 资产较大，需预留磁盘和下载时间。下载过程中断时，保留或手动移走不完整目录，再重试到空目录。
2. 使用锁定源码要求的 Unity **2022.3.52f1** 打开 `upstream/AutoDRIVE-Simulator`。如 Git LFS 指针未获取完整，先在该仓库执行 `git lfs pull` 并核对资产。具体平台图形 API 和驱动要在演示笔记本测试。
3. 将 `unity/TraCRPoseFollower.cs` 复制到上游工程 `Assets/TraCR/`，将 `unity/TraCRMapBuilder.cs` 放到 `Assets/TraCR/Editor/`。
4. 选择 NeoRacer 场景（源树含 `NeoRacer - AuE-X930`），或在副本场景中放置 `Assets/Prefabs/NeoRacer/NeoRacer.prefab`。不要把旧 Nigel 0.2.0 二进制称作 NeoRacer 构建。
5. 保存独立场景副本，保留上游原场景。使用菜单 `TraCR / Import measured road layout JSON` 导入测量好的道路。`configs/map.example.json` 是 **ILLUSTRATIVE ONLY**，其尺寸不能当作真实赛道。导入器只添加地面与道路块；标线、泡沫板边界、路标、弯道细节仍需按测量制作。

## 跟随组件

在场景中新建 `TraCR Bridge` GameObject 并挂载 `TraCRPoseFollower`：

- `CoSim` 指向 NeoRacer 所属的 `CoSimManager`，其 `VehicleRigidBody` 指向实际车辆刚体；若 prefab 没有该组件，在正确车辆父对象添加并赋值。
- `DisplayCamera` 指向用于右侧显示的实际 Unity 相机。可用车载相机作同视角对照，也可选择第三人称跟车相机。先选定一种并在现场彩排中固定。
- `DisableWhileFollowing` 显式列出原 Socket、车辆/汽车/驱动控制器以及其他会改写刚体的脚本。展示链路不启动官方实车命令链。检查场景中没有第二个程序继续改写车辆位姿。
- 原 Socket.IO 连接必须先断开，并停止相应服务器/客户端。仅禁用 MonoBehaviour 不会自动移除已经注册的 Socket 事件回调，不能只依赖组件禁用列表。
- 设置 `ServerUrl=http://127.0.0.1:8080`；如设置了 token，在启动 Unity Hub/Editor 或 Player 的同一环境中设置 `TRACR_TOKEN`，不要保存到场景。
- 配置 `BodyOriginOffset`：地图位姿所代表车体点到 prefab 刚体原点的偏移，单位米，车体 +x 前、+y 左、+z 上。`PrefabYawOffsetDegrees` 只用于模型朝向校正。先验证原点和三个朝向，避免盲目调符号。
- 确认引用正确后在 Inspector 勾选 `FollowMeasuredPose`。组件进入运动学位姿跟随，禁用竞争控制器，并在收到目标后捕获相机。取消勾选或禁用组件后恢复原控制器启用状态与刚体设置；切换回动力学模式前需重新检查初始状态。

组件使用上游 CoSim 的目标字段和直接更新路径，并显式施加刚体位姿以避免默认平滑引入未知滞后。它不依赖旧 Socket.IO 协议库，也不宣称已经验证旧 Bridge 图像与采样时间的对应关系。`core.cosim_payload()` 仅保留原生协议序列化参考，未实现全场景 Socket.IO 服务器。

当前相机捕获实现使用内置渲染管线 `Camera.Render()`；若改为 URP/HDRP，需要改成对应管线的捕获钩子并验证。跟随相机若有插值，会影响观看效果；车辆本身不做动力学预测。`WaitForEndOfFrame` 依赖正常图形帧，不适合 `-nographics` 或不更新游戏视图的 Editor 状态。

## 必须实测的验收

- 车辆在地图 (0,0)、+x、+y 和 yaw=0、+90°、180° 的位置/方向一致；车体参考点正确，轮胎与地面高度合理。
- 右侧图像来自 NeoRacer prefab 的指定相机，并随已知输入移动；不是旧的 Tiny Town Nigel 图像。
- 显示相机跟随时没有其他脚本在捕获前后改写车体。Inspector/Profiler 核查实际渲染、编码速率和 CPU/GPU 使用率。
- 断定位后车辆保持最后位置，网页明确标为过期；重连产生新的有效配对。
- 在实际笔记本构建并冷启动；验证离线网络、屏幕分辨率、电源设置和投影/外接显示器。

官方参考：[CoSimManager](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/CoSimManager.cs)、[Socket 坐标变换](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/Socket.cs)。
