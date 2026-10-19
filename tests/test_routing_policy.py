"""First-match simulations: fake GeoIP/remote membership, not network validation."""
import copy
import ipaddress
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'scripts'))
import generate
try:
    import yaml
except ImportError:
    yaml = None


def match(rules, domain='', ip=None, cn=False, upstream=False):
    for rule in rules:
        parts = rule.split(','); kind=parts[0]
        if kind in ('MATCH','FINAL'):
            return parts[1]
        value, policy = parts[1:3]
        if kind == 'DOMAIN-SUFFIX' and (domain == value or domain.endswith('.'+value)):
            return policy
        if kind in ('IP-CIDR','IP-CIDR6') and ip:
            if ipaddress.ip_address(ip) in ipaddress.ip_network(value):
                return policy
        if kind in ('RULE-SET','DOMAIN-SET') and upstream:
            return policy
        if kind == 'GEOIP' and cn:
            return policy
    raise AssertionError('No final match')


@unittest.skipUnless(yaml, "PyYAML not installed")
class RoutingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.cfg=generate.load()
        self.outputs={}
        for name in ['mihomo.yaml','android-flclash-template.yaml','mihomo-rules.fragment.yaml']:
            self.outputs[name]=yaml.safe_load((ROOT/'dist'/name).read_text())['rules']
        text=(ROOT/'dist/shadowrocket.conf').read_text().split('[Rule]\n')[1]
        self.outputs['shadowrocket.conf']=[r for r in text.splitlines() if r and not r.startswith('#')]

    def test_international_domains_before_upstream_and_cn_geoip(self):
        for name,rules in self.outputs.items():
            for d in self.cfg['proxy_domain_suffixes']:
                with self.subTest(output=name,domain=d):
                    self.assertEqual(match(rules,'api.'+d,ip='2001:db8::1',cn=True,upstream=True),'PROXY')

    def test_domestic_service_and_subdomain_coverage(self):
        for name,rules in self.outputs.items():
            for d in ['weixin.qq.com','im.qq.com','data.bilibili.com','video.bilivideo.com',
                      'www.taobao.com','www.alipay.com'] + self.cfg['direct_domain_suffixes']:
                with self.subTest(output=name,domain=d):
                    self.assertEqual(match(rules,d),'DIRECT')

    def test_suffix_boundary_and_unknown_fallback(self):
        for name,rules in self.outputs.items():
            for d in ['evilqq.com','qq.com.example.org','unknown.example.org']:
                with self.subTest(output=name,domain=d):
                    self.assertEqual(match(rules,d),'PROXY')

    def test_private_v4_v6_precedence_and_cn_fallback(self):
        for name,rules in self.outputs.items():
            for ip in ['10.0.0.1','192.168.1.1','127.0.0.1','169.254.1.1','::1','fd00::1','fe80::1']:
                with self.subTest(output=name,ip=ip):
                    self.assertEqual(match(rules,'chatgpt.com',ip),'DIRECT')
            for ip in ['192.0.2.1','2001:db8::1']:
                # CN is deliberately mocked; documentation addresses are not classified as China.
                self.assertEqual(match(rules,ip=ip,cn=True),'DIRECT')
                self.assertEqual(match(rules,ip=ip,cn=False),'PROXY')
            self.assertEqual(match(rules,'unlisted.cn'),'DIRECT')

    def test_exact_and_nested_policy_conflicts_rejected(self):
        for field,value in [('direct_domain_suffixes','openai.com'),
                            ('direct_domain_suffixes','api.openai.com'),
                            ('proxy_domain_suffixes','api.qq.com'),
                            ('proxy_domain_suffixes','com')]:
            cfg=copy.deepcopy(self.cfg);cfg[field].append(value)
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                generate.validate(cfg)

    def test_same_policy_redundancy_rejected(self):
        for d in ['qq.com','weixin.qq.com']:
            cfg=copy.deepcopy(self.cfg);cfg['direct_domain_suffixes'].append(d)
            with self.subTest(domain=d),self.assertRaises(ValueError):generate.validate(cfg)

    def test_rules_do_not_restrict_transport(self):
        for rules in self.outputs.values():
            self.assertFalse(any(r.startswith(('NETWORK,','DST-PORT,')) for r in rules))
            # Domain/IP rule simulation is transport independent. Real UDP support belongs to client/node.
            self.assertEqual(match(rules,'youtube.com'),'PROXY')
