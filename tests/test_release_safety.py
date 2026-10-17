"""Checks for accidental secret publication and expected release files."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = [
    'config/routing.json', 'dist/shadowrocket.conf', 'dist/flclash-override.js',
    'dist/android-flclash-template.yaml', 'dist/mihomo.yaml',
    'dist/mihomo-rules.fragment.yaml', 'docs/IOS.md', 'docs/ANDROID.md',
    'docs/PUBLISHING.md', 'docs/TESTING.md', '.github/workflows/check.yml',
    'AGENTS.md', 'README.md', 'LICENSE', 'CHANGELOG.md',
    'dist/clash-verge-rev-override.js', 'docs/DESKTOP.md',
]
# Intentional narrow heuristic: CI is not a replacement for a manual security review.
SECRET_PATTERNS = [
    re.compile(r'ghp_[A-Za-z0-9]{36}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{40,}'),
    re.compile(r'glpat-[A-Za-z0-9_-]{20,}'),
    re.compile(r'sk-[A-Za-z0-9]{32,}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
]

class ReleaseSafetyTests(unittest.TestCase):
    def test_expected_files_present(self):
        for rel in EXPECTED:
            with self.subTest(file=rel):
                self.assertTrue((ROOT / rel).is_file())

    def test_no_obvious_private_tokens(self):
        for path in ROOT.rglob('*'):
            if not path.is_file() or path.suffix in {'.pyc', '.png', '.jpg', '.zip'}:
                continue
            if '.git' in path.parts or '__pycache__' in path.parts:
                continue
            content = path.read_text(encoding='utf-8', errors='ignore')
            for pattern in SECRET_PATTERNS:
                with self.subTest(file=str(path.relative_to(ROOT)), pattern=pattern.pattern):
                    self.assertIsNone(pattern.search(content))

    def test_templates_do_not_embed_real_subscriptions(self):
        for rel in ('dist/mihomo.yaml', 'dist/android-flclash-template.yaml'):
            with self.subTest(file=rel):
                content = (ROOT / rel).read_text(encoding='utf-8')
                self.assertIn('https://example.invalid/YOUR_PRIVATE_SUBSCRIPTION_URL', content)

if __name__ == '__main__':
    unittest.main()
