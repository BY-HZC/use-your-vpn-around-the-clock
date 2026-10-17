// Use Your VPN around the clock - Clash Verge Rev (Windows / macOS)
// GENERATED FILE. Source: config/routing.json.
// Paste into the subscription extension script; see docs/DESKTOP.md.
// Replaces original rules; preserves nodes, groups, DNS and TUN settings.
// Select Rule mode in the app. Optional: set an exact proxy group below.
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
    "DOMAIN-SUFFIX,weixin.qq.com,DIRECT",
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

function main(config) {
  if (!config || typeof config !== "object") {
    throw new Error("USR: Invalid subscription profile");
  }
  const groups = Array.isArray(config["proxy-groups"]) ? config["proxy-groups"] : [];
  const usable = groups.filter(g => g && typeof g.name === "string" && g.name &&
    !["DIRECT", "REJECT", "PASS", "GLOBAL"].includes(g.name));
  const names = usable.map(g => g.name);
  const preferred = ["PROXY", "Proxy", "proxy", "🚀 节点选择", "节点选择", "选择节点", "代理", "🚀 Proxy", "节点切换", "♻️ 自动选择"];
  if (USR_PROXY_GROUP && !names.includes(USR_PROXY_GROUP)) {
    throw new Error("USR: 指定的代理组不存在: " + USR_PROXY_GROUP);
  }
  let target = USR_PROXY_GROUP || preferred.find(n => names.includes(n));
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
  return config;
}
