# Contributing / 贡献规则

欢迎提交经核实的域名、修复和客户端适配建议。

1. 只在 `config/routing.json` 修改共享域名规则；不要直接修改 `dist/` 下的文件。
2. 运行 `python3 scripts/generate.py` 重新生成全部配置。
3. 运行 `python3 scripts/generate.py --check` 和 `python3 -m unittest discover -s tests -v`。
4. Pull Request 描述需包括域名归属、为什么走直连或代理、测试设备与日志截图（记得遮盖 IP、用户名、订阅 token）。
5. 不得提交任何个人订阅链接、密钥、账号、设备标识符等敏感信息。

目前仅支持 Shadowrocket 与 Mihomo 输出。新客户端支持请在 PR 中附上其官方语法资料和测试记录。
