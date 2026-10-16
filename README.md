# Use Your VPN around the clock

> 原名 Universal Split Routing（USR），配置中的 USR 标识保留以兼容现有安装。
>
> 一个规则源，多种客户端：🇨🇳 中国大陆服务直连，🌍 国际服务使用自己的代理节点。

**状态：v0.3.0-beta.1 社区预览版。** 配置已通过自动化静态检查，但尚未在所有客户端和设备版本上进行真机测试。欢迎反馈兼容性问题。

> [!IMPORTANT]
> 这不是“一个 `.conf` 文件适配全平台”。不同客户端需要不同的输出文件，项目用 [`config/routing.json`](config/routing.json) **统一维护规则意图**，由脚本生成对应格式。

**iOS 新用户：先看 [Shadowrocket 教程](docs/IOS.md)。**

**Android 新用户：推荐先看 [Android FlClash 图文步骤与排错](docs/ANDROID.md)，使用 [`dist/flclash-override.js`](dist/flclash-override.js) 给自己的订阅添加分流。**

## 下载安装

| 客户端 | 文件 | 状态 | 你还需要做什么 |
| --- | --- | --- | --- |
| iPhone / iPad：Shadowrocket | [`dist/shadowrocket.conf`](dist/shadowrocket.conf) | 初版，可导入 | 保留自己的节点/订阅；首页选择节点；路由选择「配置」 |
| Android：FlClash 覆写脚本（推荐） | [`dist/flclash-override.js`](dist/flclash-override.js) | 预览版（保留原订阅节点） | 导入原订阅，粘贴脚本，配置 → 更多 → 覆写 → 脚本，具体参见 [教程](docs/ANDROID.md) |
| Android：FlClash 完整模板（高级） | [`dist/android-flclash-template.yaml`](dist/android-flclash-template.yaml) | 模板（需私密订阅 URL） | 下载后仅在个人设备填写订阅地址，勿公开上传 |
| Android：Mihomo 内核客户端 | [`dist/mihomo.yaml`](dist/mihomo.yaml) | 模板 | **先用自己的 Mihomo 兼容订阅地址替换示例地址**；再导入 |
| Windows / macOS / Linux：Mihomo 内核客户端 | [`dist/mihomo.yaml`](dist/mihomo.yaml) | 模板 | 同上；按客户端提示开启系统代理或 TUN |
| 已有 Mihomo 配置，希望只添加规则 | [`dist/mihomo-rules.fragment.yaml`](dist/mihomo-rules.fragment.yaml) | **规则片段，不能单独导入** | 手动合并 `rule-providers`、`rules`，确保存在 `PROXY` 组 |
| Stash / Surge / Loon / Quantumult X / v2rayNG / sing-box | — | 暂未适配 | 不要直接导入其他格式；欢迎提交适配 PR |

> ⚠️ **公开的配置文件不含任何节点、订阅密钥或账号**，也无法自动读取你的机场订阅。大家需要分别配置自己的代理节点。

### iOS：Shadowrocket

详细步骤见 [iOS 使用教程](docs/IOS.md)。

1. 在本项目 GitHub 仓库打开 [`dist/shadowrocket.conf`](dist/shadowrocket.conf)，点击 **Raw** 并复制 URL，或下载文件导入 Shadowrocket 的「配置」。
2. 在小火箭中将其设置为当前使用的配置；保留原来的机场订阅与节点。
3. 首页选择一个可用节点，**全局路由 = 配置**，打开连接。
4. 配置里的第三方 `China.list`、`China_Domain.list` 需要下载成功；可以在「配置 → 编辑配置 → 规则集 URL」查看。
5. 「数据 → 连接记录」中检查国内服务是否显示 `DIRECT`，国际服务是否显示 `PROXY`。

### Android / Windows / macOS / Linux：Mihomo

1. 下载 [`dist/mihomo.yaml`](dist/mihomo.yaml)，**先在本地编辑**：将 `https://example.invalid/YOUR_PRIVATE_SUBSCRIPTION_URL` 换成自己真实的、**兼容 Mihomo proxy-provider 格式**的订阅链接。
2. 不要将编辑后的文件（含个人订阅 token）上传至公开 GitHub 仓库，也不要在公开 Issue 里粘贴它。
3. 导入支持 Mihomo 内核的客户端并启用配置，等待订阅和远程规则下载。
4. 在 `PROXY` 策略组中选择一个可用节点；依客户端设置启用系统代理或 TUN 接管应用流量。
5. 如已有正在使用的 Mihomo 配置，推荐把 [`dist/mihomo-rules.fragment.yaml`](dist/mihomo-rules.fragment.yaml) **合并**进自己的配置，而非覆盖原配置；你的代理策略组名称应为 `PROXY`，或对应地改写片段中的策略组名称。

**注意：** 机场提供的通用订阅链接未必是 Mihomo 兼容格式；如仅提供专有格式，需要先从服务商取得适合 Mihomo 的订阅。示例 URL 的 `.invalid` 域名故意无法连接，防止误用。

## 分流优先级

