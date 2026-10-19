# Android 使用教程｜FlClash（Mihomo）

> Use Your VPN around the clock Android v0.4.0 Beta · Seamless Routing｜简体中文
>
> **推荐安装方式：已有机场订阅 → 导入 FlClash → 粘贴 `flclash-override.js` → 开启 VPN。** 不需要告诉项目作者你的订阅链接。
>
> 注意：这是社区预览配置，已通过静态测试和脚本模拟测试，尚未实机验证所有 Android / FlClash 版本。

## 1. 适用范围

- Android 手机或平板；客户端选择 **FlClash（Mihomo 内核）**。
- 已拥有能在 FlClash 中正常使用的 Clash / Mihomo 兼容订阅配置。
- 想让中国大陆常见 App / IP **DIRECT（直连）**，ChatGPT、YouTube、Google、Instagram 等指定国际服务 **通过已有订阅的节点**访问。
- 其余未匹配流量按 **PROXY（代理）**处理。

**这不是提供免费代理节点的项目。** `flclash-override.js` 不含任何个人节点、密码或订阅链接。

## 2. 下载并安装 FlClash

官方仓库：<https://github.com/chen08209/FlClash>

官方版本页面：<https://github.com/chen08209/FlClash/releases/latest>

在官方 Releases 中选择符合自己 Android 设备架构的 APK（不确定时优先阅读 Release 附注）。安装后打开 FlClash。不同版本的菜单文字可能有所区别。

## 3. 先导入自己的机场订阅（必须）

1. 进入 FlClash **「配置 / Profiles」** 页面。
2. 点 **「+ / 新增」**，选择 **「从 URL 导入」**（有些版本写「远程」或 `Import from URL`）。
3. 粘贴**自己的**机场订阅链接，确认导入。
4. 在配置列表中点选它，让它变成**当前配置**。
5. 进入「代理 / Proxies」选择一个可以正常使用的节点。
6. 先试着打开一个支持的网址，确认在不安装 USR 脚本的情况下，你的订阅本身已经能连通。

**如果只有 Shadowsocks、VLESS、VMess 等原始节点链接，而没有兼容 Clash/Mihomo 的配置或订阅，需要向订阅服务商获取相应格式；不要把隐私订阅粘贴进公开 Issue。**

## 4. 将 USR 分流脚本加入 FlClash（推荐）

项目文件：[`../dist/flclash-override.js`](../dist/flclash-override.js)

1. 打开 `dist/flclash-override.js`，复制**整个文件**的代码。
2. 在 FlClash 进入 **「工具」→「进阶配置」→「覆写脚本」**（有的版本位于「设置」中）。
3. 新建脚本，名称可填写 `USR - 国内直连 / 国外代理`，把全文粘贴进去并保存。
4. **关键步骤：** 重新进入 **「配置」→ 点击机场订阅右侧「更多 / ⋮」→「覆写」**。
5. 将顶部 **「覆写模式」切换成「脚本」**，并在下方**选中刚才新建的 USR 脚本**。
6. 返回订阅页面，检查 **「预览 / Preview」**：应出现 `usr-china-classical`，规则末尾应是 `MATCH,你的代理组名称`。
7. 在首页将流量模式设置为 **「规则 / Rule」**，不要选「全局 / Global」或「直连 / Direct」。
8. 打开 FlClash 的连接开关，允许 Android 系统弹出的 **VPN 连接请求**，进入「代理」页面确认可用节点仍已选中。

⚠️ **只保存脚本，不在对应订阅的「覆写」中选中脚本，通常不会生效。**

### 自动识别代理组

两端统一使用 `const USR_PROXY_GROUP = "";`。有且仅有一个合格候选时自动选中；广告、拒绝、直连组、静态空组和无代理出口的组被排除。多个候选会报错，此时将空字符串改为准确组名，例如：

```javascript
const USR_PROXY_GROUP = "🌐 Global";
```

保存并重新应用，核对最后一条 `MATCH`。组名不存在或被判定无代理出口时会报错，不会静默改选第一个组。无策略组但有节点/提供者时才新建 `USR-PROXY`（若与节点重名则附加编号）。带过滤器的候选不会自动选中，须核对过滤结果后手动指定。动态提供者尚未加载、过滤器排空、未知组类型可能需要人工检查；脚本不能证明节点在线。包含 DIRECT 的组仍须在客户端选中真实代理节点，切换订阅后也要检查组名。

**重要提醒：** 为了与 iOS 路由逻辑一致，脚本会**替换订阅原有的 `rules` 规则列表**，包括原来可能存在的广告过滤、游戏分流及特殊服务规则；**节点与代理组则保留**。不想覆盖原规则，请先备份订阅并不要使用此覆写脚本。

## 5. 直观验证：打开哔哩哔哩 + ChatGPT

1. 确保 FlClash 已连接，模式显示为 **规则 / Rule**，USR 脚本预览中有 `usr-china-classical`。
2. 打开 **哔哩哔哩**，播放一段视频。
3. 回到 FlClash 的 **「连接 / Connections」** 或「工具 → 连接」查看记录。筛选 `bilibili` / `bilivideo`。
4. `data.bilibili.com` 等常见 B 站域名应显示 **DIRECT**；未列出的 CDN 需要按实际连接判断。
5. 打开 **ChatGPT** 或 **YouTube** 再看「连接」：`openai.com` / `chatgpt.com` / `youtube.com` 应命中订阅代理组，而不是 DIRECT。
6. 如果「连接」页面中没有记录，请检查 Android VPN 是否已授权并且连接正在运行。

