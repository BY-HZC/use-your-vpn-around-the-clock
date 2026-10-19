# iOS 使用教程｜Shadowrocket

> Use Your VPN around the clock v0.4.0 Beta · Seamless Routing。规则经过静态检查，已有有限的 iOS 规则命中记录与使用正常反馈，完整真机验收仍待完成（见 [测试记录](TESTING.md)）；不同 iOS/Shadowrocket 版本仍可能存在差异。

## 1. 准备工作

- iPhone / iPad 安装 Shadowrocket，且已有自己可用的代理节点或机场订阅。
- 本项目**不提供代理服务器或订阅**，不要求你将个人订阅发给项目维护者。
- 配置文件：[`../dist/shadowrocket.conf`](../dist/shadowrocket.conf)。

## 2. 导入配置

1. 在 GitHub 仓库打开 `dist/shadowrocket.conf`，点击 **Raw**，复制 URL；也可以下载 `.conf` 文件。
2. 在 Shadowrocket 底部进入「配置」，添加远程配置 URL 或导入下载的本地文件（入口名称因版本而异）。
3. 选中刚导入的 USR 配置，确保它成为**当前使用的配置**。不要删除自己原有的机场订阅。
4. 回到首页，选择已有的可用节点，打开连接开关。
5. 将首页的「全局路由」设置为**配置（Config）**，而不是「代理（Proxy）」或「直连（Direct）」。

> 本文件仅定义路由规则；`PROXY` 指向 Shadowrocket 当前选择的代理节点。没有可用节点时，国外网站不会凭空连通。

## 3. 检查 blackmatrix7 远程规则

1. 进入「配置」并编辑当前 USR 配置。
2. 找到「规则集 URL」。
3. 检查 `China.list` 与 `China_Domain.list` 是否显示下载成功；必要时点击刷新。
4. 远程规则失败时，部分手动直连域名仍然可能工作，但国内规则覆盖范围会缩小。

远程规则来源：<https://github.com/blackmatrix7/ios_rule_script>。项目仅引用 URL，不复制上游规则内容。

## 4. 直观测试

1. 保持 Shadowrocket 连接、全局路由为「配置」。
2. 打开哔哩哔哩，播放一段视频，再到 Shadowrocket 的「数据 → 连接记录」（具体菜单依版本而异）。
3. 选择「直连」，搜索 `bilibili` 或 `bilivideo`；例如 `data.bilibili.com` 应显示 `DOMAIN-SUFFIX,bilibili.com,DIRECT`。
4. 打开 ChatGPT 或 YouTube，再到「代理」连接记录；`ios.chat.openai.com` / `youtube.com` 应显示 `PROXY` 和当前节点名称。
5. 如仅看到某个 App 可以联网，**还不能证明分流成功**；应查看具体域名/IP 的连接策略。

## 5. 常见问题

**B 站仍走代理？** 确认当前配置是 USR、全局路由为「配置」，然后查看该连接是否命中未覆盖的 CDN 域名。

**ChatGPT 无法联网？** 检查当前代理节点本身是否可用，以及是否命中 `PROXY`。

**规则集下载失败？** 检查网络能否访问 GitHub Raw；不要随意改用未知镜像。

**为什么国内 App 仍显示境外 IP？** `DIRECT` 是从当前网络直接访问，不会把你当前所在地的公网 IP 变成中国大陆 IP。

**所有 App 都被直连/代理？** 检查「全局路由」是否错误地设置为「直连」或「代理」。

## 6. 注意事项

- 不保证按 App 进程精确分流；分流主要依据域名/IP。一个 App 可能使用多个域名。
- 不提供 MITM 证书、不解密 HTTPS、不收集用户日志。
- 默认未匹配流量走 `PROXY`。若代理断开，某些国外请求可能无法访问。
- 公开反馈问题前，遮蔽个人订阅 URL、token、服务器地址及隐私信息。

## 7. 持续连接、DNS 与恢复

在「配置」路由模式下，国内与国际连接按规则使用不同出口，目标是保持 VPN 开启、无需为微信/QQ、B站、淘宝/支付宝与国际服务反复切换模式。默认仍使用 `dns-server = system`，没有新增未经确认的 DNS 参数。

解析超时或切换 Wi-Fi/蜂窝后异常时，按 [DNS 排查](DNS.md) 区分节点失败、解析失败及缓存影响，再重新发起连接检查 DIRECT / PROXY。IPv6、UDP/QUIC 和连续切换的完整验证步骤见 [TESTING.md](TESTING.md)。

恢复：在「配置」页重新选中使用 USR 前备份的配置，保留原订阅与节点；若自行改过 DNS，恢复其备份并重新连接。静态配置检查不等于此版本已在 iPhone/iPad 上验证。
