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
PAGE_SIZE = 100



def fetch_all_pages():
    """
    分页请求API，汇总所有代理
    """
    all_items = []
    page_index = 1
    page_size = 100
    total_pages = 1  # 默认至少请求1页

    while page_index <= total_pages:
        params = {
            "country": "",
            "protocol": "socks5,http",
            "anonymity": "",
            "speed": "0,5",
            "https": "0",
            "page_index": page_index,
            "page_size": page_size
        }
        try:
            prepared = requests.Request('GET', API_URL, params=params).prepare()
            # print(f"请求URL: {prepared.url}")
            resp = requests.get(API_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            # print(f"响应JSON: {data}")
        except Exception as e:
            print(f"请求第{page_index}页失败: {e}")
            break

        if page_index == 1:
            total_count = data.get("data", {}).get("total_count", 0)
            total_pages = (total_count + page_size - 1) // page_size if total_count else 1
            print(f"总代理数: {total_count}, 总页数: {total_pages}")

        page_items = data.get("data", {}).get("data", [])
        all_items.extend(page_items)

        print(f"已获取第{page_index}页，累计代理数: {len(all_items)}")

        page_index += 1
        if page_index <= total_pages:
            print("等待20秒后请求下一页...")
            time.sleep(10)

    # 统一筛选有效 socks5/http 代理
    valid_proxies = []
    for p in all_items:
        proto = p.get("protocol") if isinstance(p, dict) else None
        # print(f"[调试] 当前代理 protocol 字段: {proto}")
        if isinstance(p, dict) and proto in ("socks5", "http"):
            valid_proxies.append(p)
    print(f"有效代理总数: {len(valid_proxies)}")
    return valid_proxies

def generate_all_proxies():
    """
    请求一次API，筛选有效代理，按国家分组生成节点
    """
    proxies = fetch_all_pages()
    all_nodes = []
    country_nodes_map = {}

    country_proxy_dict = {}
    for p in proxies:
        country = p.get("country", "ZZ").upper() or "ZZ"
        proto = p.get("protocol")
        if country not in country_proxy_dict:
            country_proxy_dict[country] = []
        country_proxy_dict[country].append(p)

    for country_code, proxy_list in country_proxy_dict.items():
        nodes = []
        for idx, p in enumerate(proxy_list, 1):
            proto = p.get("protocol")
            name = f"{country_code}-{proto}-{idx}"
            node_type = proto
            node = {
                "name": name,
                "type": node_type,
                "server": p.get("ip") or p.get("host") or "",
                "port": int(p.get("port", 0)),
                "udp": True
            }
            nodes.append(node)
            all_nodes.append(node)
        country_nodes_map[country_code] = [n["name"] for n in nodes]

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