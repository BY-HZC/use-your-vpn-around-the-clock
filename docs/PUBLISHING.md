# 维护者发布指南（GitHub）

此仓库已经整理好 iOS + Android 公开发布文件。发布前请先在本地审查。

## 文件分类

| 类别 | 文件 | 是否发布 |
| --- | --- | --- |
| 统一规则源 | `config/routing.json` | 是 |
| iOS 配置 | `dist/shadowrocket.conf` | 是 |
| Android FlClash 覆写 | `dist/flclash-override.js` | 是 |
| Android Mihomo 模板 | `dist/android-flclash-template.yaml` | 是，**仅示例 URL** |
| 通用 Mihomo 模板 | `dist/mihomo.yaml` | 是，**仅示例 URL** |
| Mihomo 规则片段 | `dist/mihomo-rules.fragment.yaml` | 是，不能单独导入 |
| 使用教程 | `docs/IOS.md`, `docs/ANDROID.md`, `docs/TESTING.md` | 是 |
| 生成器与测试 | `scripts/`, `tests/`, `.github/workflows/check.yml` | 是 |
| 私有订阅/节点 | 任何含 token、密码、服务器的个人配置 | **绝对不要发布** |

## 本地检查

在项目根目录运行：

```bash
python3 scripts/generate.py --check
python3 -m unittest discover -s tests -v
```

CI 在 GitHub Actions 上执行同样的检查，另外安装 PyYAML 校验 YAML 结构。

如有意修改 `config/routing.json`，先运行 `python3 scripts/generate.py` 重新生成 `dist/` 文件，再运行测试。

## 发布到 GitHub

1. 确认已用自己的 GitHub 账号登录；推荐 GitHub CLI `gh auth status`。
2. 检查 `git status`、`git remote -v`、将要提交的文件清单及任何潜在凭据。
3. 如尚无仓库，可在项目目录执行：

```bash
git init -b main
git add .
git commit -m "Initial public beta: iOS and Android routing"
gh repo create use-your-vpn-around-the-clock --public --source=. --remote=origin --push
```

4. 如果仓库已存在，先检查远端和分支；**不要覆盖其他仓库、不要 force push**。
5. 发布后打开仓库 README，检查 `dist/`、`docs/`、`.github/workflows/check.yml` 是否存在，并检查 Actions 状态。
6. 如需要 GitHub Release，可在核实提交和版本号后创建预发布（pre-release），例如 `v0.3.0-beta.1`；不要将未测试的版本描述为稳定版。

> 如果 GitHub CLI 尚未登录，使用 `gh auth login` 完成交互授权。遇到登录错误、rate limit、2FA 或验证码时停止自动发布，等待用户在官方页面完成；不要试图绕过验证。

## 更新规则

编辑 `config/routing.json` → `python3 scripts/generate.py` → 测试 → 提交 → 推送。iOS 远程规则集和 Mihomo 远程规则集按各自客户端机制更新，但仓库生成文件的更新需要提交新版本。
