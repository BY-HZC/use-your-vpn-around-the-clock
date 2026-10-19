"""DNS is opt-in. Syntax/structure assertions are not DNS-leak guarantees."""
import json
from pathlib import Path
import unittest
try:
    import yaml
except ImportError:
    yaml = None

ROOT=Path(__file__).resolve().parent.parent


@unittest.skipUnless(yaml, "PyYAML not installed")
class DNSPolicyTests(unittest.TestCase):
    def setUp(self):
        self.example=yaml.safe_load((ROOT/'dist/mihomo-dns.optional.yaml').read_text())
        self.dns=self.example['dns']

    def test_defaults_do_not_force_dns_or_tun(self):
        for name in ['mihomo.yaml','android-flclash-template.yaml','mihomo-rules.fragment.yaml']:
            with self.subTest(file=name):
                cfg=yaml.safe_load((ROOT/'dist'/name).read_text())
                self.assertNotIn('dns',cfg);self.assertNotIn('tun',cfg)
        self.assertIn('dns-server = system',(ROOT/'dist/shadowrocket.conf').read_text())

    def test_opt_in_structure_and_bootstrap(self):
        self.assertEqual(set(self.example),{'dns'})
        self.assertTrue(self.dns['enable'])
        self.assertTrue(self.dns['respect-rules'])
        self.assertFalse(self.dns['prefer-h3'])
        self.assertEqual(self.dns['enhanced-mode'],'redir-host')
        self.assertNotIn('listen',self.dns)
        self.assertNotIn('ipv6',self.dns)
        self.assertEqual(self.dns['default-nameserver'],['223.5.5.5'])
        for url in self.dns['proxy-server-nameserver']+self.dns['direct-nameserver']:
            self.assertEqual(url,'https://223.5.5.5/dns-query#DIRECT')
        self.assertEqual(self.dns['nameserver'],['https://1.1.1.1/dns-query#PROXY'])

    def test_dns_policy_tracks_canonical_domains(self):
        cfg=json.loads((ROOT/'config/routing.json').read_text())
        policy=self.dns['nameserver-policy']
        for d in cfg['direct_domain_suffixes']+['cn']:
            self.assertEqual(policy['+.'+d],self.dns['direct-nameserver'])
        for d in cfg['proxy_domain_suffixes']:
            self.assertEqual(policy['+.'+d],self.dns['nameserver'])
        self.assertEqual(len(policy),len(cfg['direct_domain_suffixes'])+len(cfg['proxy_domain_suffixes'])+1)

    def test_all_yaml_has_no_duplicate_keys(self):
        class UniqueLoader(yaml.SafeLoader):pass
        def mapping(loader,node,deep=False):
            result={}
            for k,v in node.value:
                key=loader.construct_object(k,deep=deep)
                if key in result:raise ValueError('Duplicate YAML key: '+str(key))
                result[key]=loader.construct_object(v,deep=deep)
            return result
        UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
        for p in (ROOT/'dist').glob('*.yaml'):
            with self.subTest(file=p.name):yaml.load(p.read_text(),Loader=UniqueLoader)
