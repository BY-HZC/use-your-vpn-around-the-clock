"""Shared Android/desktop selection regressions; no private subscriptions or network."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ['flclash-override.js', 'clash-verge-rev-override.js']


def group(name, options=None, **extra):
    return dict(name=name, type='select', proxies=options or [], **extra)


def profile(groups):
    return {'proxies': [{'name': 'JP-1', 'type': 'ss'}, {'name': 'US-1', 'type': 'ss'}],
            'proxy-groups': groups, 'rules': ['MATCH,DIRECT'],
            'dns': {'enable': True, 'nameserver': ['system']}, 'tun': {'enable': True}}


def execute(script, config, selected=''):
    js = '''const fs=require('fs'),vm=require('vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const source=fs.readFileSync(input.script,'utf8').replace('const USR_PROXY_GROUP = "";',
 'const USR_PROXY_GROUP = '+JSON.stringify(input.selected)+';');
const ctx={};vm.runInNewContext(source,ctx);
const before=JSON.stringify(input.config);
const keys=['proxies','proxy-providers','dns','tun','proxy-groups'];
const refs=keys.map(k=>input.config && input.config[k]);
try { const result=ctx.main(input.config);
 console.log(JSON.stringify({result,retained:keys.every((k,i)=>
  refs[i] === undefined || (k === "proxy-groups" && refs[i].length === 0) || result[k]===refs[i])}));
} catch(e) {console.log(JSON.stringify({error:e.message,unchanged:before===JSON.stringify(input.config)}));}
'''
    r = subprocess.run(['node', '-e', js], input=json.dumps(dict(
        script=str(ROOT/'dist'/script), config=config, selected=selected)),
        capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


@unittest.skipUnless(shutil.which('node'), 'Node.js not installed')
class ProxySelectionTests(unittest.TestCase):
    def check(self, config, target=None, selected='', error=None):
        for script in SCRIPTS:
            with self.subTest(script=script, target=target, error=error):
                out = execute(script, config, selected)
                if error:
                    self.assertIn(error, out.get('error', ''))
                    self.assertTrue(out['unchanged'])
                else:
                    self.assertNotIn('error', out, out)
                    self.assertTrue(out['retained'])
                    self.assertEqual(out['result']['rules'][-1], 'MATCH,'+target)
                    if 'dns' in config:
                        self.assertEqual(out['result']['dns'], config['dns'])
                    self.assertEqual(out['result'].get('tun'), config.get('tun'))
                    self.assertIn('DOMAIN-SUFFIX,openai.com,'+target, out['result']['rules'])

    def test_reported_adblock_before_global(self):
        self.check(profile([group('🚫 广告拦截',['REJECT','DIRECT']),
                            group('🌐 Global',['JP-1','US-1'])]), '🌐 Global')

    def test_special_names_and_literal_dollar_replacement(self):
        self.check(profile([group('出口 $& $` 日本',['JP-1'])]), '出口 $& $` 日本')

    def test_empty_direct_reject_and_unknown_reference_excluded(self):
        self.check(profile([group('empty'),group('local',['DIRECT']),group('drop',['REJECT-DROP']),
                            group('unknown',['missing']),group('exit',['JP-1'])]),'exit')

    def test_blocking_name_even_if_contains_proxy_node(self):
        for name in ['广告拦截','拒绝连接','仅直连','AdBlock','REJECT traffic','Direct only']:
            self.check(profile([group(name,['JP-1']),group('exit',['US-1'])]),'exit')

    def test_multiple_candidates_never_select_first(self):
        for groups in [[group('PROXY',['JP-1']),group('🌐 Global',['US-1'])],
                       [group('a',['JP-1']),group('b',['US-1'])]]:
            self.check(profile(groups),error='USR_PROXY_GROUP')
            self.check(profile(list(reversed(groups))),error='USR_PROXY_GROUP')

    def test_explicit_group_both_clients(self):
        self.check(profile([group('a',['JP-1']),group('b',['US-1'])]),'b',selected='b')
        self.check(profile([group('a',['JP-1'])]),selected='missing',error='不存在')
        self.check(profile([group('only-direct',['DIRECT'])]),selected='only-direct',error='代理出口')

    def test_no_fallback_when_existing_groups_unusable(self):
        for groups in [[group('empty')],[group('local',['DIRECT'])],[group('Ads',['REJECT'])]]:
            self.check(profile(groups),error='USR_PROXY_GROUP')

    def test_nested_groups_cycles_and_non_proxy_nodes(self):
        self.check(profile([group('a',['b']),group('b',['a'])]),error='代理出口')
        self.check(profile([group('a',['b']),group('b',['a','JP-1'])]),'a',selected='a')
        cfg=profile([group('a',['local-node'])]);cfg['proxies']=[{'name':'local-node','type':'direct'}]
        self.check(cfg,error='代理出口')

    def test_providers_include_all_and_missing_provider(self):
        for extra in [{'use':['provider']},{'include-all':True},{'include-all-providers':True}]:
            cfg=profile([group('exit',**extra)]);cfg['proxies']=[]
            cfg['proxy-providers']={'provider':{'type':'file','path':'./example.yaml'}}
            self.check(cfg,'exit')
        self.check(profile([group('exit',use=['missing'])]),error='代理出口')
        self.check(profile([group('exit',**{'include-all-proxies':True})]),'exit')

    def test_fallback_keeps_nodes_and_providers_and_avoids_collision(self):
        cfg=profile([]);cfg['proxies'].append({'name':'USR-PROXY','type':'ss'})
        cfg['proxy-providers']={'provider':{'type':'file','path':'./example.yaml'}}
        self.check(cfg,'USR-PROXY-2')
        cfg=profile([]);cfg['proxies']=[]
        cfg['proxy-providers']={'provider':{'type':'file','path':'./example.yaml'}}
        self.check(cfg,'USR-PROXY')
        self.check({},error='订阅')

    def test_malformed_names_and_config(self):
        for name in ['bad,name','bad\nname','bad\rname']:
            self.check(profile([group(name,['JP-1'])]),error='名称')
        self.check(profile([group('same',['JP-1']),group('same',['US-1'])]),error='重复')
        self.check({'proxy-groups':{}},error='列表')
        self.check([],error='Invalid')
        self.check(None,error='Invalid')

    def test_success_retains_settings_and_second_application(self):
        cfg=profile([group('exit',['JP-1'])]);cfg['proxy-providers']={'provider':{'type':'file','path':'./example.yaml'}}
        cfg['rule-providers']={'other':{'type':'file','path':'./other.yaml','behavior':'classical'}}
        for script in SCRIPTS:
            with self.subTest(script=script):
                out=execute(script,cfg)
                self.assertTrue(out['retained'])
                self.assertEqual(out['result']['rule-providers']['other'],cfg['rule-providers']['other'])
                again=execute(script,out['result'])
                self.assertEqual(again['result'],out['result'])

    def test_empty_inline_provider_not_a_proxy_exit(self):
        for payload in [[], [{'name':'local','type':'direct'}]]:
            cfg=profile([group('exit',use=['inline'])]);cfg['proxies']=[]
            cfg['proxy-providers']={'inline':{'type':'inline','payload':payload}}
            self.check(cfg,error='代理出口')
        cfg['proxy-providers']['inline']['payload']=[{'name':'JP-1','type':'ss'}]
        self.check(cfg,'exit')

    def test_filters_require_manual_confirmation(self):
        cfg=profile([group('exit',['JP-1'],filter='US')])
        self.check(cfg,error='USR_PROXY_GROUP')
        self.check(cfg,'exit',selected='exit')
        cfg=profile([group('exit',use=['provider'])])
        cfg['proxy-providers']={'provider':{'type':'file','path':'./example.yaml','filter':'US'}}
        self.check(cfg,error='USR_PROXY_GROUP')
