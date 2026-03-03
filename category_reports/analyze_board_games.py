import json
import codecs
import re
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# API Key
API_KEY = "wgj4a1b5ukd6m1djz3g1uzvtogc3ut09"

def call_sorftime(tool_name, arguments):
    """Call Sorftime MCP API"""
    import subprocess
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    cmd = f'''curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{json.dumps(payload)}\' '''

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return result.stdout

def parse_sorftime_response(response_text):
    """Parse Sorftime SSE response"""
    for line in response_text.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]
            try:
                data = json.loads(json_text)
                if 'result' in data and 'content' in data['result']:
                    result_text = data['result']['content'][0]['text']
                    # Decode unicode escape
                    result_text = codecs.decode(result_text, 'unicode-escape')

                    # Extract JSON
                    start = result_text.find('{')
                    if start != -1:
                        # Find matching closing brace
                        depth = 0
                        end = -1
                        for i in range(start, len(result_text)):
                            if result_text[i] == '{':
                                depth += 1
                            elif result_text[i] == '}':
                                depth -= 1
                                if depth == 0:
                                    end = i + 1
                                    break

                        if end != -1:
                            json_str = result_text[start:end]
                            json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                            return json.loads(json_str)
            except:
                continue
    return None

def read_existing_category_data():
    """Read the previously saved category data"""
    file_path = 'C:/Users/49707/.claude/projects/D--amazon-mcp/4700d6ba-1f24-46ad-a7eb-86635bb4d208/tool-results/bjfkes1xv.txt'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = parse_sorftime_response(content)
    if data:
        # Save to JSON file
        output_dir = 'D:/amazon-mcp/category_reports'
        os.makedirs(output_dir, exist_ok=True)
        with open(f'{output_dir}/board_games_raw.json', 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        print(f"Saved raw data to {output_dir}/board_games_raw.json")
        return data
    return None

def get_product_details(asin):
    """Get product details for a single ASIN"""
    try:
        response = call_sorftime('product_detail', {'amzSite': 'US', 'asin': asin})
        return parse_sorftime_response(response)
    except Exception as e:
        print(f"Error fetching details for {asin}: {e}")
        return None

def calculate_five_dimension_score(stats, products):
    """Calculate five-dimensional score based on category statistics"""
    scores = {
        "market_size": 0,      # 20分
        "growth": 0,           # 25分
        "competition": 0,      # 20分
        "barriers": 0,         # 20分
        "profit": 0            # 15分
    }

    # Extract statistics
    # Calculate from products if not directly available
    total_revenue = sum(float(p.get('月销额', 0) or 0) for p in products)
    total_sales = sum(int(p.get('月销量', 0) or 0) for p in products)
    avg_price = total_revenue / total_sales if total_sales > 0 else 0

    # Count brands
    brands = {}
    for p in products:
        brand = p.get('品牌', 'Unknown')
        brands[brand] = brands.get(brand, 0) + float(p.get('月销额', 0) or 0)

    # Sort brands by revenue
    sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)
    top3_revenue = sum(v for k, v in sorted_brands[:3])
    top3_share = (top3_revenue / total_revenue * 100) if total_revenue > 0 else 0

    # Count Amazon products
    amazon_count = sum(1 for p in products if p.get('卖家', '') == 'Amazon')
    amazon_share = (amazon_count / len(products) * 100) if products else 0

    # Count low review products (less than 100 reviews)
    low_review_count = sum(1 for p in products if int(p.get('评论数', 0) or 0) < 100)
    low_review_share = (low_review_count / len(products) * 100) if products else 0

    # 1. Market Size (20 points)
    if total_revenue > 10000000:
        scores["market_size"] = 20
    elif total_revenue > 5000000:
        scores["market_size"] = 17
    elif total_revenue > 1000000:
        scores["market_size"] = 14
    else:
        scores["market_size"] = 10

    # 2. Growth Potential (25 points) - based on low review product share
    if low_review_share > 40:
        scores["growth"] = 22
    elif low_review_share > 20:
        scores["growth"] = 18
    else:
        scores["growth"] = 14

    # 3. Competition Intensity (20 points) - reverse of concentration
    if top3_share < 30:
        scores["competition"] = 18  # Low concentration = good
    elif top3_share < 50:
        scores["competition"] = 14  # Medium concentration
    else:
        scores["competition"] = 8   # High concentration = bad

    # 4. Entry Barriers (20 points)
    # Amazon share (lower is better)
    if amazon_share < 20:
        scores["barriers"] += 10
    elif amazon_share < 40:
        scores["barriers"] += 6
    else:
        scores["barriers"] += 3

    # New product opportunity (low review share is good)
    if low_review_share > 40:
        scores["barriers"] += 10
    elif low_review_share > 20:
        scores["barriers"] += 6
    else:
        scores["barriers"] += 3

    # 5. Profit Space (15 points)
    if avg_price > 30:
        scores["profit"] = 12
    elif avg_price > 15:
        scores["profit"] = 10
    else:
        scores["profit"] = 7

    scores["total"] = sum(scores.values())

    return scores, {
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "avg_price": avg_price,
        "top3_share": top3_share,
        "amazon_share": amazon_share,
        "low_review_share": low_review_share,
        "top_brands": sorted_brands[:5]
    }

