// Use Your VPN around the clock - FlClash override script (GENERATED)
// Paste this in FlClash > Tools > Advanced settings > Override scripts.
// Select the script for YOUR subscription in Profiles > More > Override > Script.
// Keeps the subscription's nodes and proxy groups; REPLACES its original rules.
// No personal URL or credentials are included here.

// Optional exact group name. Leave empty only when there is one eligible group.
const USR_PROXY_GROUP = "";
const USR_RULES = {
  "proxy": [
    "DOMAIN-SUFFIX,openai.com,{POLICY}",
    "DOMAIN-SUFFIX,chatgpt.com,{POLICY}",
    "DOMAIN-SUFFIX,oaistatic.com,{POLICY}",
    "DOMAIN-SUFFIX,oaiusercontent.com,{POLICY}",
    "DOMAIN-SUFFIX,google.com,{POLICY}",
    "DOMAIN-SUFFIX,googleapis.com,{POLICY}",
    "DOMAIN-SUFFIX,gstatic.com,{POLICY}",
    "DOMAIN-SUFFIX,youtube.com,{POLICY}",
    "DOMAIN-SUFFIX,googlevideo.com,{POLICY}",
    "DOMAIN-SUFFIX,ytimg.com,{POLICY}",
    "DOMAIN-SUFFIX,instagram.com,{POLICY}",
    "DOMAIN-SUFFIX,facebook.com,{POLICY}",
    "DOMAIN-SUFFIX,fbcdn.net,{POLICY}",
    "DOMAIN-SUFFIX,x.com,{POLICY}",
    "DOMAIN-SUFFIX,twitter.com,{POLICY}",
    "DOMAIN-SUFFIX,twimg.com,{POLICY}",
    "DOMAIN-SUFFIX,t.co,{POLICY}",
    "DOMAIN-SUFFIX,github.com,{POLICY}",
    "DOMAIN-SUFFIX,githubusercontent.com,{POLICY}",
    "DOMAIN-SUFFIX,githubassets.com,{POLICY}",
    "DOMAIN-SUFFIX,spotify.com,{POLICY}",
    "DOMAIN-SUFFIX,scdn.co,{POLICY}",
    "DOMAIN-SUFFIX,discord.com,{POLICY}",
    "DOMAIN-SUFFIX,discord.gg,{POLICY}",
    "DOMAIN-SUFFIX,discordapp.com,{POLICY}",
    "DOMAIN-SUFFIX,telegram.org,{POLICY}",
    "DOMAIN-SUFFIX,t.me,{POLICY}"
  ],
  "direct": [
    "DOMAIN-SUFFIX,qq.com,DIRECT",
    "DOMAIN-SUFFIX,weixin.com,DIRECT",
    "DOMAIN-SUFFIX,wechat.com,DIRECT",
    "DOMAIN-SUFFIX,tenpay.com,DIRECT",
    "DOMAIN-SUFFIX,alipay.com,DIRECT",
    "DOMAIN-SUFFIX,alipayobjects.com,DIRECT",
    "DOMAIN-SUFFIX,taobao.com,DIRECT",
    "DOMAIN-SUFFIX,tmall.com,DIRECT",
    "DOMAIN-SUFFIX,alicdn.com,DIRECT",
    "DOMAIN-SUFFIX,bilibili.com,DIRECT",
    "DOMAIN-SUFFIX,bilivideo.com,DIRECT",
    "DOMAIN-SUFFIX,biliapi.com,DIRECT",
    "DOMAIN-SUFFIX,hdslb.com,DIRECT",
    "DOMAIN-SUFFIX,douyin.com,DIRECT",
    "DOMAIN-SUFFIX,douyincdn.com,DIRECT",
    "DOMAIN-SUFFIX,bytedance.com,DIRECT",
    "DOMAIN-SUFFIX,xiaohongshu.com,DIRECT",
    "DOMAIN-SUFFIX,xhscdn.com,DIRECT",
    "DOMAIN-SUFFIX,jd.com,DIRECT",
    "DOMAIN-SUFFIX,360buyimg.com,DIRECT",
    "DOMAIN-SUFFIX,meituan.com,DIRECT",
    "DOMAIN-SUFFIX,meituan.net,DIRECT",
    "DOMAIN-SUFFIX,dianping.com,DIRECT",
    "DOMAIN-SUFFIX,12306.cn,DIRECT",
    "DOMAIN-SUFFIX,zhihu.com,DIRECT",
    "DOMAIN-SUFFIX,zhimg.com,DIRECT",
    "DOMAIN-SUFFIX,baidu.com,DIRECT",
    "DOMAIN-SUFFIX,bdstatic.com,DIRECT",
    "DOMAIN-SUFFIX,netease.com,DIRECT",
    "DOMAIN-SUFFIX,163.com,DIRECT",
    "DOMAIN-SUFFIX,126.com,DIRECT",
    "DOMAIN-SUFFIX,youku.com,DIRECT",
    "DOMAIN-SUFFIX,iqiyi.com,DIRECT"
  ],
  "private": [
    "IP-CIDR,127.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,10.0.0.0/8,DIRECT,no-resolve",
    "IP-CIDR,172.16.0.0/12,DIRECT,no-resolve",
    "IP-CIDR,192.168.0.0/16,DIRECT,no-resolve",
    "IP-CIDR,169.254.0.0/16,DIRECT,no-resolve",
    "IP-CIDR6,::1/128,DIRECT,no-resolve",
    "IP-CIDR6,fc00::/7,DIRECT,no-resolve",
    "IP-CIDR6,fe80::/10,DIRECT,no-resolve"
  ],
  "end": [
    "RULE-SET,usr-china-classical,DIRECT",
    "DOMAIN-SUFFIX,cn,DIRECT",
    "GEOIP,CN,DIRECT"
  ],
  "url": "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/China/China_Classical.yaml"
};

const USR_BUILTINS = ["DIRECT", "REJECT", "REJECT-DROP", "PASS", "COMPATIBLE", "GLOBAL"];
function usrName(name) {
  return typeof name === "string" && name.trim() && !/[,\r\n]/.test(name) &&
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
  const excluded = /广告|拦截|屏蔽|拒绝|直连|阻断|\b(?:ad[-_ ]?block|ads?|reject|block|direct|bypass)\b/i;
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
