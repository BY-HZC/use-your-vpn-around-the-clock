# 验证配置是否真的生效

## Shadowrocket（iOS）

1. 切到 `dist/shadowrocket.conf`，首页选择代理节点；「全局路由」设为「配置」。
2. 进入「配置 → 编辑配置 → 规则集 URL」，确认 `China.list` 和 `China_Domain.list` 显示成功。
3. 打开哔哩哔哩播放视频，再从小火箭「数据」中查看连接，过滤「直连」。
4. 查看 `data.bilibili.com` 等域名应显示 `DOMAIN-SUFFIX,bilibili.com,DIRECT`。注意视频 CDN 可能走其它域名，需逐条检查。
5. 打开 ChatGPT / YouTube，再过滤「代理」。`chatgpt.com`、`openai.com`、`youtube.com` 对应记录应显示 `PROXY`。
6. 检查部分仅通过远程规则命中的国内域名是否走 DIRECT，以验证规则集实际被使用，而不只是手动规则。

## Mihomo

1. 导入本地已替换私密订阅地址的 `dist/mihomo.yaml`；确保订阅提供者和 `china-classical` 规则集更新成功。
2. 在客户端的「连接/Connections」页面观察请求是否按预期命中 DIRECT 或 PROXY。
3. 在「代理/Proxies」里检查 `PROXY` 组已经选择可用代理节点；如果选到不可用节点，国外流量也会失败。
4. 需要全设备覆盖时确认客户端已开启适当的系统代理或 TUN；仅设置浏览器系统代理不一定覆盖所有 App。

## 预期结果与局限

| 示例域名 | 预期策略 | 判断依据 |
| --- | --- | --- |
| `data.bilibili.com` | DIRECT | 显式直连域名 |
| `qq.com` | DIRECT | 显式直连域名 |
| `ios.chat.openai.com` | PROXY | 显式国际域名 |
| `www.youtube.com` | PROXY | 显式国际域名 |
| 未被列出的中国大陆 IPv4 地址 | DIRECT | GEOIP,CN（取决于地理 IP 数据库） |
| 未匹配的其它域名 | PROXY | FINAL / MATCH |

网站能否打开**不能单独证明**走了哪条线路；以连接页面的命中规则及策略为准。

## Windows / macOS：Clash Verge Rev（待真机验证）

按 [桌面教程](DESKTOP.md) 验证并记录操作系统版本、架构、客户端及内核版本、日期和脱敏结果；不要将 Node 模拟通过填写为真机通过。

- [ ] Windows：订阅扩展脚本保存、加载及最终规则检查。
- [ ] macOS Intel / Apple Silicon：分别记录测试，未测试的架构保持待验证。
- [ ] 常见及特殊代理组名；手动指定组；订阅更新后组名变化。
- [ ] 系统代理下的浏览器连接规则和实际节点。
- [ ] TUN 服务安装/权限、其他应用接管、DNS 及 IPv6。
- [ ] 局域网设备、中国大陆域名及 IP、国际域名、最终 MATCH 兜底。
- [ ] 远程规则首次下载/更新失败、无可用节点时的行为。
- [ ] Wi-Fi 切换、休眠唤醒、退出客户端后代理恢复。
- [ ] 移除扩展后恢复原订阅路由。

## v0.4.0 Beta · Seamless Routing 验收

### 分清验证层级

| 层级 | 当前结果 | 能说明什么 |
| --- | --- | --- |
| 静态检查 | 生成一致性、YAML 结构、域名冲突及敏感字符串扫描通过 | 文件与规则源一致，结构符合检查条件 |
| Node.js 模拟 | 包括双端代理组识别、保留订阅字段、分流优先级，完整 unittest 共 38 项通过、0 跳过 | 合成输入下的脚本行为；GeoIP/上游命中在路由模拟中是人为设定 |
| Mihomo 内核解析 | 2026-10-18，macOS ARM64，Mihomo v1.19.32，10/10 通过 | 五种生成配置 × 默认/可选 DNS；替换为合成节点和本地测试规则提供者，保留生成的规则顺序 |
| 真机联网 | iOS 有限观察及维护者反馈；Android、Windows、macOS 待验证 | iOS 已观察部分域名/IP 的规则命中；完整持续联网、DNS、UDP 与配置版本验收未完成 |