def generate_markdown_report(stats, products, scores, metrics):
    """Generate markdown analysis report"""
    output_dir = 'D:/amazon-mcp/category_reports'
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{output_dir}/board_games_analysis_{timestamp}.md'

    # Determine rating
    total_score = scores["total"]
    if total_score >= 85:
        rating = "优秀"
        emoji = "🟢"
    elif total_score >= 70:
        rating = "良好"
        emoji = "🟡"
    elif total_score >= 55:
        rating = "一般"
        emoji = "🟠"
    else:
        rating = "较差"
        emoji = "🔴"

    md_content = f"""# Board Games 品类选品分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析站点**: Amazon US
**类目ID**: 166225011

---

## 执行摘要

| 指标 | 结果 |
|------|------|
| **综合评级** | {emoji} **{rating}** |
| **总分** | {total_score}/100 |
| **市场规模** | {scores['market_size']}/20 |
| **增长潜力** | {scores['growth']}/25 |
| **竞争烈度** | {scores['competition']}/20 |
| **进入壁垒** | {scores['barriers']}/20 |
| **利润空间** | {scores['profit']}/15 |

### 核心建议
"""

    # Add strategic recommendations based on scores
    if total_score >= 85:
        md_content += "- ✅ **强烈推荐进入**: 该品类市场空间大，竞争相对温和，适合新卖家入场\n"
    elif total_score >= 70:
        md_content += "- ✅ **推荐进入**: 该品类整体表现良好，建议选择细分差异化产品\n"
    elif total_score >= 55:
        md_content += "- ⚠️ **谨慎进入**: 该品类竞争激烈或利润空间有限，建议做好充分调研\n"
    else:
        md_content += "- ❌ **不建议进入**: 该品类存在较高的进入壁垒或市场饱和\n"

    md_content += f"""

---

## 一、市场概况

### 整体数据

| 指标 | 数值 |
|------|------|
| Top100月销总额 | ${metrics['total_revenue']:,.2f} |
| Top100月销总量 | {metrics['total_sales']:,} |
| 平均价格 | ${metrics['avg_price']:.2f} |
| Top3品牌集中度 | {metrics['top3_share']:.1f}% |
| Amazon自营占比 | {metrics['amazon_share']:.1f}% |
| 新品机会占比(评论<100) | {metrics['low_review_share']:.1f}% |

### 市场规模分析
"""

    if metrics['total_revenue'] > 10000000:
        md_content += f"- **市场规模**: 超大型市场 (月销额 ${metrics['total_revenue']/1000000:.1f}M)\n"
    elif metrics['total_revenue'] > 5000000:
        md_content += f"- **市场规模**: 大型市场 (月销额 ${metrics['total_revenue']/1000000:.1f}M)\n"
    else:
        md_content += f"- **市场规模**: 中型市场 (月销额 ${metrics['total_revenue']/1000000:.1f}M)\n"

    md_content += f"""

---

## 二、竞争格局

### 品牌集中度分析
"""

    for i, (brand, revenue) in enumerate(metrics['top_brands'], 1):
        share = (revenue / metrics['total_revenue'] * 100) if metrics['total_revenue'] > 0 else 0
        md_content += f"{i}. **{brand}**: ${revenue:,.2f} (占{share:.1f}%)\n"

    md_content += f"""

### 竞争强度评估
"""

    if metrics['top3_share'] < 30:
        md_content += "- **竞争状态**: 🟢 低度集中 - 市场较为分散，新品牌有机会\n"
    elif metrics['top3_share'] < 50:
        md_content += "- **竞争状态**: 🟡 中度集中 - 头部品牌有一定优势，但仍有空间\n"
    else:
        md_content += "- **竞争状态**: 🔴 高度集中 - 头部品牌垄断，新进入者困难\n"

    md_content += f"""

### Amazon自营影响
"""

    if metrics['amazon_share'] < 20:
        md_content += f"- **自营挤压**: 🟢 低 ({metrics['amazon_share']:.1f}%) - Amazon自营产品少，第三方卖家机会多\n"
    elif metrics['amazon_share'] < 40:
        md_content += f"- **自营挤压**: 🟡 中等 ({metrics['amazon_share']:.1f}%) - 部分品类有自营竞争\n"
    else:
        md_content += f"- **自营挤压**: 🔴 高 ({metrics['amazon_share']:.1f}%) - Amazon自营产品较多，竞争激烈\n"

    md_content += f"""

---

## 三、Top20产品分析

| 排名 | ASIN | 产品名称 | 价格 | 月销量 | 月销额 | 评分 | 评论数 | 品牌 |
|------|------|----------|------|--------|--------|------|--------|------|
"""

    for i, p in enumerate(products[:20], 1):
        title = p.get('标题', 'N/A')[:40] + '...' if len(p.get('标题', '')) > 40 else p.get('标题', 'N/A')
        price = p.get('价格', 0)
        sales = p.get('月销量', 0)
        revenue = p.get('月销额', 0)
        rating = p.get('星级', 0)
        reviews = p.get('评论数', 0)
        brand = p.get('品牌', 'N/A')

        md_content += f"| {i} | {p.get('ASIN', 'N/A')} | {title} | ${price} | {sales:,} | ${revenue:,.0f} | {rating} | {reviews:,} | {brand} |\n"

    md_content += f"""

---

## 四、五维评分详情

### 1. 市场规模 (20分)
**得分**: {scores['market_size']}/20

"""
    if metrics['total_revenue'] > 10000000:
        md_content += "- 该品类月销额超过$10M，属于**超大型市场**\n"
        md_content += "- 市场容量巨大，可容纳多个卖家\n"
    elif metrics['total_revenue'] > 5000000:
        md_content += "- 该品类月销额超过$5M，属于**大型市场**\n"
        md_content += "- 市场容量充足，具有发展潜力\n"
    else:
        md_content += "- 该品类月销额低于$5M，属于**中型市场**\n"
        md_content += "- 市场容量适中，需要精准定位\n"

    md_content += f"""

### 2. 增长潜力 (25分)
**得分**: {scores['growth']}/25

- **新品机会**: 评论数<100的产品占比 {metrics['low_review_share']:.1f}%
"""

    if metrics['low_review_share'] > 40:
        md_content += "- 新品空间充足，说明市场接受新产品的意愿较强\n"
        md_content += "- 适合有创新能力的新卖家进入\n"
    elif metrics['low_review_share'] > 20:
        md_content += "- 新品有一定空间，但需要差异化定位\n"
    else:
        md_content += "- 新品空间有限，市场被老产品占据\n"

    md_content += f"""

### 3. 竞争烈度 (20分)
**得分**: {scores['competition']}/20

- **品牌集中度**: Top3品牌占比 {metrics['top3_share']:.1f}%
"""

    if metrics['top3_share'] < 30:
        md_content += "- 市场分散，头部品牌优势不明显\n"
        md_content += "- 新品牌有机会切入并获取市场份额\n"
    elif metrics['top3_share'] < 50:
        md_content += "- 头部品牌有一定优势\n"
        md_content += "- 建议选择细分差异化赛道\n"
    else:
        md_content += "- 头部品牌垄断明显\n"
        md_content += "- 建议避开头部品牌主攻的细分市场\n"

    md_content += f"""

### 4. 进入壁垒 (20分)
**得分**: {scores['barriers']}/20

- **Amazon自营占比**: {metrics['amazon_share']:.1f}%
- **新品机会**: {metrics['low_review_share']:.1f}%
"""

    if metrics['amazon_share'] < 20:
        md_content += "- Amazon自营产品较少，第三方卖家机会充足\n"
    elif metrics['amazon_share'] < 40:
        md_content += "- Amazon自营有一定布局，需注意价格竞争\n"
    else:
        md_content += "- Amazon自营占比较高，建议避开其主推产品\n"

    md_content += f"""

### 5. 利润空间 (15分)
**得分**: {scores['profit']}/15

- **平均价格**: ${metrics['avg_price']:.2f}
"""

    if metrics['avg_price'] > 30:
        md_content += "- 高客单价品类，利润空间充足\n"
        md_content += "- 可投入更多营销预算\n"
    elif metrics['avg_price'] > 15:
        md_content += "- 中等客单价，利润空间适中\n"
        md_content += "- 需要控制成本和营销费用\n"
    else:
        md_content += "- 低客单价品类，利润空间有限\n"
        md_content += "- 需要通过规模效应盈利\n"

    md_content += f"""

---

## 五、选品建议

### ✅ 推荐方向
"""

    # Generate recommendations based on analysis
    if metrics['low_review_share'] > 20:
        md_content += "1. **关注新品机会**: 评论数<100的产品占比较高，说明市场接受新产品的意愿较强\n"

    if metrics['top3_share'] < 50:
        md_content += "2. **选择细分赛道**: 品牌集中度适中，可以通过细分定位切入市场\n"

    if metrics['avg_price'] > 15:
        md_content += "3. **中高端定位**: 平均价格适中，可以尝试中高端差异化产品\n"

    md_content += f"""

### ⚠️ 注意事项
"""

    if metrics['amazon_share'] > 20:
        md_content += "- Amazon自营占比较高，注意避开其主推产品\n"

    if metrics['top3_share'] > 50:
        md_content += "- 头部品牌集中度高，建议避开与其直接竞争\n"

    if metrics['avg_price'] < 15:
        md_content += "- 客单价较低，需要重点关注供应链成本\n"

    md_content += f"""

---

## 六、风险提示

1. **价格竞争风险**: 该品类平均价格${metrics['avg_price']:.2f}，需注意价格战风险
2. **库存风险**: 该品类可能存在季节性波动，需合理规划库存
3. **合规风险**: 确保产品符合相关安全标准和认证要求
4. **IP风险**: 注意避免侵犯知名品牌的知识产权

---

*报告由 Claude Code 自动生成*
*数据来源: Sorftime MCP*
"""

    # Write the report
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"\n✅ 报告已生成: {filename}")
    return filename

