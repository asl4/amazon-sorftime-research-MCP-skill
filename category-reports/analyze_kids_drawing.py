#!/usr/bin/env python3
"""分析 Kids' Drawing Kits 品类数据"""

import sys
sys.path.append('.claude/skills/category-selection/scripts')

from sorftime_parser import parse_sorftime_sse, extract_top_products, calculate_metrics, calculate_five_dimension_scores
import json
from datetime import datetime

# 读取原始响应
with open('category-reports/kids-drawing-kits-raw.json', 'r', encoding='utf-8') as f:
    raw_response = f.read()

# 解析数据
data = parse_sorftime_sse(raw_response)

if not data:
    print("解析失败")
    sys.exit(1)

# 提取统计信息
print("=== 数据结构 ===")
print(f"键列表: {list(data.keys())[:30]}")

# 查找统计数据键
stats_keys = [k for k in data.keys() if not k.startswith('Top') and not k.startswith('top')]
print(f"\n统计键: {stats_keys}")

# 提取 Top20 产品
products = extract_top_products(data, limit=20)

# 计算指标
metrics = calculate_metrics(products)

# 计算五维评分
scores = calculate_five_dimension_scores(metrics)

# 保存产品数据
with open('category-reports/kids-drawing-kits-products.json', 'w', encoding='utf-8') as f:
    json.dump({
        'products': products,
        'metrics': metrics,
        'scores': scores,
        'raw_stats': {k: v for k, v in data.items() if k not in ['Top100产品', 'Top100äº§å']}
    }, f, ensure_ascii=False, indent=2)

print("\n=== 分析结果 ===")
print(f"总销额: ${metrics['total_revenue']:,.2f}")
print(f"总销量: {metrics['total_sales']:,}")
print(f"平均价格: ${metrics['avg_price']:.2f}")
print(f"Top3品牌占比: {metrics['top3_share']:.1f}%")
print(f"Amazon自营占比: {metrics['amazon_share']:.1f}%")
print(f"低评价新品占比: {metrics['low_review_share']:.1f}%")
print(f"\n五维评分: {scores['total']}/100")
print(f"  - 市场规模: {scores['market_size']}/20")
print(f"  - 增长潜力: {scores['growth']}/25")
print(f"  - 竞争烈度: {scores['competition']}/20")
print(f"  - 进入壁垒: {scores['barriers']}/20")
print(f"  - 利润空间: {scores['profit']}/15")

print("\n=== Top5 品牌 ===")
for brand, revenue in metrics['top_brands']:
    print(f"  {brand}: ${revenue:,.2f}")