| 测试域名 | 期望策略 | 规则依据 |
| --- | --- | --- |
| `data.bilibili.com` | DIRECT | `DOMAIN-SUFFIX,bilibili.com` |
| `qq.com` | DIRECT | `DOMAIN-SUFFIX,qq.com` |
| `ios.chat.openai.com` | 订阅代理组 | `DOMAIN-SUFFIX,openai.com` |
| `youtube.com` | 订阅代理组 | `DOMAIN-SUFFIX,youtube.com` |
| 未手动列出的国内 IP | DIRECT（如 GeoIP 数据可用） | `GEOIP,CN` |
| 其他未知目的地 | 订阅代理组 | `MATCH` 兜底 |

**仅仅看到 App 能联网，不能证明它使用了直连或代理；应当看连接的匹配规则及实际策略。**

## 6. 高级用法：完整 YAML 配置

如果你不想使用覆写脚本，项目还提供 [`../dist/android-flclash-template.yaml`](../dist/android-flclash-template.yaml)。它是**模板**，不是不需要设置就能连接的成品。

1. 把模板保存到**你自己设备的私有目录**，打开文本编辑器。
2. 将其中的 `https://example.invalid/YOUR_PRIVATE_SUBSCRIPTION_URL` 换成自己的 **Mihomo proxy-provider 兼容**订阅 URL。
3. 保存成 `USR-Android.private.yaml`（本项目 `.gitignore` 会忽略 `*.private.yaml`）。
4. FlClash「配置」→「+」→「文件 / File」导入这个私有 YAML。
5. 选择该配置，打开「代理」中的 `PROXY` 组选择节点，再开启 Android VPN。
6. 打开「外部资源 / Providers」检查 `my-subscription` 代理提供者和 `china-classical` 规则提供者已下载成功。

如果服务商只提供完整的 Clash 配置（包含 `proxy-groups` 和 `rules`），**并不保证**能直接把那个 URL 填进 `proxy-providers.url`。此时推荐第 4 节的覆写方法，或向服务商获取专门的代理提供者订阅。

## 7. 常见问题

**导入脚本后没有节点 / 国外服务不通？** 检查当前机场订阅能否单独使用，以及「代理组」是否选对。USR 并不自带节点。若脚本报错，先在对应配置的「覆写」恢复标准模式，确认原订阅还能工作。

**国内服务仍显示代理？** 检查是否处于规则模式、脚本是否真的挂载到当前配置，以及连接是否在这次启动后重新发起。搜索实际访问的域名/IP；部分海外 CDN 并不属于大陆规则集，需要补充专门规则。

**`usr-china-classical` 下载失败？** 远程规则首次下载依赖网络正常访问 GitHub Raw；可以稍后刷新规则集，或检查配置是否已能够正常联网。不要随意相信不明镜像地址。

**打开脚本但看不到它生效？** 查看「配置 → 更多 → 覆写」是不是仍选择「标准」，脚本模式是否确实勾选新建脚本；必要时查看「预览」或客户端日志。

**为什么直连后，视频网站依然提示地区限制？** DIRECT 使用的是你当前网络的公网 IP，不能自动变成中国大陆 IP。

**会自动更新吗？** blackmatrix7 的 China 规则集按配置定时拉取（当前设置 `86400` 秒）；但本仓库中自定义域名清单更新后，**FlClash 本地粘贴的 JS 脚本不会自动更新**，需要从 GitHub 复制新版脚本重新保存。

**会和其他 Android VPN 同时工作吗？** 同一 Android 用户配置通常不能同时开启两个常规 VpnService VPN。系统若已有其他 VPN，可能需要先关闭另一个连接。

## 8. 安全及开源说明

- 请勿向别人公开机场订阅 URL、访问令牌、账号密码、私钥及包含这些内容的日志。
- 本项目无广告、无 MITM 解密配置，也没有任何流量上传服务端；它只定义本地路由和第三方规则集地址。
- 公开脚本不会知道你的订阅地址，但客户端会按自己的配置向节点服务商与 GitHub Raw 发出相应网络请求。
- 配置经过脚本语法与仿真测试，不代表已在你的安卓设备上通过真实联网测试。遇到问题可分享**已遮蔽 token、服务器 IP、订阅地址及个人数据**的截图。

## 官方参考

- FlClash: https://github.com/chen08209/FlClash
- FlClash Releases: https://github.com/chen08209/FlClash/releases/latest
- Mihomo proxy-providers: https://wiki.metacubex.one/en/config/proxy-providers/
- blackmatrix7 China rules: https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Clash/China/README.md

## v0.4.0：持续连接、DNS 与恢复

在规则模式下，国内连接走 DIRECT、国际服务走已选代理组，日常切换 App 不需要反复关闭 VPN。先按 [连续切换测试清单](TESTING.md) 检查微信/QQ、B站、淘宝/支付宝与国际服务；只看到 App 能联网不够，还需核对连接策略。

脚本保留订阅的 DNS 和 TUN，不自动使用可选 DNS。解析超时、IPv6 或 Wi-Fi/蜂窝切换异常时按 [DNS 排查](DNS.md) 区分 DNS 和节点故障，先恢复原设置再比较。

恢复原订阅：在当前订阅「覆写」恢复此前模式/备份脚本（原本为标准模式时选标准），保存并重新应用；核对最终规则已恢复。公开反馈只提供脱敏片段。Node 模拟和内核解析检查不能代替 Android 真机、UDP/QUIC 和 DNS 验证。
