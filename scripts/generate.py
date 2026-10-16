#!/usr/bin/env python3
"""Build portable configs from config/routing.json. Python standard library only."""
from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
import re
import sys

from generate_android import flclash_script, android_template

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "config" / "routing.json"
DIST = ROOT / "dist"
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)[a-z0-9-]+(?:\.[a-z0-9-]+)+$")


def load():
    cfg = json.loads(SRC.read_text(encoding="utf-8"))
    if cfg["routing"]["default"] != "PROXY":
        raise ValueError("This version must fail closed to PROXY for unmatched traffic")
    domains = []
    for field in ("proxy_domain_suffixes", "direct_domain_suffixes"):
        seq = cfg[field]
        if not seq or len(seq) != len(set(seq)):
            raise ValueError(f"Empty or duplicate entries in {field}")
        for domain in seq:
            if not DOMAIN_RE.fullmatch(domain) or domain.lower() != domain:
                raise ValueError(f"Bad domain in {field}: {domain!r}")
        domains += seq
    if len(domains) != len(set(domains)):
        raise ValueError("Same domain occurs in both PROXY and DIRECT")
    for network in cfg["private_ipv4_cidrs"]:
        if ipaddress.ip_network(network).version != 4:
            raise ValueError(f"Expected IPv4 private CIDR: {network}")
    for network in cfg["private_ipv6_cidrs"]:
        if ipaddress.ip_network(network).version != 6:
            raise ValueError(f"Expected IPv6 private CIDR: {network}")
    for name, url in cfg["upstream"].items():
        if not url.startswith("https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/"):
            raise ValueError(f"Check source URL: {name}")
    return cfg


def shadowrocket(cfg):
    lines = [
        "# Use Your VPN around the clock | GENERATED FILE - DO NOT EDIT",
        "# Source of truth: config/routing.json",
        "# Requires an existing node/subscription; select the node on Shadowrocket Home.",
        "# Remote rules from blackmatrix7; see README for provenance.",
        "", "[General]", "bypass-system = true",
        "skip-proxy = localhost,*.local,10.0.0.0/8,127.0.0.0/8,172.16.0.0/12,192.168.0.0/16,169.254.0.0/16",
        "dns-server = system",
        "", "[Rule]", "# Local / private IP addresses",
    ]
    for c in cfg["private_ipv4_cidrs"]:
        lines.append(f"IP-CIDR,{c},DIRECT,no-resolve")
    for c in cfg["private_ipv6_cidrs"]:
        lines.append(f"IP-CIDR6,{c},DIRECT,no-resolve")
    lines += ["", "# Explicit international services MUST precede China rules"]
    lines += [f"DOMAIN-SUFFIX,{d},PROXY" for d in cfg["proxy_domain_suffixes"]]
    lines += ["", "# Explicit mainland services"]
    lines += [f"DOMAIN-SUFFIX,{d},DIRECT" for d in cfg["direct_domain_suffixes"]]
    up = cfg["upstream"]
    lines += ["", "# Maintained third-party China lists; require network fetch"]
    lines += [
        f"RULE-SET,{up['shadowrocket_china_rules']},DIRECT",
        f"DOMAIN-SET,{up['shadowrocket_china_domains']},DIRECT",
    ]
    if cfg["routing"]["china_tld_direct"]:
        lines.append("DOMAIN-SUFFIX,cn,DIRECT")
    if cfg["routing"]["china_ip_direct"]:
        lines.append("GEOIP,CN,DIRECT")
    lines += ["FINAL,PROXY", ""]
    return "\n".join(lines)


def q(value: str) -> str:
    # JSON double-quoted scalars are valid in YAML 1.2.
    return json.dumps(value, ensure_ascii=False)


