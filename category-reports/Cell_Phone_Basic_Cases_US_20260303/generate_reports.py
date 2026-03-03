import json
import os
import xlsxwriter

# Load data
data_file = r"D:\amazon-mcp\category-reports\Cell_Phone_Basic_Cases_US_20260303\data.json"
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

output_dir = os.path.dirname(data_file)
rating_color = data['scores']['rating_color']

# Create Markdown Report
md_content = f"""# 亚马逊品类选品分析报告

## 分析对象
- **品类名称**: {data['category']}
- **亚马逊站点**: {data['site']}
- **分析时间**: {data['date']}
- **数据来源**: Sorftime MCP
- **Node ID**: {data['nodeId']}

---

## 执行摘要

| 评分项 | 得分 | 满分 |
|--------|------|------|
| 市场规模 | {data['scores']['market_size_score']} | 20 |
| 增长潜力 | {data['scores']['growth_score']} | 25 |
| 竞争烈度 | {data['scores']['competition_score']} | 20 |
| 进入壁垒 | {data['scores']['barrier_score']} | 20 |
| 利润空间 | {data['scores']['profit_score']} | 15 |
| **综合得分** | **{data['scores']['total_score']}** | **100** |

### 综合评级: {data['scores']['rating']}

---

## 一、市场规模分析

### 市场规模评分: {data['scores']['market_size_score']}/20

### 市场数据
| 指标 | 数值 |
|------|------|
| Top100 月销量 | {data['statistics']['total_sales']:,} 件 |
| Top100 月销额 | ${data['statistics']['total_revenue']:,.2f} |
| 平均价格 | ${data['statistics']['avg_price']:.2f} |
| 中位数价格 | ${data['statistics']['median_price']:.2f} |
| 平均评分 | {data['statistics']['avg_rating']:.2f} |
| Top3品牌占比 | {data['statistics']['top3_brand_share']:.1f}% |
| Amazon自营占比 | {data['statistics']['amazon_share']:.1f}% |
| 高评分占比 | {data['statistics']['high_rated_share']:.1f}% |

---

## 二、Top 20 产品

| 排名 | ASIN | 标题 | 价格 | 销量 | 评分 | 品牌 |
|------|------|------|------|------|------|------|
"""

for idx, p in enumerate(data['products'], 1):
    md_content += f"| {idx} | {p['ASIN']} | {p['title'][:60]}... | ${p['price']:.2f} | {p['sales']:,} | {p['rating']} | {p['brand']} |\n"

md_content += r"""

## 三、品牌分析

### Top 10 品牌

| 排名 | 品牌 | 月销量 | 市场份额 |
|------|------|--------|----------|
"""

for idx, b in enumerate(data['brands'], 1):
    md_content += f"| {idx} | {b['name']} | {b['sales']:,} | {b['share']:.1f}% |\n"

md_content += r"""

---

*本报告由 Sorftime MCP 数据驱动生成*
"""

