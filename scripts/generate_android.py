"""Generate Android and desktop overrides using one shared selection engine."""
import json


JS_TEMPLATE = '''// Use Your VPN around the clock - FlClash override script (GENERATED)
// Paste this in FlClash > Tools > Advanced settings > Override scripts.
// Select the script for YOUR subscription in Profiles > More > Override > Script.
// Keeps the subscription's nodes and proxy groups; REPLACES its original rules.
// No personal URL or credentials are included here.

// Optional exact group name. Leave empty only when there is one eligible group.
const USR_PROXY_GROUP = "";
const USR_RULES = __USR_DATA__;

const USR_BUILTINS = ["DIRECT", "REJECT", "REJECT-DROP", "PASS", "COMPATIBLE", "GLOBAL"];
function usrName(name) {
  return typeof name === "string" && name.trim() && !/[,\\r\\n]/.test(name) &&
    !USR_BUILTINS.includes(name.toUpperCase());
}
function usrNode(node) {
  return node && usrName(node.name) && typeof node.type === "string" &&
    !["direct", "reject", "reject-drop", "pass", "dns"].includes(node.type.toLowerCase());
}
function usrSelect(config) {
  if (config["proxy-groups"] !== undefined && !Array.isArray(config["proxy-groups"])) {
    throw new Error("USR: proxy-groups 必须是列表");
  }
  const groups = config["proxy-groups"] || [];
  const nodes = (Array.isArray(config.proxies) ? config.proxies : []).filter(usrNode);
  const providers = config["proxy-providers"] || {};
  const providerNames = Object.keys(providers).filter(n => providers[n] &&
    (["http", "file"].includes(providers[n].type) ||
     (providers[n].type === "inline" && Array.isArray(providers[n].payload) &&
      providers[n].payload.some(usrNode))));
  const nodeNames = nodes.map(n => n.name);
  const byName = new Map();
  for (const g of groups) {
    if (!g || !usrName(g.name) || byName.has(g.name) || nodeNames.includes(g.name)) {
      throw new Error("USR: 策略组名称无效或重复，请修复订阅");
    }
    byName.set(g.name, g);
  }
  const excluded = /广告|拦截|屏蔽|拒绝|直连|阻断|\\b(?:ad[-_ ]?block|ads?|reject|block|direct|bypass)\\b/i;
  function eligible(g, visiting = new Set()) {
    if (!g || excluded.test(g.name) || visiting.has(g.name) ||
        !["select", "url-test", "fallback", "load-balance"].includes(g.type)) return false;
    const next = new Set(visiting); next.add(g.name);
    // Provider contents and Mihomo regex filters cannot be resolved here.
    // Treat them as potential exits; the user must verify loaded nodes in the app.
    if ((g["include-all"] || g["include-all-providers"]) && providerNames.length) return true;
    if ((g["include-all"] || g["include-all-proxies"]) && nodeNames.length) return true;
    if (Array.isArray(g.use) && g.use.some(n => providerNames.includes(n))) return true;
    return Array.isArray(g.proxies) && g.proxies.some(n =>
      nodeNames.includes(n) || eligible(byName.get(n), next));
  }
  function filtered(g, visiting = new Set()) {
    if (!g || visiting.has(g.name)) return false;
    const hasFilter = x => x && ["filter", "exclude-filter", "exclude-type"].some(k => x[k]);
    const next = new Set(visiting); next.add(g.name);
    if (hasFilter(g)) return true;
    const used = (g["include-all"] || g["include-all-providers"]) ? providerNames :
      (Array.isArray(g.use) ? g.use : []);
    return used.some(n => hasFilter(providers[n])) ||
      (Array.isArray(g.proxies) && g.proxies.some(n => filtered(byName.get(n), next)));
  }
  if (USR_PROXY_GROUP) {
    if (!byName.has(USR_PROXY_GROUP)) throw new Error("USR: 指定的代理组不存在，请检查 USR_PROXY_GROUP");
    if (!eligible(byName.get(USR_PROXY_GROUP))) {
      throw new Error("USR: 指定组没有可确认的代理出口或属于排除组，请检查 USR_PROXY_GROUP");
    }
    return {target: USR_PROXY_GROUP};
  }
  if (groups.length) {
    const candidates = groups.filter(g => eligible(g));
    if (candidates.length !== 1) {
      throw new Error("USR: " + (candidates.length ? "存在多个候选代理组: " + candidates.map(g => g.name).join(" / ") :
        "没有可确认的代理出口") + "；请检查订阅，并手动设置 USR_PROXY_GROUP");
    }
    if (filtered(candidates[0])) {
      throw new Error("USR: 候选组含节点过滤器，无法确认过滤后的出口；请核对节点并手动设置 USR_PROXY_GROUP");
    }
    return {target: candidates[0].name};
  }
  if (!nodeNames.length && !providerNames.length) throw new Error("USR: 请先导入带有节点的 Mihomo 订阅");
  let target = "USR-PROXY";
  for (let i = 2; nodeNames.includes(target); i++) target = "USR-PROXY-" + i;
  return {target, group: {
    name: target, type: "select",
    ...(nodeNames.length ? {proxies: nodeNames} : {}),
    ...(providerNames.length ? {use: providerNames} : {})
  }};
}

function main(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("USR: Invalid subscription profile");
  }
  const selection = usrSelect(config);
  const target = selection.target;
  // No mutation until proxy selection has succeeded.
  if (selection.group) config["proxy-groups"] = [selection.group];

  config["rule-providers"] = config["rule-providers"] || {};
  config["rule-providers"]["usr-china-classical"] = {
    type: "http", behavior: "classical", format: "yaml",
    url: USR_RULES.url,
    path: "./ruleset/usr-china-classical.yaml", interval: 86400
  };

  const proxyRules = USR_RULES.proxy.map(r => r.replace("{POLICY}", () => target));
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
    start = content.index('// Optional exact group name.')
    content = content[start:]
    # Clash Verge Rev owns mode; the user selects Rule mode in its UI.
    content = content.replace('  config.mode = "rule";\n', '')
    return ('// Use Your VPN around the clock - Clash Verge Rev (Windows / macOS)\n'
            '// GENERATED FILE. Source: config/routing.json.\n'
            '// Paste into the subscription extension script; see docs/DESKTOP.md.\n'
            '// Replaces original rules; preserves nodes, groups, DNS and TUN settings.\n'
            '// Select Rule mode in the app. Optional: set an exact proxy group below.\n'
            + content)