def main():
    print("=" * 60)
    print("Board Games Category Analysis")
    print("=" * 60)

    # Step 1: Read existing category data
    print("\n[1/4] Reading category data...")
    data = read_existing_category_data()

    if not data or 'Top100产品' not in data:
        print("❌ Failed to parse category data")
        return

    products = data['Top100产品']
    print(f"✅ Found {len(products)} products in Top100")

    # Use Top20 products for analysis
    top_products = products[:20]
    print(f"✅ Analyzing Top20 products")

    # Step 2: Calculate scores
    print("\n[2/4] Calculating five-dimensional scores...")
    scores, metrics = calculate_five_dimension_score(data, top_products)

    print(f"✅ Market Size Score: {scores['market_size']}/20")
    print(f"✅ Growth Score: {scores['growth']}/25")
    print(f"✅ Competition Score: {scores['competition']}/20")
    print(f"✅ Barriers Score: {scores['barriers']}/20")
    print(f"✅ Profit Score: {scores['profit']}/15")
    print(f"✅ **Total Score: {scores['total']}/100**")

    # Step 3: Generate report
    print("\n[3/4] Generating markdown report...")
    report_file = generate_markdown_report(data, top_products, scores, metrics)

    # Step 4: Summary
    print("\n[4/4] Analysis complete!")
    print("=" * 60)

    if scores['total'] >= 85:
        rating = "优秀 🟢"
    elif scores['total'] >= 70:
        rating = "良好 🟡"
    elif scores['total'] >= 55:
        rating = "一般 🟠"
    else:
        rating = "较差 🔴"

    print(f"\n📊 Board Games Category Rating: {rating}")
    print(f"📈 Total Score: {scores['total']}/100")
    print(f"💰 Market Size: ${metrics['total_revenue']:,.2f}/month")
    print(f"🏆 Top3 Brand Share: {metrics['top3_share']:.1f}%")
    print(f"📦 Report: {report_file}")

if __name__ == "__main__":
    main()
