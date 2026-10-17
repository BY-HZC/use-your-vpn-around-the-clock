"""Generate FlClash Android files from the shared routing policy."""
import json


JS_TEMPLATE = '''// Use Your VPN around the clock - FlClash override script (GENERATED)
// Paste this in FlClash > Tools > Advanced settings > Override scripts.
// Select the script for YOUR subscription in Profiles > More > Override > Script.
// Keeps the subscription's nodes and proxy groups; REPLACES its original rules.
// No personal URL or credentials are included here.

const USR_RULES = __USR_DATA__;

function main(config) {
  if (!config || typeof config !== "object") {
    throw new Error("USR: Invalid subscription profile");
  }
  const groups = Array.isArray(config["proxy-groups"]) ? config["proxy-groups"] : [];
  const usable = groups.filter(g => g && typeof g.name === "string" && g.name &&
    !["DIRECT", "REJECT", "PASS", "GLOBAL"].includes(g.name));
  const names = usable.map(g => g.name);
  const preferred = ["PROXY", "Proxy", "proxy", "🚀 节点选择", "节点选择", "选择节点", "代理", "🚀 Proxy", "节点切换", "♻️ 自动选择"];
  let target = preferred.find(n => names.includes(n));
  if (!target) {
    const byName = usable.find(g => /节点|选择|代理|proxy|select|自动|机场/i.test(g.name));
    const bySelect = usable.find(g => g.type === "select");
    target = (byName || bySelect || usable[0] || {}).name;
  }

  // Support subscription profiles with raw proxies/providers but no groups.
  if (!target) {
    const nodeNames = (Array.isArray(config.proxies) ? config.proxies : [])
      .filter(p => p && typeof p.name === "string" && p.name)
      .map(p => p.name);
    const providerNames = Object.keys(config["proxy-providers"] || {});
    if (!nodeNames.length && !providerNames.length) {
      throw new Error("USR: 请先导入带有节点的 Mihomo 订阅");
    }
    target = "USR-PROXY";
    config["proxy-groups"] = groups.concat([{
      name: target, type: "select",
      ...(nodeNames.length ? {proxies: nodeNames} : {}),
      ...(providerNames.length ? {use: providerNames} : {})
    }]);
  }

  config["rule-providers"] = config["rule-providers"] || {};
  config["rule-providers"]["usr-china-classical"] = {
    type: "http", behavior: "classical", format: "yaml",
    url: USR_RULES.url,
    path: "./ruleset/usr-china-classical.yaml", interval: 86400
  };

  const proxyRules = USR_RULES.proxy.map(r => r.replace("{POLICY}", target));
  // Replace existing subscription routing (including its ad-blocking rules).
  config.rules = [
    ...USR_RULES.private,
    ...proxyRules,
    ...USR_RULES.direct,
    ...USR_RULES.end,
    `MATCH,${target}`
  ];
  config.mode = "rule";
  return config;
}
'''


def flclash_script(cfg):
    parts = {
        'proxy': [f'DOMAIN-SUFFIX,{d},{{POLICY}}' for d in cfg['proxy_domain_suffixes']],
        'direct': [f'DOMAIN-SUFFIX,{d},DIRECT' for d in cfg['direct_domain_suffixes']],
        'private': ([f'IP-CIDR,{n},DIRECT,no-resolve' for n in cfg['private_ipv4_cidrs']] +
                    [f'IP-CIDR6,{n},DIRECT,no-resolve' for n in cfg['private_ipv6_cidrs']]),
        'end': ['RULE-SET,usr-china-classical,DIRECT'] +
               (['DOMAIN-SUFFIX,cn,DIRECT'] if cfg['routing']['china_tld_direct'] else []) +
               (['GEOIP,CN,DIRECT'] if cfg['routing']['china_ip_direct'] else []),
        'url': cfg['upstream']['mihomo_china_classical'],
    }
    return JS_TEMPLATE.replace('__USR_DATA__', json.dumps(parts, ensure_ascii=False, indent=2))


def android_template(cfg, mihomo_function):
    content = mihomo_function(cfg)
    content = content.replace(
        '# Use Your VPN around the clock | GENERATED FILE - DO NOT EDIT',
        '# Use Your VPN around the clock for Android / FlClash | GENERATED FILE - DO NOT EDIT', 1)
    return content.replace(
        '# Replace YOUR_PRIVATE_SUBSCRIPTION_URL with your own Mihomo-compatible provider URL.',
        '# Beginners: use flclash-override.js instead; it does not need a private URL.\n'
        '# Replace YOUR_PRIVATE_SUBSCRIPTION_URL with your own Mihomo-compatible provider URL.', 1)


def clash_verge_script(cfg):
    """Use the shared routing engine through Clash Verge Rev's main(config) API."""
    content = flclash_script(cfg)
    start = content.index('const USR_RULES =')
    content = content[start:]
    content = content.replace('  let target = preferred.find(n => names.includes(n));',
        '  if (USR_PROXY_GROUP && !names.includes(USR_PROXY_GROUP)) {\n'
        '    throw new Error("USR: 指定的代理组不存在: " + USR_PROXY_GROUP);\n'
        '  }\n'
        '  let target = USR_PROXY_GROUP || preferred.find(n => names.includes(n));')
    # Clash Verge Rev owns mode; the user selects Rule mode in its UI.
    content = content.replace('  config.mode = "rule";\n', '')
    return ('// Use Your VPN around the clock - Clash Verge Rev (Windows / macOS)\n'
            '// GENERATED FILE. Source: config/routing.json.\n'
            '// Paste into the subscription extension script; see docs/DESKTOP.md.\n'
            '// Replaces original rules; preserves nodes, groups, DNS and TUN settings.\n'
            '// Select Rule mode in the app. Optional: set an exact proxy group below.\n'
            'const USR_PROXY_GROUP = "";\n\n' + content)