发布提交会触发 [GitHub Actions](https://github.com/BY-HZC/use-your-vpn-around-the-clock/actions)，请以对应提交的运行结果为准。内核 `-t` 只解析配置，没有启动代理服务；可选 DNS 的 TLS 握手和解析结果没有由这项检查验证。

### 重现本地检查

使用 Python 3.10+、Node.js 与 PyYAML（建议与 CI 相同的 6.0.2）。生成器本身不依赖 PyYAML；完整测试缺少它会跳过部分检查。

```bash
python3 scripts/generate.py
python3 scripts/generate.py --check
python3 -m unittest discover -s tests -v
```

如已有从官方来源取得的 Mihomo 内核，可额外执行：

```bash
python3 scripts/check_mihomo.py --core /absolute/path/to/mihomo --data-dir /absolute/path/to/test-cache
```

此脚本使用 `192.0.2.1` 文档保留地址作为不可用的合成节点，不读取个人订阅。缺少公开 GeoIP 数据时，内核可能下载数据库到指定测试目录；不要把该缓存目录提交到仓库。内核验证需要 PyYAML 和 Node.js。真实订阅的 provider 下载与内容有效性仍须另测。

### 每个平台都执行的场景

保持规则模式和可用节点，不为每个应用关闭 VPN 或切换模式。每项记录通过/失败/未测试、具体版本、网络、域名或 IP、匹配规则及最终出口；截图和日志须脱敏。

| 场景 | 检查方式与期望 |
| --- | --- |
| 连续切换 | 微信 → ChatGPT → QQ → YouTube → 哔哩哔哩 → Google → 淘宝/支付宝 → GitHub，重复 3 轮；检查国内 DIRECT、国际代理，记录耗时和失败 |
| 国内应用 | 微信/QQ 发消息、B站播放、淘宝浏览、支付宝打开服务；不要用真实付款作为必要验收步骤 |
| 国内规则集 | 选一个仅命中上游 China 的域名，确认规则下载成功及实际 DIRECT |
| 国际域名优先级 | 查看国际域名命中显式规则；仅有 IP、丢失域名时不能保证仍按服务识别 |
| 未匹配流量 | 使用不命中其他规则的测试目的地，核对最终 MATCH/FINAL 使用代理 |
| 代理组误判 | 广告组 + Global；多候选报错；显式指定组；DIRECT-only、空组、提供者未加载或过滤为空时核对错误及恢复 |
| IPv6 | 分别验证局域网 IPv6、国内公网 IPv6、国际服务 AAAA；查看实际 IPv4/IPv6 连接，不能用 IPv4 成功替代 IPv6 验证 |
| UDP / QUIC | 在支持 UDP 的节点上验证语音或视频、HTTP/3；确认协议、命中与实际节点。TCP 成功不等于 UDP 成功，也不强制启用/禁用 QUIC |
| DNS 默认 | 记录默认 DNS 解析结果、节点域名解析、国内 CDN 和国际域名连接；区分超时、错误地址和连接失败 |
| DNS 可选 | 先备份；检查 PROXY 组名、节点引导 DNS、DoH 可达性、内网域名；失败可恢复。不要将“能联网”解释为零泄漏 |
| 网络切换 | iOS/Android Wi-Fi ↔ 蜂窝；Windows/macOS Wi-Fi ↔ 手机热点或有线，分别重建连接并观察 DNS 缓存、IPv6 及断线恢复 |
| 局域网/恢复 | NAS/打印机访问、休眠唤醒、退出后的系统代理、恢复原订阅脚本和 DNS |

### 平台记录（iOS 有限反馈，其余待测）

| 平台 | 客户端/内核版本 | 网络与架构 | 连续切换 | DNS/IPv6/UDP | 恢复 |
| --- | --- | --- | --- | --- | --- |
| iOS / iPadOS | Shadowrocket / 配置版本：待核对 | 提供的截图显示 Wi-Fi；其他待填 | 部分规则命中已观察，完整连续切换未记录 | 未测试 | 未测试 |
| Android | FlClash / Mihomo：待填 | 设备架构与网络：待填 | 未测试 | 未测试 | 未测试 |
| Windows | Clash Verge Rev / Mihomo：待填 | 系统/架构/接管方式：待填 | 未测试 | 未测试 | 未测试 |
| macOS | Clash Verge Rev / Mihomo：待填 | Intel/Apple Silicon 分别填 | 未测试 | 未测试 | 未测试 |

### iOS 有限实机反馈（2026-10-19 整理）

维护者提供的 2026-10-18 Shadowrocket 连接记录显示：

- 微信 `weixin.qq.com` 下的连接命中 `DOMAIN-SUFFIX,qq.com,DIRECT`。
- 一条 IP 连接命中 `GEOIP,CN,DIRECT`。
- ChatGPT/OpenAI、Google/gstatic 相关连接命中显式 PROXY 规则。
- 未列入显式域名规则的一条连接命中 `FINAL,PROXY`。

维护者随后反馈当前测试使用没有问题。以上仅记录可观察的规则命中与使用反馈，不包含原始截图、完整 URL、节点信息或个人日志。截图无法独立确认使用的是哪一个配置版本，iOS/Shadowrocket 版本也未提供，因此不将其写成 v0.4.0 完整真机验收通过；B站、淘宝/支付宝、网络切换、IPv6、UDP/QUIC、DNS 和其他平台仍按清单验证。
