# Use Your VPN around the clock 全天候使用你的VPN

> 一个规则源，多种客户端：🇨🇳 中国大陆服务直连，🌍 国际服务使用自己的代理节点。

**v0.4.0-beta.1

目标是保持 VPN 连接，在微信、QQ、哔哩哔哩、淘宝、支付宝与 ChatGPT、YouTube、Google、GitHub 之间连续切换。规则自动决定国内直连或国际代理，无需为每个 App 反复关闭 VPN。

> [!IMPORTANT]
> 项目旨在全天不切换卡关也能正常访问国内外软件

**iOS 用户：先看 [Shadowrocket 教程](docs/IOS.md)。**

**Android 用户：推荐先看 [Android FlClash 图文步骤与排错](docs/ANDROID.md)，使用 [`dist/flclash-override.js`](dist/flclash-override.js) 给自己的订阅添加分流。**

**Windows / macOS：使用 [Clash Verge Rev 桌面教程](docs/DESKTOP.md) 和 [订阅扩展脚本](dist/clash-verge-rev-override.js)。桌面适配为预览版，尚待真机验证。**

## 下载安装

| 客户端 | 文件 | 状态 | 你还需要做什么 |
| --- | --- | --- | --- |
| iPhone / iPad：Shadowrocket | [`dist/shadowrocket.conf`](dist/shadowrocket.conf) | 初版，可导入 | 保留自己的节点/订阅；首页选择节点；路由选择「配置」 |
| Android：FlClash 覆写脚本（推荐） | [`dist/flclash-override.js`](dist/flclash-override.js) | 预览版（保留原订阅节点） | 导入原订阅，粘贴脚本，配置 → 更多 → 覆写 → 脚本，具体参见 [教程](docs/ANDROID.md) |
| Android：FlClash 完整模板（高级） | [`dist/android-flclash-template.yaml`](dist/android-flclash-template.yaml) | 模板（需私密订阅 URL） | 下载后仅在个人设备填写订阅地址，勿公开上传 |
| Windows / macOS：Clash Verge Rev 最新稳定版 | [`dist/clash-verge-rev-override.js`](dist/clash-verge-rev-override.js) | 预览版 | 保留原订阅；编辑订阅扩展脚本；应用中选择规则模式，参见 [桌面教程](docs/DESKTOP.md) |
| Android：Mihomo 内核客户端 | [`dist/mihomo.yaml`](dist/mihomo.yaml) | 模板 | **先用自己的 Mihomo 兼容订阅地址替换示例地址**；再导入 |
| Linux / 其他 Mihomo 客户端（高级模板） | [`dist/mihomo.yaml`](dist/mihomo.yaml) | 模板 | 同上；按客户端提示开启系统代理或 TUN |
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

### Windows / macOS：Clash Verge Rev

