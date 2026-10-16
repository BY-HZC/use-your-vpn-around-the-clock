"""Minimal consistency and routing-priority tests."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent


class GeneratedConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routing = json.loads((ROOT / 'config/routing.json').read_text(encoding='utf-8'))
        cls.shadowrocket = (ROOT / 'dist/shadowrocket.conf').read_text(encoding='utf-8')
        cls.mihomo = (ROOT / 'dist/mihomo.yaml').read_text(encoding='utf-8')
        cls.fragment = (ROOT / 'dist/mihomo-rules.fragment.yaml').read_text(encoding='utf-8')

    def test_regeneration_is_reproducible(self):
        result = subprocess.run(
            [sys.executable, 'scripts/generate.py', '--check'], cwd=ROOT,
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_shadowrocket_precedence_and_fallback(self):
        cfg = self.shadowrocket
        self.assertIn('[General]\n', cfg)
        self.assertIn('[Rule]\n', cfg)
        self.assertLess(cfg.index('DOMAIN-SUFFIX,openai.com,PROXY'), cfg.index('RULE-SET,https://'))
        self.assertIn('DOMAIN-SUFFIX,bilibili.com,DIRECT', cfg)
        self.assertIn('GEOIP,CN,DIRECT', cfg)
        self.assertIn('IP-CIDR6,fc00::/7,DIRECT,no-resolve', cfg)
        self.assertEqual(cfg.rstrip().splitlines()[-1], 'FINAL,PROXY')

    def test_mihomo_precedence_and_template(self):
        cfg = self.mihomo
        self.assertLess(cfg.index('DOMAIN-SUFFIX,openai.com,PROXY'), cfg.index('RULE-SET,china-classical,DIRECT'))
        self.assertIn('DOMAIN-SUFFIX,bilibili.com,DIRECT', cfg)
        self.assertIn('GEOIP,CN,DIRECT', cfg)
        self.assertIn('IP-CIDR6,fc00::/7,DIRECT,no-resolve', cfg)
        self.assertIn('MATCH,PROXY', cfg)
        self.assertIn('https://example.invalid/YOUR_PRIVATE_SUBSCRIPTION_URL', cfg)
        self.assertIn('allow-lan: false', cfg)
        self.assertIn('behavior: classical', cfg)
        self.assertIn('use:\n      - my-subscription', cfg)

    def test_rule_sets_are_compatible_with_targets(self):
        self.assertIn('/rule/Shadowrocket/China/China.list', self.shadowrocket)
        self.assertIn('/rule/Shadowrocket/China/China_Domain.list', self.shadowrocket)
        self.assertIn('/rule/Clash/China/China_Classical.yaml', self.mihomo)
        self.assertIn('FRAGMENT ONLY', self.fragment)
        self.assertNotIn('proxy-providers:', self.fragment)

    def test_yaml_parse_when_pyyaml_present(self):
        try:
            import yaml
        except ImportError:
            self.skipTest('Install PyYAML for optional structural YAML validation')
        full = yaml.safe_load(self.mihomo)
        frag = yaml.safe_load(self.fragment)
        self.assertEqual(full['mode'], 'rule')
        self.assertEqual(full['proxy-groups'][0]['name'], 'PROXY')
        self.assertEqual(full['rules'][-1], 'MATCH,PROXY')
        self.assertEqual(full['rule-providers']['china-classical']['behavior'], 'classical')
        self.assertEqual(full['proxy-providers']['my-subscription']['type'], 'http')
        self.assertEqual(frag['rules'][-1], 'MATCH,PROXY')


if __name__ == '__main__':
    unittest.main()