1. 内网 IPv4 / IPv6 及本地地址 → `DIRECT`
2. 显式列出的国际域名 → `PROXY`
3. 显式列出的中国大陆软件域名 → `DIRECT`
4. [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 的中国大陆规则集 → `DIRECT`
5. `.cn` 域名 → `DIRECT`
6. 归属中国大陆 IP → `DIRECT`（可能触发 DNS 解析）
7. 其余流量 → `PROXY`

这些策略按每条连接的域名/IP 匹配，不是按应用进程名匹配。部分境外 CDN、DNS、IPv6、系统 VPN 检测与分流以外的网络策略可能导致例外。“直连”是从用户当前网络直接访问，并**不意味着获得中国大陆公网 IP**。

## 项目结构

```text
config/routing.json                 # 唯一的自定义规则源
scripts/generate.py                # Python 标准库生成器
dist/shadowrocket.conf             # Shadowrocket 配置
dist/mihomo.yaml                  # Mihomo 完整模板（需填自己的订阅）
dist/mihomo-rules.fragment.yaml    # Mihomo 规则片段（需合并）
dist/flclash-override.js          # 推荐 Android：覆写自己的订阅
dist/android-flclash-template.yaml # Android 完整 YAML 模板
docs/ANDROID.md                   # Android 中文使用教程
docs/IOS.md                       # iOS 中文使用教程
docs/PUBLISHING.md                # GitHub 维护者发布指南
AGENTS.md                         # Codex 等编码助手的仓库说明
CHANGELOG.md                      # 版本记录
scripts/generate_android.py       # Android 版生成器
tests/test_generated.py            # 回归测试
docs/TESTING.md                    # 真机测试方法
.github/workflows/check.yml        # GitHub Actions 一致性检查
```

## 修改或贡献规则

只编辑 [`config/routing.json`](config/routing.json) 中的 `proxy_domain_suffixes` 或 `direct_domain_suffixes`。注意同一域名不能同时加入两组，检查域名归属后再提交。

```bash
python3 scripts/generate.py
python3 scripts/generate.py --check
python3 -m unittest discover -s tests -v
```

生成器只依赖 Python 3.10+ 的标准库；自动化 CI 额外使用 PyYAML 检查生成文件能否被 YAML 解析。

**上游规则会自行更新：** Mihomo 的 `rule-providers` 每 86400 秒尝试更新一次；Shadowrocket 的下载/刷新由应用自己的规则集管理机制决定。修改自定义规则源则需要重新执行生成器、提交新文件。

## 想把这个仓库公开发布？

详见 [维护者发布指南](docs/PUBLISHING.md)。

1. 在 GitHub 创建公开仓库，建议仓库名 `use-your-vpn-around-the-clock`，初始化时**不要**勾选添加 README、`.gitignore` 或 license（本包已包含）。
2. 解压本 ZIP，把项目根目录的**所有文件及隐藏的 `.github` 目录**上传到新仓库。
3. 创建仓库后，在 `dist/shadowrocket.conf` 页面复制 GitHub 提供的 **Raw** URL 对外分享，不要自己手打可能错误的仓库地址。
4. 同时分享 `README.md`；Android / 桌面用户按说明编辑自己的 Mihomo 配置。
5. 保持 `.github/workflows/check.yml` 启用，检查提交后生成文件是否仍一致。

如果已经有 GitHub CLI，也可以在项目根目录运行：

```bash
git init
git add .
git commit -m "Initial release: cross-platform split routing"
gh repo create use-your-vpn-around-the-clock --public --source=. --remote=origin --push
```

GitHub CLI 命令需要用户自行登录授权；若同名仓库已存在，应先审查其内容和历史，避免覆盖无关项目。请先检查要公开的文件中没有个人订阅、私钥、令牌。

## 隐私与安全

- 不采集、回传、存储任何访问日志；此仓库仅发布静态配置与生成脚本。
- 不开启 HTTPS 中间人解密（MITM），不要求安装证书。
- 不包含任何真实代理节点或凭据；选择和信任节点由使用者负责。
- 配置引用第三方上游规则，使用方会向 GitHub Raw 请求规则文件；如服务不可访问，部分远程规则可能不可用。
- 默认未命中的流量使用 `PROXY`；使用前检查是否符合自己的隐私、法规与网络要求。
- 具体 DNS、流量接管及泄漏保护受到客户端、操作系统、订阅配置影响，本项目不承诺匿名性或零泄漏。

## 致谢和许可

本项目自写的生成脚本、配置模板和文档采用 [MIT License](LICENSE)。第三方中国大陆规则集直接通过 URL 引用，并未复制到本仓库，著作权与适用许可仍归 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 等各原作者；使用时请遵循相关项目授权。

客户端格式参考： [Shadowrocket 配置示例](https://github.com/reallinzc/Shadowrocket/blob/main/shadowrocket.conf) · [Mihomo 规则提供者文档](https://wiki.metacubex.one/en/config/rule-providers/) · [Mihomo 代理提供者文档](https://wiki.metacubex.one/en/config/proxy-providers/)

---

**English:** USR keeps one editable routing policy (`config/routing.json`) and generates Shadowrocket and Mihomo output files. Mainland-China domains and IPs use DIRECT; explicitly listed international domains and unmatched traffic use PROXY. Bring your **own** proxy subscription or nodes; never commit private subscription URLs to a public repo. This preview release needs device testing.
