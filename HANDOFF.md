# TraCR NeoRacer 接续说明

本仓库从 `/scratch/gilbreth/zjcai/autodrive-demo/HANDOFF.md` 接续。新目标：师兄笔记本现场展示，左侧车载视频，右侧 AutoDRIVE NeoRacer，泡沫板道路约 5 m × 5 m。原来的 Nigel 离线成果保持不变。

## 当前交付

- Python 服务、浏览器双画面、有界时间匹配、断流提示、自检模式。
- 视频、只读 ROS 2、可选俯视 AprilTag 适配器。
- Unity CoSim 跟随/渲染回执 C# 源码和道路 JSON 导入器。
- 标定工具、固定上游版本、安装与现场手册、自动测试、GitHub CI 配置。

软件验证见 `docs/VALIDATION.md`。**未验证真实车、Unity C# 编译/构建、NeoRacer 渲染或真实时空同步。** 自检两幅图都是程序生成；其精度和延迟不能当实测指标。

## 下一步依赖

1. 师兄笔记本系统和 GPU；在该机安装相应 Unity 版本并编译本仓库组件。
2. 当前实车视频接口/ROS 2 话题列表，定位来源和质量状态。
3. 场地测量图与坐标/车体点定义；没有地图定位时确认是否可安装俯视相机。
4. 接车、标定、完成 `docs/RUNBOOK.md` 中连续运行及故障恢复检查。
5. 用户已创建 RU0804/TraCR-neoracer-demo 并明确选择 Public。连接已确认可写，通过 GitHub API 发布；后续无需再询问账号或可见性。地图制作说明见 docs/MAP_WORKFLOW.md。

不要把这些未知项写成默认实车配置，也不要将源码就绪说成已经现场跑通。不要重跑 Nigel 来冒充 NeoRacer 实现。

## 资源规则

遵守用户 A100-40GB 优先、占用/排队才 A30 standby、完整 demo 禁止 A10 的规则，所有实质计算走 Slurm；具体见 `docs/GILBRETH.md`。调度和浏览器测试成功不等于 Unity 图形链路成功。

现场方案为本地服务，不依赖 Gilbreth 常驻进程。原始项目与 `/home/zjcai/d2s-diffusion` 没有被修改。上游环境/大文件保留在原项目，当前仓库不打包它们。