1. 从 [官方最新稳定版](https://github.com/clash-verge-rev/clash-verge-rev/releases/latest) 安装适合设备架构的客户端，先导入并验证自己的订阅。
2. 将 [`dist/clash-verge-rev-override.js`](dist/clash-verge-rev-override.js) 全文粘贴到当前订阅的扩展脚本中；保存并应用。
3. 在客户端选择「规则」模式和可用代理节点，按需开启系统代理或 TUN。
4. 查看最终规则和连接记录：国内 DIRECT，指定国际服务及未匹配流量指向所选代理组。

脚本会替换原订阅的路由规则（含广告过滤等），保留节点、已有代理组和 DNS / TUN 字段。客户端自身设置优先级及后续扩展仍可能影响最终配置。详细导入、更新、恢复方法见 [桌面教程](docs/DESKTOP.md)。此适配针对 Clash Verge Rev，不承诺原版 Clash、Clash for Windows 或 ClashX 兼容。

### 其他 Mihomo 客户端：高级模板

1. 下载 [`dist/mihomo.yaml`](dist/mihomo.yaml)，**先在本地编辑**：将 `https://example.invalid/YOUR_PRIVATE_SUBSCRIPTION_URL` 换成自己真实的、**兼容 Mihomo proxy-provider 格式**的订阅链接。
2. 不要将编辑后的文件（含个人订阅 token）上传至公开 GitHub 仓库，也不要在公开 Issue 里粘贴它。
3. 导入支持 Mihomo 内核的客户端并启用配置，等待订阅和远程规则下载。
4. 在 `PROXY` 策略组中选择一个可用节点；依客户端设置启用系统代理或 TUN 接管应用流量。
5. 如已有正在使用的 Mihomo 配置，推荐把 [`dist/mihomo-rules.fragment.yaml`](dist/mihomo-rules.fragment.yaml) **合并**进自己的配置，而非覆盖原配置；你的代理策略组名称应为 `PROXY`，或对应地改写片段中的策略组名称。

**注意：** 机场提供的通用订阅链接未必是 Mihomo 兼容格式；如仅提供专有格式，需要先从服务商取得适合 Mihomo 的订阅。示例 URL 的 `.invalid` 域名故意无法连接，防止误用。

## 正确选择代理组

Android 与桌面脚本都提供 `const USR_PROXY_GROUP = "";`。留空时仅在有一个合格候选组时自动选择；广告/拒绝/仅直连组、静态空组和没有代理出口的组会排除。出现多个候选时，按错误提示在本地脚本中填写准确组名，例如 `const USR_PROXY_GROUP = "🌐 Global";`，保存并重新应用。

候选判断依据节点/提供者引用，不依据“PROXY”名称猜测优先级。动态提供者和过滤器的最终结果仍需在客户端核对；代理组包含 DIRECT 时，请确认当前选中真实节点。原订阅节点、代理提供者和已有代理组保留，但原 `rules`（含广告过滤等）会被替换。恢复步骤见各平台教程。

## DNS 与连接验证

默认保留原订阅 DNS/TUN；Shadowrocket 仍使用 system。需要排查 DNS 时先看 [DNS 指南](docs/DNS.md)，可选 [Mihomo DNS 示例](dist/mihomo-dns.optional.yaml) 不会自动应用，不能独立导入。

在连接页核对：国内域名/IP 应命中 DIRECT，指定国际域名和未知流量应指向代理组且最终使用代理节点。国际域名规则优先于 China 规则集和 CN GeoIP，但私有地址规则仍排在最前。只看到网页能打开，无法证明分流正确；完整场景见 [测试清单](docs/TESTING.md)。

规则覆盖与边界见 [分流审查记录](docs/ROUTING.md)。

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
scripts/check_mihomo.py            # 可选内核解析检查（合成节点）
dist/mihomo-dns.optional.yaml      # 可选 DNS 片段，先看 docs/DNS.md
dist/shadowrocket.conf             # Shadowrocket 配置
dist/mihomo.yaml                  # Mihomo 完整模板（需填自己的订阅）
dist/mihomo-rules.fragment.yaml    # Mihomo 规则片段（需合并）
dist/flclash-override.js          # 推荐 Android：覆写自己的订阅
dist/android-flclash-template.yaml # Android 完整 YAML 模板
dist/clash-verge-rev-override.js   # Windows / macOS：Clash Verge Rev 扩展脚本
docs/DESKTOP.md                   # Windows / macOS 中文教程
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

生成器只依赖 Python 3.10+ 标准库。完整测试需 Node.js 与 PyYAML（CI 已安装）；缺少依赖时相关检查会跳过，不能据此认定全部检查通过。内核检查方式见 [TESTING.md](docs/TESTING.md)。

**上游规则会自行更新：** Mihomo 的 `rule-providers` 每 86400 秒尝试更新一次；Shadowrocket 的下载/刷新由应用自己的规则集管理机制决定。修改自定义规则源则需要重新执行生成器、提交新文件。


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
