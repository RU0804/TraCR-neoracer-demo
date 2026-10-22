# 验证记录

2026-10-22。当前结论：**服务与协议的软件原型通过检查；NeoRacer 实车、Unity 构建与现场时间/空间对齐未验证。**

## 已执行

- Slurm 作业 `12006837`：`sukkusur / a100-40gb / normal`，2 CPU、6 GB、1 GPU，36 秒，COMPLETED。
- 首轮 26 项 Python 测试全部通过；覆盖时间戳和数值校验、最近时间匹配、有限缓冲、坐标轴、定位丢失、错误/重复/迟到回执、无定位不生成仿真图、HTTP/WS token、JPEG 解码与标记几何。
- Chromium：双图可解码、合成来源标注、桌面 1440×1080 与手机 390×844 无横向溢出、持续连接超过 16 秒、断流后冻结图片标过期、真实输入模式不会生成假图、无 JavaScript 错误。
- 调度器模拟检查：空闲 A100 选择、占用转 A30、排队转 A30、A30 配额变化拒绝猜测、异常额度输出拒绝、A10 运行时拒绝，全部通过。
- Python 语法编译与 shell 语法检查通过。实际 GitHub Actions 尚未执行；Windows/macOS 未测试。

修正采样时间新鲜度和 loopback Host 检查后，复验作业 **12006850** 使用同样 A100-40GB 配置，33 秒，COMPLETED：**28 项 Python 测试全部通过，浏览器检查全部通过**。最终归档对应此版本。

依赖版本记录在 `requirements-tested-linux-py39.txt`。当前有 aiohttp 建议改用 AppKey 的非失败警告；不影响上述检查结果。

## 证据

`docs/evidence/` 保存自检界面、无硬件等待界面以及机器可读验证摘要。截图均来自合成测试，不能作为实车或 AutoDRIVE 演示图使用。HTTP 测试中的 Unity 客户端是协议替身，不会启动 Unity。

复现浏览器检查：安装 `playwright` 并下载 Chromium；在两个终端分别运行 `tracr-demo --self-test` 和 `tracr-demo --port 8081`，第三个终端运行 `python scripts/check_browser.py`。Gilbreth 使用 `scripts/submit_validation.sh`，不可在登录节点长期运行渲染。

## 未执行，不能据此宣称通过

- AutoDRIVE NeoRacer 场景导入、C# 编译、相机渲染与独立程序构建。
- 笔记本 GPU 和允许的 Gilbreth GPU 上 Unity 图形 API 兼容性。
- 实车相机、真实 ROS 2 话题、标记检测速度和遮挡恢复。
- 真实道路重建、场地/车体参考点标定及空间误差。
- 设备时钟校准、曝光到屏幕的端到端延迟、实际帧率和丢帧率。

自检的帧率、P95 和零时间差来自同进程生成数据，只能用于软件烟雾测试，不能报告为硬件性能。
