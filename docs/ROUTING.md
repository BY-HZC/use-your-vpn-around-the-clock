# v0.4.0 分流审查记录

唯一域名规则源是 `config/routing.json`；所有客户端沿用“私有地址 → 指定国际服务 → 指定国内服务 → China 规则集 → .cn / CN IP → 代理兜底”的顺序。

## 本次调整

移除 `weixin.qq.com`，因为 `DOMAIN-SUFFIX,qq.com` 已覆盖它及其子域名，实际分流意图不变。生成器现在拒绝精确重复以及同策略或不同策略的父子域名重叠，避免未来新增条目时出现隐蔽覆盖。需要例外策略时应先设计明确的优先级与测试，不能绕过校验。

没有推测或新增 App 的内部域名。现有覆盖可按以下族检查；这是静态规则覆盖，不是全量 App 流量或真机联网证明。

| 服务 | 现有域名族（含子域名） | 期望 |
| --- | --- | --- |
| 微信 / QQ | qq.com、weixin.com、wechat.com、tenpay.com | DIRECT |
| 哔哩哔哩 | bilibili.com、bilivideo.com、biliapi.com、hdslb.com | DIRECT |
| 淘宝 | taobao.com、tmall.com、alicdn.com | DIRECT |
| 支付宝 | alipay.com、alipayobjects.com | DIRECT |
| ChatGPT | openai.com、chatgpt.com、oaistatic.com、oaiusercontent.com | PROXY |
| YouTube / Google | youtube.com、googlevideo.com、ytimg.com、google.com、googleapis.com、gstatic.com | PROXY |
| GitHub | github.com、githubusercontent.com、githubassets.com | PROXY |

其余大陆域名由既有 [blackmatrix7 China 规则集](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Clash/China)、`.cn` 和 GeoIP 共同补充。第三方登录、CDN、广告或新域名可能走其他规则；后续只有收集脱敏的实际命中证据并核实域名归属后才增加规则。

## 顺序和协议边界

- 指定国际域名早于 China 集合与 `GEOIP,CN`，因此连接仍带有可匹配域名时，不会仅因解析到国内公网 IP 而被这两项改成 DIRECT。
- 私有地址优先级最高；如果目的地址是私有地址，仍按用户要求 DIRECT。只看到 IP、嗅探未取得域名或客户端未接管时，无法保证按国际服务域名识别。
- IPv4/IPv6 私有网段分别保留，公网 CN GeoIP 命中依赖数据库与客户端；不强制打开或关闭 IPv6。
- 规则没有按 TCP/UDP 区分，不阻断 UDP/QUIC，也不改变节点的 UDP 开关。是否可用取决于节点能力、VPN/TUN 接管、DNS 和网络环境，不通过增加端口规则来假装解决问题。

依据：[Mihomo 路由规则](https://wiki.metacubex.one/config/rules/) 与 [DNS 解析流程](https://wiki.metacubex.one/config/dns/diagram/)。模拟测试把 GeoIP/上游命中作为输入，仅验证规则先后逻辑；真实行为见 [测试清单](TESTING.md)。
