"""Clash Verge Rev main(config) contract simulations, not Boa/device tests."""
from pathlib import Path
import json
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'dist/clash-verge-rev-override.js'


@unittest.skipUnless(shutil.which('node'), 'Node.js not installed')
class ClashVergeTests(unittest.TestCase):
    def run_js(self, body):
        code = '''const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(SCRIPT_PATH, 'utf8');
function apply(config, group = '') {
  const ctx = {};
  vm.runInNewContext(source.replace('const USR_PROXY_GROUP = "";',
    'const USR_PROXY_GROUP = ' + JSON.stringify(group) + ';'), ctx);
  return ctx.main(config, 'test profile');
}
'''.replace('SCRIPT_PATH', json.dumps(str(SCRIPT))) + body
        result = subprocess.run(['node', '-e', code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_preserves_subscription_and_app_settings(self):
        self.run_js('''
const config = {
  proxies: [{name:'node-A',type:'ss'}],
  'proxy-groups': [{name:'PROXY',type:'select',proxies:['node-A']}],
  'proxy-providers': {local:{type:'file',path:'./example.yaml'}},
  'rule-providers': {old:{type:'file',path:'./old.yaml',behavior:'classical'}},
  dns:{enable:true},tun:{enable:false},mode:'global',rules:['MATCH,DIRECT']
};
const refs = {proxies:config.proxies,groups:config['proxy-groups'],
  providers:config['proxy-providers'],dns:config.dns,tun:config.tun};
const out = apply(config);
assert.strictEqual(out,config);
assert.strictEqual(out.proxies,refs.proxies);
assert.strictEqual(out['proxy-groups'],refs.groups);
assert.strictEqual(out['proxy-providers'],refs.providers);
assert.strictEqual(out.dns,refs.dns);
assert.strictEqual(out.tun,refs.tun);
assert.strictEqual(out.mode,'global'); // Rule mode must be chosen in the app.
assert(out['rule-providers'].old);
assert(out['rule-providers']['usr-china-classical']);
assert(!out.rules.includes('MATCH,DIRECT'));
assert.strictEqual(out.rules.filter(r=>r.startsWith('MATCH,')).length,1);
assert.strictEqual(out.rules.at(-1),'MATCH,PROXY');
assert(out.rules.indexOf('DOMAIN-SUFFIX,openai.com,PROXY') <
  out.rules.indexOf('RULE-SET,usr-china-classical,DIRECT'));
assert.strictEqual(out.rules[0],'IP-CIDR,127.0.0.0/8,DIRECT,no-resolve');
assert(out.rules.includes('DOMAIN-SUFFIX,bilibili.com,DIRECT'));
assert(out.rules.includes('GEOIP,CN,DIRECT'));
assert(out.rules.includes('IP-CIDR6,fc00::/7,DIRECT,no-resolve'));
const again = apply(out);
assert.strictEqual(again.rules.filter(r=>r.startsWith('MATCH,')).length,1);
''')

    def test_exact_group_fallback_and_errors(self):
        self.run_js('''
const config = {proxies:[{name:'node-A',type:'ss'}], 'proxy-groups':[
  {name:'PROXY',type:'select',proxies:['node-A']},
  {name:'My Desktop',type:'select',proxies:['node-A']}
]};
assert.strictEqual(apply(config,'My Desktop').rules.at(-1),'MATCH,My Desktop');
assert.throws(()=>apply(config,'missing'),/指定的代理组不存在/);
assert.throws(()=>apply(null),/Invalid subscription/);
assert.throws(()=>apply({}),/订阅/);
for (const c of [
  {proxies:[{name:'node-A',type:'ss'}]},
  {'proxy-providers':{local:{type:'file',path:'./example.yaml'}}}
]) {
 const out=apply(c);
 assert.strictEqual(out.rules.at(-1),'MATCH,USR-PROXY');
 assert(out['proxy-groups'].some(g=>g.name==='USR-PROXY'));
 assert(!Object.hasOwn(out,'mode'));
}
''')

    def test_shared_policy_and_syntax(self):
        result = subprocess.run(['node', '--check', str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.run_js('''
const routing=JSON.parse(fs.readFileSync(ROUTING_PATH,'utf8'));
const desktop=apply({proxies:[{name:'node-A',type:'ss'}], 'proxy-groups':[{name:'PROXY',type:'select',proxies:['node-A']}]});
for(const d of routing.proxy_domain_suffixes)
 assert(desktop.rules.includes(`DOMAIN-SUFFIX,${d},PROXY`));
for(const d of routing.direct_domain_suffixes)
 assert(desktop.rules.includes(`DOMAIN-SUFFIX,${d},DIRECT`));
const ctx={};vm.runInNewContext(fs.readFileSync(ANDROID_PATH,'utf8'),ctx);
assert.deepStrictEqual(Array.from(desktop.rules),Array.from(ctx.main({
 proxies:[{name:'node-A',type:'ss'}], 'proxy-groups':[{name:'PROXY',type:'select',proxies:['node-A']}]
}).rules));
'''.replace('ROUTING_PATH', json.dumps(str(ROOT/'config/routing.json')))
           .replace('ANDROID_PATH', json.dumps(str(ROOT/'dist/flclash-override.js'))))
