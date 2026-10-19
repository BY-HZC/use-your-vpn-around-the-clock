# Changelog

## v0.4.0-beta.1 — Seamless Routing（2026-10-19，预发布）

- 修复广告拦截组被误选为最终代理出口的问题，Android/桌面使用同一代理组检查逻辑。
- Android 新增与桌面一致的 `USR_PROXY_GROUP`；排除明显广告/拒绝/直连组、静态空组和无代理出口组，多候选明确报错。
- 保留原节点、代理提供者、已有代理组及 DNS/TUN；无组时创建 USR-PROXY，并处理与节点重名。
- 统一源移除被 qq.com 覆盖的 weixin.qq.com，增加域名重复与父子后缀冲突检查；不猜测新应用域名。
- 新增可选 Mihomo DNS 片段与 DNS 排查说明，默认不合并，Shadowrocket 保持 system DNS。
- 扩充至 38 项自动化测试；Mihomo v1.19.32 合成输入配置解析 10/10 通过。
- 完善四平台持续连接、应用连续切换、DNS/IPv6/UDP、网络切换和恢复清单；补充维护者提供的 iOS 有限实机反馈，完整跨平台真机验收仍待完成。
- 未加入一键导入、GitHub 自动更新、网站、新客户端、测速或节点切换。

## v0.3 后续桌面适配（main）

- Windows / macOS 适配 Clash Verge Rev 最新稳定版的订阅扩展脚本接口。
- 添加桌面导入、规则验证、更新与恢复教程，保留通用 Mihomo 模板。
- 新增桌面脚本模拟测试；本版本仍需 Windows / macOS 真机验证。

## v0.3.0-beta.1 (release preparation)

- 项目命名为 Use Your VPN around the clock，保留 USR 配置标识。
- 统一各客户端的内网规则优先级。
- 整理 iOS 与 Android 统一仓库结构，补充 Shadowrocket iOS 教程。
- 增加 GitHub / Codex 发布指南和发布前检查说明。
- 保留 v0.2 的统一规则源、FlClash 覆写脚本、Mihomo 模板与 CI 测试。
- 仍属社区预览版：并未宣称 Android 或所有客户端已完成真机验证。

## v0.2 Beta

- 添加 FlClash JavaScript 覆写与 Android 中文教程。
- 添加 Android 完整 Mihomo YAML 模板与脚本模拟测试。

## v0.1 Beta

- 首版统一规则源、Shadowrocket 与 Mihomo 输出、Python 生成器及 CI。
