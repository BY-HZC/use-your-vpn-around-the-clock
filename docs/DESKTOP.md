# Windows / macOS 使用教程｜Clash Verge Rev

本项目桌面端适配 **Clash Verge Rev 最新稳定版**的订阅扩展脚本接口。2026-10-17 核对官方 `releases/latest` 指向 v2.5.8；后续请以官方发布页为准。适配依据为官方文档，尚未完成 Windows / macOS 真机测试，不保证后续版本接口不变。

## 1. 安装并准备自己的订阅

- 从 [官方最新稳定版](https://github.com/clash-verge-rev/clash-verge-rev/releases/latest) 下载。不要选择 AutoBuild 作为日常适配基准。
- Windows：按设备架构与发布说明选择安装包，完成安装。
- macOS：Apple Silicon 选择对应 ARM 安装包，Intel 选择对应 x64 安装包；按官方安装说明安装，安全提示请按系统和官方流程处理。
- 在「订阅」页导入自己的 Clash / Mihomo 兼容订阅，选中该订阅，在代理组中选择可用节点。先确认原订阅能正常联网。
- USR 不提供节点，不需要你将订阅链接或访问令牌交给维护者。此教程不承诺 Clash for Windows、ClashX 或原版 Clash 兼容。

## 2. 给当前订阅添加分流

1. 先备份已有扩展脚本。打开 [clash-verge-rev-override.js](../dist/clash-verge-rev-override.js)，复制全文。
2. 在 Clash Verge Rev「订阅」页右键当前订阅卡片（Mac 也可使用 Control 点击），找到编辑扩展脚本的入口。菜单名称随版本变化，以 [官方扩展文档](https://www.clashverge.dev/guide/extend.html) 为准。
3. 将代码粘贴到**当前订阅的扩展脚本**中，保存并应用/重新激活配置。不要把 JS 当作订阅 YAML 导入，也不要同时粘贴到全局与订阅脚本。
4. 若已有其他自定义脚本，覆盖前先备份；多个脚本或规则编辑器可能改变执行结果。USR 会替换原订阅的整个 `rules` 列表，包括原有广告过滤、游戏和其他特殊分流。
5. 在客户端界面将模式设为「规则 / Rule」。脚本不设置 `mode`，因为该字段由 Clash Verge Rev 应用设置管理。
6. 查看最终运行配置/规则页，应有 `usr-china-classical` 规则提供者、`GEOIP,CN,DIRECT`，最后一条是 `MATCH,你的代理组`。不能仅凭脚本保存成功判断生效。

脚本保留原有节点、代理提供者、代理组及 DNS / TUN 字段；新增 USR 规则提供者并替换路由。客户端设置和其他扩展仍可能改写最终配置。首次使用检查上游规则是否下载成功。

### 选择代理组

两端统一使用 `const USR_PROXY_GROUP = "";`。有且仅有一个合格候选时自动选中；广告、拒绝、直连组、静态空组和无代理出口的组被排除。多个候选会报错，此时将空字符串改为准确组名，例如：

```javascript
const USR_PROXY_GROUP = "🌐 Global";
```

保存并重新应用，核对最后一条 `MATCH`。组名不存在或被判定无代理出口时会报错，不会静默改选第一个组。无策略组但有节点/提供者时才新建 `USR-PROXY`（若与节点重名则附加编号）。带过滤器的候选不会自动选中，须核对过滤结果后手动指定。动态提供者尚未加载、过滤器排空、未知组类型可能需要人工检查；脚本不能证明节点在线。包含 DIRECT 的组仍须在客户端选中真实代理节点，切换订阅后也要检查组名。

## 3. 系统代理和 TUN

- **系统代理**：先开启此模式验证浏览器。只有遵循系统代理设置的应用会被接管，不能据此推断所有应用都生效。
- **TUN**：需要接管更多应用时，在客户端设置中按官方说明安装/启用服务并授予所需权限，再开启 TUN。Windows / macOS 的权限提示不同，按本机客户端提示操作；USR 不会自动安装服务或开启 TUN。
- DNS、IPv6 和路由由客户端与原订阅共同决定。保持默认配置先测试，出现问题后依据日志逐项排查。不要直接关闭系统安全功能来解决联网问题。
- 若已有其他 VPN，先排查接管冲突；首次使用时同时检查打印机、NAS 等局域网设备是否可访问。

## 4. 验证连接记录

在规则模式下访问以下目标，然后进入客户端「连接 / Connections」页查看实际匹配规则与最终节点。必要时重新发起连接，旧连接不代表更新后的规则。

| 目标 | 期望 |
| --- | --- |
| `data.bilibili.com` / `qq.com` | DIRECT |
| 只被上游 China 规则覆盖的国内域名 | 命中 `usr-china-classical`，DIRECT |
| 国内 IP | GeoIP 数据可用时命中 `GEOIP,CN,DIRECT` |
| `chatgpt.com` / `youtube.com` | 指向所选代理组，最终选择可用代理节点 |
| 无其他规则命中的目的地 | `MATCH` 指向所选代理组 |
| 局域网 IPv4 / IPv6 | DIRECT |

分流按域名和 IP，而非应用名。能打开网页不能单独证明分流成功。DIRECT 使用当前网络出口，不会赋予中国大陆公网 IP。代理故障时国际服务及未匹配请求可能失败。

## 5. 更新和恢复

- 上游 China 规则配置为每 86400 秒尝试更新，具体下载结果在客户端中查看。
- 本地粘贴的 JS **不会自动随 GitHub 更新**。从项目下载新版全文，重新粘贴、恢复个人代理组设置、保存应用并再次检查连接。
- 订阅更新后检查扩展是否仍生效、代理组是否改名。
- 恢复：把当前订阅扩展脚本恢复为此前备份；若此前无脚本，恢复 `function main(config) { return config; }`，保存并重新激活订阅，确认原始路由恢复。不要删除自己的订阅。
- 退出客户端后检查系统代理是否恢复；休眠唤醒及 Wi-Fi 切换后再次确认连接。

## 6. 问题排查与测试状态

脚本报代理组不存在：核对本地 `USR_PROXY_GROUP` 和订阅组名。完全无节点：先导入有效订阅。国内流量仍代理：检查规则模式、当前订阅、最终运行规则、远程规则下载，以及是否被其他扩展改写。

自动化仅覆盖生成一致性、JavaScript 语法及 Node.js 模拟，**不等同于 Clash Verge Rev 的 Boa 执行器或实际系统网络测试**。Windows / macOS 导入、服务权限、TUN、DNS / IPv6、网络切换和退出恢复均待真机验证，见 [测试清单](TESTING.md)。反馈时提供版本与脱敏截图，不要上传订阅、节点地址、完整日志或账号信息。

## 官方参考

- [Clash Verge Rev 仓库](https://github.com/clash-verge-rev/clash-verge-rev)
- [官方安装说明](https://www.clashverge.dev/install.html)
- [扩展配置与脚本、执行顺序及设置优先级](https://www.clashverge.dev/guide/extend.html)
- [JavaScript main(config) 脚本接口](https://www.clashverge.dev/guide/script.html)

## v0.4.0 Beta · Seamless Routing

规则模式下，国内与国际连接由规则分别选择出口，目标是在 App 间切换时保持 VPN 连接。桌面脚本继续保留 DNS/TUN，Clash Verge Rev 的界面仍需选择规则模式。若国内或国际应用连续切换后异常，先看连接命中和最终节点，再按 [DNS 排查](DNS.md) 检查解析、IPv6 与缓存。

可选 DNS 片段不自动合并，不要覆盖已有可用设置。按第 5 节可恢复原订阅脚本；若手动试用了 DNS 片段，同时恢复 DNS 备份。Windows / macOS 的真实 DNS、UDP/QUIC、休眠唤醒与网络切换仍按 [测试清单](TESTING.md) 验证。
