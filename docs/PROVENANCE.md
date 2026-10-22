# 成果来源和边界

## 此前已有结果

原项目位于 Gilbreth 的 `/scratch/gilbreth/zjcai/autodrive-demo`，交接文档为 `HANDOFF.md`。本仓库是独立的继续开发成果，未修改 `/home/zjcai/d2s-diffusion`、原始输出或历史日志。

已成功运行的是 **AutoDRIVE Simulator 0.2.0 / Nigel / Tiny Town**，包括红灯停车、左转路线跟踪和目标点停车。约 46 秒的离线展示保留在原项目 `outputs/final_demo_presentation/` 和 `outputs/autodrive_demo_delivery.zip`。

原实验 136 条遥测、46.391 秒，路径 RMSE 约 2.82 cm，终点误差约 3.30 cm。这些数字仅适用于当时 Nigel 仿真路线，不能标到 NeoRacer、当前网页、真实车辆或实际泡沫板地图上。其视频输出 10 fps 也不是实时采样率。历史作业使用 A10，发生在新资源约束生效之前；不改写为 A100 成果。

## 本仓库新增

Python 本地显示服务、只读输入适配器、位姿/视频配对协议、合成自检、Unity 跟随与渲染回执源码、道路 JSON 导入器、标定工具、软件测试及部署文档。所有 synthetic 图像由程序生成并标记。没有 NeoRacer 的实车录像或已运行 Unity 镜头。

上游固定版本记录于 `upstream.lock.json`。AutoDRIVE 资产和二进制未复制进仓库。CoSim 字段与坐标约定参考固定版本的官方源码：[Socket.cs](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/Socket.cs)、[CoSimManager.cs](https://github.com/Tinker-Twins/AutoDRIVE/blob/75b7df5216524a3c6b3150d698139190c6c44f8f/Assets/Scripts/CoSimManager.cs)。

NeoRacer 实车接口候选参考 [Neobotics 驱动](https://github.com/Neobotics-Foundation-Inc/neoracer_ros2_driver) 以及交接中的源码核查，未把上游车辆配置当成用户实车的事实。

## 许可证与再分发

本仓库当前未指定开源许可证，应由项目负责人决定后添加 LICENSE。不要假设“上传 GitHub”等同于已选择开源授权。使用/下载 AutoDRIVE、NeoRacer 模型及其他第三方资产时保留其版权说明并按各自许可证执行；本仓库未重新授权第三方内容。
