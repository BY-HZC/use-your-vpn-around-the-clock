# DNS 审查与可选方案｜v0.4.0 Beta

## 默认行为

| 输出 | 本版本默认行为 |
| --- | --- |
| Shadowrocket | 保持 `dns-server = system` |
| Mihomo / Android 完整模板 | 不新增 `dns` 块，由客户端及其设置决定实际解析行为 |
| FlClash / Clash Verge Rev 脚本 | 保留输入配置的 DNS、TUN、IPv6 和节点字段 |

先使用原来可以联网的订阅。本项目按域名/IP 分流，不能单凭规则文件控制所有应用的 DNS 请求。客户端 DNS 覆写、浏览器安全 DNS、系统加密 DNS、缓存和应用自带解析都可能影响结果。

## 可选 Mihomo 示例（默认不启用）

[`dist/mihomo-dns.optional.yaml`](../dist/mihomo-dns.optional.yaml) 是生成器维护的 **DNS 片段**，不能独立导入，也不由覆写脚本自动应用。适合了解 DNS 设置的用户在备份后测试；当前仅验证 Mihomo v1.19.32 的配置解析，其他内核版本和真实网络行为待验证。

- 例子面向中国大陆网络：已明确列出的国内域名和 `.cn` 使用 `223.5.5.5` 的 DoH，并显式指定 DIRECT。它是公共解析服务，不一定优于当前网络的解析器；境外、企业内网或特殊运营商网络请先选择适合自己的解析器。
- 指定国际域名和未被 DNS 策略覆盖的域名使用 `1.1.1.1` 的 DoH，经 `#PROXY` 出站。须已有名为 `PROXY` 的策略组；如果实际组名不同，替换片段内所有 `#PROXY`，并确认该组选择了真实代理节点。组名含 `#`、`&` 等 DNS 参数分隔符时，不要直接套用这个片段。
- 节点域名使用独立的 `proxy-server-nameserver`，通过 IP 地址形式的 DoH 直连，避免先建立代理才能解析代理节点的循环。`default-nameserver` 为引导解析器；不要改成依赖同一个代理才能访问的地址。
- `respect-rules` 让其他未显式指定出口的 DNS 连接遵循路由；此例对主要解析器使用 `#DIRECT` / `#PROXY` 明确出口，并关闭优先 HTTP/3。DoH 依然需要服务器可达和证书有效。
- `direct-nameserver` 在 DIRECT 出口重新解析，尽量获得适合直连的结果。未被显式国内 DNS 策略覆盖的域名，首次查询仍可能经过代理，随后才在直连出口重解析；不能宣称所有 DNS 查询和最终流量出口都完全相同。
- 国内/国际域名策略由 `config/routing.json` 生成。没有额外下载 GeoSite 依赖，也没有另造一份应用域名清单。

合并前逐项核对自己的 `dns` 设置，保留需要的内网域名、hosts、fake-IP 排除和运营商策略。示例使用 `redir-host`，不要直接覆盖正在工作的 fake-IP 配置；更改解析模式后需要客户端重新加载并处理旧 DNS 缓存。示例不设置 DNS 监听端口、TUN、DNS 劫持或 IPv6 开关，因此也不会自动接管系统/应用的所有查询。

Clash Verge Rev 的应用设置和扩展执行顺序会影响最终配置，尤其应检查「DNS 覆写」与最终运行配置；FlClash 同样需要核对实际启用的设置。若内核不支持相关字段、节点解析失败或内网失效，恢复备份 DNS 配置并重新应用。**加密 DNS、语法检查通过都不能证明零 DNS 泄漏。**

## Shadowrocket 的处理

从 [App Store 开发者入口](https://apps.apple.com/us/app/shadowrocket/id932747118) 核对到的 [开发者网站](https://shadowlaunch.com/) 未提供可据以确认当前 DNS 字段兼容性的详细公开配置规范。因此本版本保留现有 system 设置，不采用自称官方的第三方教程参数，也不直接套用 Mihomo 的 DNS 字段。

如需自定义 DNS，请按设备上 Shadowrocket 当前版本提供的设置和说明逐项测试；必须记录客户端版本、网络环境、解析结果与实际连接策略。本版本没有新增 Shadowrocket DNS 保证。

## 故障排查：先区分解析失败与节点失败

1. 在原订阅下确认节点可用，再应用 USR。若节点域名都无法解析，先恢复原 DNS，检查本地网络；不要通过频繁切换路由模式掩盖问题。
2. 查看连接记录和 DNS/错误日志：是解析超时、没有 A/AAAA 地址，还是已有地址但代理连接失败？只分享脱敏片段。
3. 国内访问异常：检查 DIRECT 命中、DNS 返回地址与 CDN；确认未被浏览器/系统安全 DNS或其他扩展改写。不要凭 IP 所在地直接新增宽泛域名规则。
4. 国际服务异常：确认代理组最终选中节点、远程规则加载、节点域名引导解析，以及代理侧能否访问所选 DNS。
5. Wi-Fi 切换到蜂窝或 IPv6 网络后，重建连接并比较缓存/新查询；检查 IPv4、IPv6 分别是否可用。UDP/QUIC 不通也可能来自节点或接管方式，而非 DNS。
6. 每次只修改一个设置；无改善就恢复备份，重新加载原订阅并核对最终配置。恢复方式见各平台教程。

## 依据与验证边界

以下为 2026-10-18 查阅的官方来源，具体字段随内核版本变化：

- [Mihomo DNS 字段及出口参数](https://wiki.metacubex.one/config/dns/)：策略解析、引导解析器、节点专用解析器。
- [Mihomo 解析流程](https://wiki.metacubex.one/config/dns/diagram/)：DIRECT 重解析及 UDP 行为有版本差异。
- [Clash Verge Rev 扩展优先级](https://www.clashverge.dev/guide/extend.html)：应用设置、订阅及扩展的实际生效顺序。
- [FlClash 官方项目](https://github.com/chen08209/FlClash)：基于 Mihomo，实际行为还取决于打包内核和客户端设置。

配置解析验证使用合成节点，不连接私人订阅；不检验解析器可达性、解析准确性、DoH 证书握手、应用解析接管或 DNS 泄漏。真机清单见 [TESTING.md](TESTING.md)。
