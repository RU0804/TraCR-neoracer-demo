# 接车与空间标定

现场目标为车载前视视频 + 虚拟场景。**车载视频本身不等于地图定位**；想让虚拟车跟随，需要持续获取真实车的地图位置、朝向和时间。第一版保持遥控驾驶，展示程序只读取状态。

## 优先复用现有定位

先在真实车上核查系统、ROS 版本、实际话题与编码；不要把上游标准配置当成这台车的事实。可只读运行：

```bash
ros2 topic list -t
ros2 topic info /camera/color -v
ros2 topic info /odom -v
ros2 topic hz /camera/color
```

话题名字是候选，需要以实际列表为准。相机可能是 `Image` 携带 JPEG、标准 RGB/BGR 原图或 `CompressedImage`。适配器支持这几种常用路径；其他编码会明确报错。

在已安装 ROS 2 的环境运行。若用 venv，应使用相同系统 Python 并用 `python3 -m venv --system-site-packages .venv-ros` 让 `rclpy` 可见，再安装本仓库。不要在 Gilbreth 直接运行 NeoRacer 官方的系统安装/服务启用脚本。

```bash
# source /opt/ros/humble/setup.bash（版本以实车为准）
# 若确有地图定位 PoseStamped：
python adapters/ros2_readonly.py --image-topic /camera/color --pose-topic /localization/pose
# 若只有 Odometry（必须测量初始 odom->map 变换）：
python adapters/ros2_readonly.py --image-topic /camera/color --pose-topic /odom \
  --odometry --transform configs/local.odom_to_map.json
```

`PoseStamped` 默认必须 `frame_id=map`；其他坐标需要显式变换。地图姿态不一定包含可信定位质量，该来源必须自行判断跟踪丢失。适配器目前不推断 SLAM 算法置信度；如果定位器在失败时继续发布旧姿态和新时间戳，需另加该算法的质量状态适配，不能指望本服务自动识别。仅 `/odom` 有初始对齐也会逐步漂移。

只启动真实车 ROS 数据接收，不启动 AutoDRIVE 官方仿真 ROS bridge。不创建 `/drive`、`/mux_out`、`/motor` 等控制发布器。若还要同时运行仿真 ROS，使用不同 ROS_DOMAIN_ID 和命名空间/网络隔离，确保模拟 `/odom`、`/scan` 不会进入此适配器。

## 可选：俯视 AprilTag

如果没有可靠地图定位，可以在车顶装 AprilTag 36h11，俯视固定相机仅承担定位；左侧仍显示车载相机。5 m × 5 m 的覆盖、遮挡和小标记分辨率都要现场测，不能保证单摄像头一定足够。

1. 选择固定坐标原点、+x、+y、单位米。测量道路中心线、路宽、路口、边界，并写入独立地图 JSON。将纸质/地面坐标标识与 Unity 原点对应。
2. 固定俯视相机焦距、分辨率和位置，使用棋盘格标定内参/畸变。保存与实际分辨率匹配的 `camera_matrix`、`distortion`。
3. 在 **车顶标记高度的水平平面** 布置至少六个已测地图 XY 的控制点，记录原始图像像素坐标。不要直接用地面四角拟合后套到车顶，倾斜相机会产生视差。
4. 建立测量 JSON，包含 `camera_matrix`、`distortion`、`image_size`、`pixels`（N×2）和 `map_xy`（N×2）。运行：

```bash
python scripts/calibrate_overhead.py measurements.json --output configs/local.overhead.json
```

5. 在输出配置中填写真实 `tag_id`、`yaw_offset_rad`、`tag_to_base_xy_m` 和 `base_z_m`。标记印刷顶边指向定义为前向，`yaw_offset_rad` 是它到车辆前向的修正。`tag_to_base_xy_m` 是从标记中心到车辆参考点的向量，用车辆坐标表达。保留测量依据。
6. 单独启动车载视频适配器，然后运行定位：

```bash
python adapters/apriltag.py --source 1 --calibration configs/local.overhead.json
```

默认面积门限只是初始设置。未检测到唯一目标 ID 时立即发布丢失状态。相机断流则由服务超时标过期。当前检测质量仅包括 ID 唯一性和面积门限，没有完整的重投影置信度评估；必须通过独立点和动态测试验收。

`calibrated=false` 的示例配置不能直接启动。拟合残差只是控制点内误差，不是实际定位精度；在未参与拟合的车位、不同方向和道路边缘做独立核验，记录最大误差与 P95。若场地不平、标记明显倾斜或相机移动，平面假设失效，需要重新标定或升级到完整 3D 位姿估计。

参考：[OpenCV 标记检测文档](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)。