def mihomo_parts(cfg):
    provider = [
        'rule-providers:',
        '  china-classical:',
        '    type: http',
        '    behavior: classical',
        '    format: yaml',
        f"    url: {q(cfg['upstream']['mihomo_china_classical'])}",
        '    path: ./ruleset/china-classical.yaml',
        '    interval: 86400',
    ]
    rules = ['rules:', '  # Local / private IP addresses']
    rules += [f'  - {q(f"IP-CIDR,{c},DIRECT,no-resolve")}' for c in cfg['private_ipv4_cidrs']]
    rules += [f'  - {q(f"IP-CIDR6,{c},DIRECT,no-resolve")}' for c in cfg['private_ipv6_cidrs']]
    rules += ['  # Explicit international services']
    rules += [f'  - {q(f"DOMAIN-SUFFIX,{d},PROXY")}' for d in cfg['proxy_domain_suffixes']]
    rules += ['  # Explicit mainland services']
    rules += [f'  - {q(f"DOMAIN-SUFFIX,{d},DIRECT")}' for d in cfg['direct_domain_suffixes']]
    rules += ['  # The maintained upstream rule-provider']
    rules += [f'  - {q("RULE-SET,china-classical,DIRECT")}']
    if cfg['routing']['china_tld_direct']:
        rules.append(f'  - {q("DOMAIN-SUFFIX,cn,DIRECT")}')
    if cfg['routing']['china_ip_direct']:
        rules.append(f'  - {q("GEOIP,CN,DIRECT")}')
    rules.append(f'  - {q("MATCH,PROXY")}')
    return provider, rules


def mihomo(cfg, fragment=False):
    provider, rules = mihomo_parts(cfg)
    header = [
        '# Use Your VPN around the clock | GENERATED FILE - DO NOT EDIT',
        '# Source of truth: config/routing.json',
        '# Matches in order; unmatched traffic uses PROXY.',
    ]
    if fragment:
        header += [
            '# FRAGMENT ONLY, NOT AN IMPORTABLE STANDALONE CONFIG.',
            '# Merge these keys into an existing Mihomo config with a group named PROXY.',
            '# Preserve provider names and rules order; do not create duplicate YAML keys.',
        ]
        return "\n".join(header + [''] + provider + [''] + rules + [''])
    base = [
        '# Replace YOUR_PRIVATE_SUBSCRIPTION_URL with your own Mihomo-compatible provider URL.',
        '# Do NOT commit that secret URL to a public repository.',
        '# This file is a TEMPLATE. No proxy servers or credentials are bundled.',
        '',
        'mixed-port: 7890',
        'allow-lan: false',
        'mode: rule',
        'log-level: warning',
        'proxy-providers:',
        '  my-subscription:',
        '    type: http',
        '    url: "https://example.invalid/YOUR_PRIVATE_SUBSCRIPTION_URL"',
        '    path: ./providers/my-subscription.yaml',
        '    interval: 86400',
        '    health-check:',
        '      enable: true',
        '      url: "https://www.gstatic.com/generate_204"',
        '      interval: 600',
        '',
        'proxy-groups:',
        '  - name: PROXY',
        '    type: select',
        '    use:',
        '      - my-subscription',
        '',
    ]
    return "\n".join(header + base + provider + [''] + rules + [''])


def build(cfg):
    return {
        DIST / 'shadowrocket.conf': shadowrocket(cfg),
        DIST / 'mihomo.yaml': mihomo(cfg),
        DIST / 'mihomo-rules.fragment.yaml': mihomo(cfg, fragment=True),
        DIST / 'flclash-override.js': flclash_script(cfg),
        DIST / 'android-flclash-template.yaml': android_template(cfg, mihomo),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='verify generated files match source')
    args = parser.parse_args()
    files = build(load())
    bad = []
    for path, content in files.items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                bad.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(exist_ok=True, parents=True)
            path.write_text(content, encoding='utf-8')
            print(f'Generated {path.relative_to(ROOT)}')
    if bad:
        print('Out of date generated files: ' + ', '.join(bad), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
