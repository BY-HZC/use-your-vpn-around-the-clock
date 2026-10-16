"""Static generation + Node.js simulation for FlClash override compatibility."""
from pathlib import Path
import json
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'dist' / 'flclash-override.js'
TEMPLATE = ROOT / 'dist' / 'android-flclash-template.yaml'


class FlClashAndroidTests(unittest.TestCase):
    def test_template_valid_yaml(self):
        try:
            import yaml
        except ImportError:
            self.skipTest('PyYAML not installed')
        config = yaml.safe_load(TEMPLATE.read_text(encoding='utf-8'))
        self.assertEqual(config['mode'], 'rule')
        self.assertEqual(config['rules'][-1], 'MATCH,PROXY')
        self.assertEqual(config['rule-providers']['china-classical']['behavior'], 'classical')
        self.assertEqual(config['proxy-groups'][0]['name'], 'PROXY')

    @unittest.skipUnless(shutil.which('node'), 'Node.js not installed')
    def test_script_syntax_and_runtime(self):
        self.assertEqual(subprocess.run(['node', '--check', str(SCRIPT)], capture_output=True).returncode, 0)
        cases = [
            {'proxies': [{'name': 'JP-1', 'type': 'ss'}],
             'proxy-groups': [{'name': '🚀 节点选择', 'type': 'select', 'proxies': ['JP-1']}],
             'rules': ['MATCH,DIRECT'], 'mode': 'global',
             'rule-providers': {'old': {'type': 'file', 'path': './old.yaml', 'behavior': 'classical'}}},
            {'proxies': [{'name': 'JP-1', 'type': 'ss'}], 'rules': []},
            {'proxy-providers': {'subscriber': {'type': 'http', 'url': 'https://private.invalid/sub'}}},
        ]
        node_script = f'''
const fs = require('fs'); const vm = require('vm');
const s = fs.readFileSync({json.dumps(str(SCRIPT))}, 'utf8');
const testCases = {json.dumps(cases, ensure_ascii=False)};
for (const c of testCases) {{
  const ctx = {{}};
  vm.runInNewContext(s, ctx);
  const result = ctx.main(c);
  if (result.mode !== 'rule' || !result['rule-providers']['usr-china-classical']) throw Error('No rule mode / remote provider');
  if (result.rules.find(r => r.startsWith('DOMAIN-SUFFIX,openai.com,')).endsWith(',DIRECT')) throw Error('AI not proxy');
  if (!result.rules.includes('DOMAIN-SUFFIX,bilibili.com,DIRECT')) throw Error('Bili not DIRECT');
  if (!result.rules.includes('GEOIP,CN,DIRECT')) throw Error('CN IP no direct');
  if (!result.rules.includes('RULE-SET,usr-china-classical,DIRECT')) throw Error('Provider not used');
  if (!result.rules[result.rules.length-1].startsWith('MATCH,')) throw Error('Missing final match');
  if (result.rules.filter(r => r.startsWith('MATCH,')).length !== 1) throw Error('Duplicate MATCH');
}}
const custom = vm.runInNewContext(s+'\\nmain({{proxies:[{{name:"X",type:"ss"}}],rules:[]}})');
if (custom.rules[custom.rules.length-1] !== 'MATCH,USR-PROXY') throw Error('Fallback failed');
let threw = false;
try {{vm.runInNewContext(s+'\\nmain({{}})')}} catch(e) {{threw=true}}
if (!threw) throw Error('No nodes must fail loudly');
console.log('FlClash script: 4 simulation scenarios passed');
'''
        r = subprocess.run(['node', '-e', node_script], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

if __name__ == '__main__':
    unittest.main()
