# 输入与渲染协议

本地 HTTP 服务默认 `127.0.0.1:8080`。接口体是 JSON，最大 3 MB。JPEG 最大 1920×1080、约 2 MB 解码前二进制。每个视频/位姿环形缓冲默认最多 40 项；只有一个在途 Unity 请求。过期数据不排队补播。

## 视频

`POST /api/camera`：

```json
{"id":"camera-session:42","capture_time":1790000000.125,"time_basis":"capture","source":"onboard-camera","jpeg":"BASE64_JPEG"}
```

时间是 **UTC Unix 秒**。例子时间只说明格式，不能原样发送。`time_basis=capture` 只有在来源确实提供曝光/采样时间且已换算到服务时钟时使用；否则为 `receipt`。OpenCV 适配器使用收到解码帧的时间，无法测出摄像头编码、网络和内部缓冲造成的延迟。

## 位姿

`POST /api/pose`：

```json
{"id":"localizer-session:42","capture_time":1790000000.125,"time_basis":"capture","source":"real-localizer","frame_id":"map","quality":"localized","x":1.2,"y":0.8,"z":0.0,"yaw":1.5707963268}
```

地图右手坐标，米、弧度：+x 为车辆零朝向，+y 左向，+z 向上，yaw 从 +x 朝 +y 逆时针。位置对应选定车体参考点，必须与 Unity 偏移配置一致。`quality=odometry` 表示相对里程计，页面持续提示漂移。`quality=test` 仅用于合成自检。

定位丢失可立即发送 `{"capture_time":当前UTC秒,"time_basis":"receipt","quality":"lost"}`。丢失会清空位姿缓冲并作废在途渲染；停止发数据也会触发超时。不要重发旧位姿并盖上新的采样时间。不要混入仿真 `/odom`。

所有数字必须有限，时间戳单调递增。默认拒绝超过 2 秒的输入和领先服务时钟超过 50 ms 的输入。数据新鲜阈值为 750 ms，默认视频/位姿匹配差不超过 80 ms。这些是可调工程门限，不是已经测到的性能。

## Unity 拉取与回执

`GET /api/unity/next`：无可匹配新视频返回 204；否则给出 `ticket, frame_id, pose_id, capture_time, pose_time, ux,uy,uz,qx,qy,qz,qw`。选择最新视频和时间最接近的位姿，不做运动预测或外推。

从地图到 Unity 的转换与锁定版 `Socket.cs` 一致：位置 `(-y,z,x)`，平面旋转四元数 `(0,-sin(yaw/2),0,cos(yaw/2))`。若走原生 Socket.IO，使用 `core.cosim_payload()` 发地图坐标，由 Socket.cs 转换；不能重复转换。

Unity 将目标施加到虚拟车、等待跟随相机更新、显式渲染指定相机，再 `POST /api/unity/frame`：

```json
{"ticket":"SERVER_TICKET","frame_id":"camera-session:42","pose_id":"localizer-session:42","jpeg":"BASE64_RENDERED_JPEG"}
```

票据必须存在且 ID 完全匹配；过期（默认 600 ms）、重复或倒序回执被拒绝。此回执是组件声明该图使用了该位姿，不是独立视觉定位或物理精度证据。需要 Unity 实际接入验证组件执行顺序与场景中的其他脚本。

浏览器 `/ws` 先发送 `{"token":"..."}`，随后接收状态和成对图像。前端解码完两张图后在同一次浏览器绘制回调更新。网络/显示刷新仍会产生延迟，不能把同次 DOM 更新等同于曝光同步或显示器扫描同步。无匹配渲染时显示新视频并将保留的仿真画面标过期。

## 指标与时钟

`/api/status` 的 P95 来源为最近 600 个成功配对：视频时间到服务收到渲染回执的年龄、视频时间与位姿时间之差。它们不包含浏览器传输、解码、显示刷新；receipt 模式更不包含视频原有传输延迟。`clock_verified=false` 为默认值；仅在有时钟校准记录后手动设 true。它是操作者声明，不是自动测时结果。

设备与笔记本用可验证的 NTP/PTP 或测得的偏差统一时钟；ROS `use_sim_time` 必须关闭。启动前实测时间源是否为曝光、发布还是驱动收到时间。ROS 适配器默认也使用 receipt，`--capture-timestamps --clock-offset-s OFFSET` 必须明确开启。服务重启会清空会话与统计。

## 局域网接入

同机部署默认不需 token。监听非回环地址时，必须设置至少 20 字符的 `TRACR_TOKEN`。HTTP 接口使用 `Authorization: Bearer ...`；浏览器通过密码框填入 token（只存当前标签页会话）；Unity 从同名环境变量读取。不要把 token 写进场景或提交到 Git。

默认拒绝浏览器跨源请求。明文 HTTP 只适合受控演示局域网；若跨不可信网络，应在前面加 TLS。服务不提供任何实车驾驶、油门、转向或 ROS 发布接口。
