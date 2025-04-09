import requests
import yaml
import time
import json
import os
from datetime import datetime, timedelta
import sys

API_URL = os.environ.get("PROXY_API_URL")
if not API_URL:
    print("错误：未设置环境变量 PROXY_API_URL")
    sys.exit(1)
UUID = "9f1b0c2e-3d4a-4b5c-8f6e-123456789abc"  # 固定UUID，可替换
PAGE_SIZE = 20
SKIP_FILE = "skip_countries.json"

# 内置国家代码列表，方便扩展
COUNTRY_CODES = [
    "AF", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO", "BN", "BG", "BF", "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR", "CU", "CW", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ", "ER", "EE", "SZ", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "VA", "HN", "HK", "HU", "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP", "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MG", "MW", "MY", "MV", "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MK", "MP", "NO", "OM", "PK", "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RE", "RO", "RU", "RW", "BL", "SH", "KN", "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI", "SB", "SO", "ZA", "GS", "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US", "UM", "UY", "UZ", "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW"
]

def load_skip_list():
    if not os.path.exists(SKIP_FILE):
        return {}
    try:
        with open(SKIP_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_skip_list(skip_list):
    with open(SKIP_FILE, "w", encoding="utf-8") as f:
        json.dump(skip_list, f, ensure_ascii=False, indent=2)

def should_skip_country(skip_list, country_code):
    info = skip_list.get(country_code)
    if not info:
        return False
    deadline_str = info.get("until")
    if not deadline_str:
        return False
    try:
        deadline = datetime.fromisoformat(deadline_str)
    except Exception:
        return False
    return datetime.now() < deadline

def update_skip_list(skip_list, country_code, total_count):
    if total_count == 0:
        # 加入或更新跳过名单，截止时间为3天后
        skip_list[country_code] = {
            "until": (datetime.now() + timedelta(days=3)).isoformat()
        }
    else:
        # 有结果，移除跳过记录
        if country_code in skip_list:
            del skip_list[country_code]

def fetch_country_proxies(country_code):
    """
    获取指定国家的代理列表，只请求一页
    """
    params = {
        "country": country_code,
        "protocol": "socks5,http",
        "anonymity": "elite,anonymous",
        "page_size": PAGE_SIZE,
        "page": 1
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[{country_code}] 请求失败: {e}")
        return [], None

    total_count = data.get("total_count", None)
    items = data.get("results") or data.get("data") or []
    valid_proxies = [
        p for p in items
        if str(p.get("is_valid")) == "1" and p.get("protocol") in ("socks5", "http")
    ]
    print(f"[{country_code}] 获取有效代理数: {len(valid_proxies)}")
    return valid_proxies, total_count

def generate_all_proxies():
    """
    针对所有国家代码，获取代理，生成节点
    """
    all_nodes = []
    country_nodes_map = {}

    skip_list = load_skip_list()

    for code in COUNTRY_CODES:
        if should_skip_country(skip_list, code):
            print(f"[{code}] 在跳过名单中，跳过请求")
            continue

        proxies, total_count = fetch_country_proxies(code)

        # total_count为None时不更新跳过名单
        if total_count is not None:
            update_skip_list(skip_list, code, total_count)

        nodes = []
        for idx, p in enumerate(proxies, 1):
            proto = p.get("protocol")
            name = f"{code}-{proto}-{idx}"
            node_type = proto  # 'socks5' 或 'http'
            node = {
                "name": name,
                "type": node_type,
                "server": p.get("ip") or p.get("host") or "",
                "port": int(p.get("port", 0)),
                "udp": True
            }
            nodes.append(node)
            all_nodes.append(node)
        country_nodes_map[code] = [n["name"] for n in nodes]
        time.sleep(1)  # 避免请求过快

    save_skip_list(skip_list)

    return all_nodes, country_nodes_map

def build_clash_config(all_nodes, country_nodes_map):
    """
    构建Clash配置字典
    """
    proxy_groups = []

    # 每个国家一个分组
    for code, node_names in country_nodes_map.items():
        if not node_names:
            continue
        proxy_groups.append({
            "name": code,
            "type": "select",
            "proxies": node_names
        })

    # 总分组，包含所有国家分组名
    all_country_group = {
        "name": "All-Countries",
        "type": "select",
        "proxies": [code for code in country_nodes_map if country_nodes_map[code]]
    }
    proxy_groups.append(all_country_group)

    rules = [
        "MATCH,All-Countries"
    ]

    clash_config = {
        "proxies": all_nodes,
        "proxy-groups": proxy_groups,
        "rules": rules
    }

    return clash_config

def main():
    all_nodes, country_nodes_map = generate_all_proxies()
    clash_config = build_clash_config(all_nodes, country_nodes_map)

    yaml_content = yaml.dump(clash_config, allow_unicode=True, sort_keys=False)

    with open("sub.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print("Clash订阅已写入 sub.yaml")

if __name__ == "__main__":
    main()