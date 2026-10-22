# GitHub 发布与更新

用户已创建公开仓库：[RU0804/TraCR-neoracer-demo](https://github.com/RU0804/TraCR-neoracer-demo)。Public 是用户明确选择，保留该设置。此工作区的 origin 已配置为 `https://github.com/RU0804/TraCR-neoracer-demo.git`。源码、测试记录、界面截图和地图制作说明已上传；首次完整发布核对了本地与远端 Git 文件树一致性。

源码、小型验证截图和文档进入 Git；Python 环境、Unity 工程下载、二进制、录像和本地标定不进入版本库。提交前检查 `git status --short` 和 `git diff --cached --stat`。本地配置使用 `configs/local*.json`，token 只放环境变量。

在配置了 GitHub 登录的开发电脑上，首次获取：

```bash
git clone https://github.com/RU0804/TraCR-neoracer-demo.git
cd TraCR-neoracer-demo
```

后续更新：

```bash
git pull --ff-only
# 修改和验证后提交
git push origin main
```

不要将现有非空远端强推覆盖。此环境通过已连接 GitHub 的文件/Git 数据接口发布，不依赖本机 gh 登录。公开仓库可直接通过 HTTPS 获取。

如果从源码 ZIP 解压得到目录，目录不含 .git；优先直接 git clone，或使用提供的 Git bundle 保留本地历史。录制数据保存在被忽略的 `recordings/`，需要公开时单独确认数据来源与授权。

本仓库目前没有开源 LICENSE；发布为 public 不代表已替项目负责人选择开源许可证。AutoDRIVE 模型和其他第三方资产也未重新授权或打包。
