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
