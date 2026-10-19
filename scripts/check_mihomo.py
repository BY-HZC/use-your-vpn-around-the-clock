#!/usr/bin/env python3
"""Optional core syntax check with synthetic nodes; requires PyYAML and Node.js.

Never reads user subscriptions. Does not start a proxy service or test connectivity.
The core may download its public GeoIP database into --data-dir when absent.
"""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import tempfile

import yaml

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', required=True, type=Path)
    parser.add_argument('--data-dir', required=True, type=Path)
    args = parser.parse_args()
    core = args.core.resolve()
    data_dir = args.data_dir.resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(core), '-v'], check=True)
    # RFC 5737 documentation address; deliberately not a usable service.
    node = {'name': 'TEST-NODE', 'type': 'socks5', 'server': '192.0.2.1', 'port': 9}
    base = {'proxies': [node], 'proxy-groups': [
        {'name': 'PROXY', 'type': 'select', 'proxies': ['TEST-NODE']}], 'mode': 'rule'}
    with tempfile.TemporaryDirectory(prefix='usr-core-', dir=data_dir) as tmp:
        tmp = Path(tmp)
        subscription = tmp/'nodes.yaml'
        subscription.write_text(yaml.safe_dump({'proxies': [node]}))
        rules = tmp/'rules.yaml'
        rules.write_text('payload:\n  - DOMAIN-SUFFIX,example.cn\n')
        cases = {}
        for name in ['mihomo.yaml', 'android-flclash-template.yaml', 'mihomo-rules.fragment.yaml']:
            cfg = yaml.safe_load((ROOT/'dist'/name).read_text())
            if name.endswith('fragment.yaml'):
                cfg = {**copy.deepcopy(base), **cfg}
            # Substitute only external provider inputs, preserve every generated routing rule.
            if 'proxy-providers' in cfg:
                cfg['proxy-providers'] = {'my-subscription': {'type': 'file', 'path': str(subscription)}}
            cases[name] = cfg
        for name in ['flclash-override.js', 'clash-verge-rev-override.js']:
            code = '''const fs=require('fs'),vm=require('vm');const ctx={};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);
console.log(JSON.stringify(ctx.main(JSON.parse(fs.readFileSync(0,'utf8')))));'''
            result = subprocess.run(['node', '-e', code, str(ROOT/'dist'/name)],
                                    input=json.dumps(base), text=True, capture_output=True, check=True)
            cases[name] = json.loads(result.stdout)
        dns = yaml.safe_load((ROOT/'dist/mihomo-dns.optional.yaml').read_text())['dns']
        passed = 0
        for name, original in cases.items():
            for with_dns in [False, True]:
                cfg = copy.deepcopy(original)
                for key in cfg['rule-providers']:
                    cfg['rule-providers'][key] = {'type': 'file', 'path': str(rules),
                                                  'behavior': 'classical', 'format': 'yaml'}
                if with_dns:
                    cfg['dns'] = copy.deepcopy(dns)
                target = tmp/'check.yaml'
                target.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
                print(f'CHECK {name} optional_dns={with_dns}', flush=True)
                subprocess.run([str(core), '-t', '-d', str(data_dir), '-f', str(target)],
                               check=True, timeout=120)
                passed += 1
        print(f'{passed} core configuration checks passed (synthetic provider inputs; no traffic test).')


if __name__ == '__main__':
    main()
