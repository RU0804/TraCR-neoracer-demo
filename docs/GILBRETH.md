# Gilbreth 资源约束

遵守用户 2026-10-20 的 GPU 指令：

1. 提交前检查 `slist` 的组内额度、运行和排队。优先 `sukkusur / a100-40gb / normal` 的单张 A100-40GB。
2. A100 额度占用或已承诺给排队工作时选择 A30。当前无购买额度，使用 `a30 / standby`；将来额度变化应重新核实。
3. 完整 demo、图形仿真禁止 A10。用户仅允许预计 30 秒以内的极小任务使用 A10，本仓库提交脚本从不选 A10。
4. Unity、视频编码和浏览器渲染等实质工作放入 Slurm，不在登录节点持续运行。

```bash
bash scripts/submit_validation.sh --dry-run
bash scripts/submit_validation.sh --test-only
# 为浏览器检查配置 Python/Playwright 路径后：
bash scripts/submit_validation.sh
```

默认 `TRACR_BROWSER_PYTHON=.venv/bin/python`；运行浏览器检查需提前安装 Playwright/Chromium。可复用环境变量 `TRACR_BROWSER_PYTHON`、`PLAYWRIGHT_BROWSERS_PATH` 指向已有安装。

当前脚本请求 2 CPU、6 GB、1 GPU、8 分钟上限，正常验证用几十秒。作业结束后停止服务，不留常驻进程。完整 Python 服务也会拒绝 A10 分区运行。

本仓库浏览器测试成功 **不代表 Unity 的 NVIDIA Vulkan 图形链路成功**。A100/A30 的 Unity 图形兼容性仍待验证；不能因此切换到 A10。现场演示优先笔记本本地渲染。