# Save Markdown
md_file = os.path.join(output_dir, "report.md")
with open(md_file, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Markdown report saved: {md_file}")

# Create Excel Report
excel_file = os.path.join(output_dir, f"category_report_{data['category'].replace(' ', '_')}_{data['site']}.xlsx")
wb = xlsxwriter.Workbook(excel_file)

header_fmt = wb.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1})
title_fmt = wb.add_format({'bold': True, 'font_size': 16, 'bg_color': '#4472C4', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter'})
bold_fmt = wb.add_format({'bold': True, 'bg_color': '#E7E6E6'})
number_fmt = wb.add_format({'num_format': '#,##0'})
currency_fmt = wb.add_format({'num_format': '$#,##0.00'})
percent_fmt = wb.add_format({'num_format': '0.0%'})
center_fmt = wb.add_format({'align': 'center'})

# Summary Sheet
ws_summary = wb.add_worksheet("分析摘要")
ws_summary.merge_range('A1:E1', f"Amazon Category Analysis - {data['category']}", title_fmt)
ws_summary.set_row(0, 30)

ws_summary.write('A3', 'Category', bold_fmt)
ws_summary.write('B3', data['category'])
ws_summary.write('A4', 'Site', bold_fmt)
ws_summary.write('B4', data['site'])
ws_summary.write('A5', 'Date', bold_fmt)
ws_summary.write('B5', data['date'])

# Scores
ws_summary.write('A7', 'Metric', header_fmt)
ws_summary.write('B7', 'Score', header_fmt)
ws_summary.write('C7', 'Max', header_fmt)

scores_data = [
    ("Market Size", data['scores']['market_size_score'], 20),
    ("Growth Potential", data['scores']['growth_score'], 25),
    ("Competition", data['scores']['competition_score'], 20),
    ("Entry Barrier", data['scores']['barrier_score'], 20),
    ("Profit Space", data['scores']['profit_score'], 15),
]

row = 8
for name, score, max_score in scores_data:
    ws_summary.write(row, 0, name)
    ws_summary.write(row, 1, score)
    ws_summary.write(row, 2, max_score)
    row += 1

ws_summary.write(row, 0, "Total Score", wb.add_format({'bold': True, 'font_size': 12}))
ws_summary.write(row, 1, f"{data['scores']['total_score']}/100")
ws_summary.write(row, 2, data['scores']['rating'])

# Statistics
row += 2
ws_summary.write(row, 0, "Market Statistics", wb.add_format({'bold': True, 'font_size': 12}))
row += 1

stats = data['statistics']
stats_data = [
    ("Monthly Sales", stats['total_sales'], 'number'),
    ("Monthly Revenue", stats['total_revenue'], 'currency'),
    ("Avg Price", stats['avg_price'], 'currency'),
    ("Median Price", stats['median_price'], 'currency'),
    ("Avg Rating", f"{stats['avg_rating']:.2f}", 'text'),
    ("Top3 Brand Share", stats['top3_brand_share'] / 100, 'percent'),
    ("Amazon Share", stats['amazon_share'] / 100, 'percent'),
]

for label, value, fmt_type in stats_data:
    ws_summary.write(row, 0, label)
    if fmt_type == 'number':
        ws_summary.write(row, 1, value, number_fmt)
    elif fmt_type == 'currency':
        ws_summary.write(row, 1, value, currency_fmt)
    elif fmt_type == 'percent':
        ws_summary.write(row, 1, value, percent_fmt)
    else:
        ws_summary.write(row, 1, value)
    row += 1

ws_summary.set_column('A:A', 20)
ws_summary.set_column('B:B', 18)

# Products Sheet
ws_products = wb.add_worksheet("Top Products")
headers = ["Rank", "ASIN", "Title", "Price", "Sales", "Revenue", "Rating", "Reviews", "Brand", "Seller"]
for col, header in enumerate(headers):
    ws_products.write(0, col, header, header_fmt)

for idx, product in enumerate(data['products']):
    row = idx + 1
    ws_products.write(row, 0, idx + 1, center_fmt)
    ws_products.write(row, 1, product['ASIN'])
    ws_products.write(row, 2, product['title'][:50])
    ws_products.write(row, 3, product['price'], currency_fmt)
    ws_products.write(row, 4, product['sales'], number_fmt)
    ws_products.write(row, 5, product['revenue'], currency_fmt)
    ws_products.write(row, 6, product['rating'])
    ws_products.write(row, 7, product.get('reviews', 0), number_fmt)
    ws_products.write(row, 8, product['brand'])
    ws_products.write(row, 9, product['seller'])

ws_products.set_column('A:A', 8)
ws_products.set_column('B:B', 14)
ws_products.set_column('C:C', 50)
ws_products.set_column('D:H', 12)
ws_products.set_column('I:J', 20)

wb.close()
print(f"Excel report saved: {excel_file}")
