---
name: "category-selection"
description: "亚马逊品类自动化选品分析技能。通过五维评分模型对亚马逊品类进行深度市场调研，生成Markdown分析报告。当用户使用 /category-select 命令或提出'分析XX品类'、'XX品类市场调研'、'XX品类选品'等需求时触发此技能。支持配置分析数量，默认Top20。"
---

# 亚马逊品类选品分析

## 快速参考

| 步骤 | 工具/操作 | 用途 |
|------|----------|------|
| 1. 搜索类目 | `category_name_search` | 获取类目 nodeId |
| 2. 类目报告 | `category_report` | 获取 Top 产品列表和统计数据 |
| 3. 产品详情 | `product_detail` | 获取单个产品详情 |
| 4. 类目关键词 | `category_keywords` | 获取类目核心关键词 |
| 5. 1688采购 | `products_1688` | 获取供应链成本 |

**调用格式**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

## 触发条件

当用户使用以下方式请求时，启动此分析流程：
- **命令**: `/category-select {品类名称} {站点} [--limit N]`
- **示例**: `/category-select "Sofas & Couches" US --limit 20`
- **自然语言**: "分析Amazon美国站的Sofas品类"、"Sofas品类市场调研"、"Sofas品类选品"

## 角色设定

你是一位拥有10年经验的"亚马逊选品专家"和"市场分析师"。你精通品类分析方法论，能够通过数据洞察市场机会、竞争格局和进入壁垒，为用户提供可执行的选品建议。

## 数据来源

本分析使用 **Sorftime MCP** 服务获取亚马逊数据。

**Sorftime MCP 是一个流式 HTTP 服务**，使用 Server-Sent Events (SSE) 协议返回数据。

**品类分析可用工具**：
| 工具名 | 功能 |
|--------|------|
| `category_name_search` | 搜索类目名称获取 nodeId |
| `category_report` | 类目实时报告 (Top100 产品 + 统计数据) |
| `category_tree` | 类目树结构 |
| `category_trend` | 类目历史趋势 |
| `category_keywords` | 类目核心关键词 |
| `product_detail` | 产品详情 |
| `products_1688` | 1688 采购成本分析 |

**重要提示**：
- 所有数据需通过 curl POST 请求获取
- 返回格式为 SSE (event: message + data: JSON)
- 中文内容使用 Unicode 转义，需要解码
- **大数据量会保存到临时文件**，需要特殊处理 (见下方"大数据处理"章节)

## 分析流程

### 第一步：信息收集与数据抓取

#### 1.1 搜索类目获取 nodeId

**工具**: `category_name_search`

**调用示例**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"Sofas"}}}'
```

**参数说明**:
- `amzSite`: 亚马逊站点 (US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA)
- `searchName`: 类目名称

**返回处理**:
- 找到多个类目时，让用户确认选择哪个
- 优先选择与用户搜索意图最匹配的类目
- 保存 `NodeId` 用于后续调用

#### 1.2 获取类目报告 (核心数据)

**工具**: `category_report`

**调用示例**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_report","arguments":{"amzSite":"US","nodeId":"3733551"}}}'
```

**参数说明**:
- `amzSite`: 亚马逊站点
- `nodeId`: 类目 ID (从上一步获取)

**返回数据包含**:
- **Top100 产品列表**: ASIN, 标题, 价格, 销量, 评分, 品牌, 卖家等
- **类目统计数据**:
  - `top100产品月销量`: 总销量
  - `top100产品月销额`: 总销额
  - `average_price`: 平均价格
  - `median_price`: 中位数价格
  - `top3_brands_sales_volume_share`: Top3 品牌销量占比
  - `amazonOwned_sales_volume_share`: Amazon 自营占比
  - `high_rated_sales_volume_share`: 高评分产品占比
  - `low_reviews_sales_volume_share`: 低评论产品占比 (新品机会指标)

#### 1.3 获取产品详情 (可选)

**工具**: `product_detail`

**调用示例**:
```bash
# 对 TopN 产品逐个获取详情
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"B07PQFT83F"}}}'
```

**并发策略**: 可以同时发起多个请求提高效率

```bash
# 并发获取多个产品详情
curl ... '{"id":3,...,"arguments":{"asin":"ASIN1"}}' &
curl ... '{"id":4,...,"arguments":{"asin":"ASIN2"}}' &
curl ... '{"id":5,...,"arguments":{"asin":"ASIN3"}}' &
wait
```

#### 1.4 获取类目关键词 (可选)

**工具**: `category_keywords`

**调用示例**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"category_keywords","arguments":{"amzSite":"US","nodeId":"3733551","page":1}}}'
```

#### 1.5 获取 1688 采购成本 (可选)

**工具**: `products_1688`

**调用示例**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"products_1688","arguments":{"searchName":"产品名称"}}}'
```

---

### 🔧 大数据处理 (关键章节)

**问题**: `category_report` 返回的数据通常超过 25000 token，无法直接用 Read 工具读取。

**解决方案**: 使用以下标准流程处理大数据。

#### 方法一：使用 Grep 提取关键统计数据 (推荐)

```bash
# 从临时文件中提取关键统计数据
grep -o '"top100[^"]*":"[^"]*"' /path/to/tempfile.txt
grep -o '"average_price":"[^"]*"' /path/to/tempfile.txt
grep -o '"amazonOwned[^"]*":"[^"]*"' /path/to/tempfile.txt
```

**更高效的方式** - 使用 Python 一键提取：

```python
# 保存为 scripts/extract_category_stats.py
import re
import sys

def extract_stats(file_path):
    """从 Sorftime 响应文件中提取统计数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 定义需要提取的字段
    patterns = {
        '总销量': r'"top100产品月销量":"?(\d+)"?',
        '总销额': r'"top100产品月销额":"?([\d.]+)"?',
        '平均价格': r'"average_price":"?([\d.]+)"?',
        '中位数价格': r'"median_price":"?([\d.]+)"?',
        'Top3品牌占比': r'"top3_brands_sales_volume_share":"?([\d.]+%?)"?',
        'Amazon自营占比': r'"amazonOwned_sales_volume_share":"?([\d.]+%?)"?',
        '高评分占比': r'"high_rated_sales_volume_share":"?([\d.]+%?)"?',
        '低评论占比': r'"low_reviews_sales_volume_share":"?([\d.]+%?)"?',
    }

    results = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            results[name] = match.group(1)

    return results

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else input("输入文件路径: ")
    stats = extract_stats(file_path)

    print("=== 类目统计数据 ===")
    for name, value in stats.items():
        print(f"{name}: {value}")
```

**使用方式**:
```bash
python scripts/extract_category_stats.py /path/to/tempfile.txt
```

#### 方法二：提取 Top N 产品信息

```python
# 保存为 scripts/extract_top_products.py
import re
import json
import sys

def extract_top_products(file_path, limit=10):
    """提取 Top N 产品"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 SSE data 行中的 JSON
    for line in content.split('\n'):
        if line.startswith('data: '):
            # 解析 JSON 并解码 Unicode
            # (完整代码见 sorftime_parser.py)
            pass

    # 或者使用正则直接提取
    asin_pattern = r'"ASIN":"([A-Z0-9]{10})".*?"标题":"([^"]{50,120})".*?"价格":([\d.]+).*?"月销量":"?(\d+)"?.*?"星级":"?([\d.]+)"?.*?"品牌":"([^"]+)"'

    products = []
    for match in re.finditer(asin_pattern, content):
        asin, title, price, sales, rating, brand = match.groups()
        products.append({
            'ASIN': asin,
            'title': title[:80],
            'price': float(price),
            'sales': int(sales),
            'rating': float(rating),
            'brand': brand
        })
        if len(products) >= limit:
            break

    return products

if __name__ == "__main__":
    file_path = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    products = extract_top_products(file_path, limit)

    print(f"=== Top {len(products)} 产品 ===")
    for i, p in enumerate(products, 1):
        print(f"\n{i}. {p['ASIN']}")
        print(f"   {p['title']}")
        print(f"   价格: ${p['price']:.2f} | 销量: {p['sales']:,} | 评分: {p['rating']}★")
```

#### 方法三：完整解析脚本 (一次处理所有数据)

```bash
# 创建一个完整的数据提取脚本
cat > scripts/parse_category_report.py << 'SCRIPT_EOF'
#!/usr/bin/env python3
import re
import json
import sys
import codecs

def parse_category_report(file_path, limit=20):
    """完整解析类目报告"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 提取统计数据
    stats = extract_statistics(content)

    # 2. 提取 Top 产品
    products = extract_products(content, limit)

    # 3. 计算五维评分
    scores = calculate_scores(stats)

    return {
        'statistics': stats,
        'products': products,
        'scores': scores
    }

def extract_statistics(content):
    # ... (实现)
    pass

def extract_products(content, limit):
    # ... (实现)
    pass

def calculate_scores(stats):
    # ... (实现)
    pass

if __name__ == "__main__":
    result = parse_category_report(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
SCRIPT_EOF
```

#### 大数据处理标准流程

```bash
# 1. 调用 API (数据保存到临时文件)
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_report","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}' \
  > temp_response.txt

# 2. 提取统计数据
python scripts/extract_category_stats.py temp_response.txt

# 3. 提取 Top 产品
python scripts/extract_top_products.py temp_response.txt 20

# 4. 基于提取的数据生成报告
```

#### 降级处理方案

当数据无法完整解析时的降级策略：

| 场景 | 降级方案 |
|------|----------|
| 统计数据解析失败 | 使用 Top 产品数据估算市场规模 |
| 产品列表解析失败 | 仅基于统计数据给出分析 |
| 大数据超时 | 减少分析数量 (Top20 → Top10) |
| JSON 解析错误 | 使用正则表达式提取关键数据 |

---

### 第二步：数据分析与评分

#### 2.1 提取关键指标

从 `category_report` 返回的数据中提取以下指标：

| 指标 | 数据源 | 用途 |
|------|--------|------|
| 总销额 | `top100产品月销额` | 市场规模评估 |
| Top3 品牌占比 | `top3_brands_sales_volume_share` | 竞争集中度 |
| Amazon 自营占比 | `amazonOwned_sales_volume_share` | 平台挤压程度 |
| 低评论产品占比 | `low_reviews_sales_volume_share` | 新品机会 |
| 平均价格 | `average_price` | 利润空间参考 |

#### 2.2 计算五维评分

```python
# 市场规模 (20分)
revenue = float(stats.get('top100产品月销额', 0))
if revenue > 10000000:
    market_size_score = 20
elif revenue > 5000000:
    market_size_score = 17
elif revenue > 1000000:
    market_size_score = 14
else:
    market_size_score = 10

# 增长潜力 (25分) - 基于低评论产品占比 (新品机会)
new_product_share = float(stats.get('low_reviews_sales_volume_share', '0%').replace('%', ''))
if new_product_share > 40:
    growth_score = 22
elif new_product_share > 20:
    growth_score = 18
else:
    growth_score = 14

# 竞争烈度 (20分) - 基于 Top3 品牌占比
top3_share = float(stats.get('top3_brands_sales_volume_share', '0%').replace('%', ''))
if top3_share < 30:
    competition_score = 18  # 低度集中，竞争较小
elif top3_share < 50:
    competition_score = 14  # 中度集中
else:
    competition_score = 8   # 高度集中，竞争激烈

# 进入壁垒 (20分)
amazon_share = float(stats.get('amazonOwned_sales_volume_share', '0%').replace('%', ''))
barrier_score = 0

# Amazon 占比越低，壁垒越小
if amazon_share < 20:
    barrier_score += 10
elif amazon_share < 40:
    barrier_score += 6
else:
    barrier_score += 3

# 新品机会越大，壁垒越小
if new_product_share > 40:
    barrier_score += 10
elif new_product_share > 20:
    barrier_score += 6
else:
    barrier_score += 3

# 利润空间 (15分) - 基于平均价格
avg_price = float(stats.get('average_price', 0))
if avg_price > 300:
    profit_score = 12
elif avg_price > 150:
    profit_score = 10
elif avg_price > 50:
    profit_score = 7
else:
    profit_score = 4

# 计算总分
total_score = market_size_score + growth_score + competition_score + barrier_score + profit_score
```

#### 2.3 评级判定

| 总分 | 评级 | 建议 |
|------|------|------|
| 80-100 | 优秀 | 强烈推荐进入 |
| 70-79 | 良好 | 可以考虑进入 |
| 50-69 | 一般 | 谨慎进入 |
| 0-49 | 较差 | 不建议进入 |

### 第三步：生成报告

#### 报告格式说明

本技能支持 **4 种报告格式**，所有报告保存在统一的输出文件夹中：

| 格式 | 文件名 | 说明 |
|------|--------|------|
| **Markdown** | `category_analysis_report.md` | 完整分析报告，易于阅读 |
| **Excel** | `category_analysis_report.xlsx` | 多工作表详细数据，含图表 |
| **HTML** | `dashboard.html` | 可视化交互式仪表板 |
| **CSV** | `data/*.csv` | 原始数据文件，用于二次处理 |

#### 报告生成方法

**方法一：使用解析脚本自动生成 (推荐)**

```bash
# 1. 解析 API 响应并生成所有报告
python scripts/parse_sorftime_sse.py temp_response.txt 20 --生成报告

# 输出目录示例:
# category-reports/Phone_Cases_20260303/
# ├── category_analysis_report.md
# ├── category_analysis_report.xlsx
# ├── dashboard.html
# └── data/
#     ├── statistics.csv
#     ├── products.csv
#     ├── scores.csv
#     └── raw_data.json
```

**方法二：使用报告生成器**

```bash
# 1. 先解析数据为 JSON
python scripts/parse_sorftime_sse.py temp_response.txt 20 --json > parsed_data.json

# 2. 生成所有报告
python scripts/generate_reports.py parsed_data.json
```

**方法三：手动使用 Write 工具保存 Markdown**

```bash
# 创建输出目录
mkdir -p category-reports/{品类名}_{日期}

# 保存 Markdown 报告
Write category-reports/{品类名}_{日期}/category_analysis_report.md
```

#### 输出目录结构

```
category-reports/
└── {品类名称}_{日期}/              # 例如: Phone_Cases_20260303/
    ├── category_analysis_report.md  # Markdown 主报告
    ├── category_analysis_report.xlsx # Excel 详细报告
    ├── dashboard.html               # HTML 可视化仪表板
    └── data/                        # 原始数据目录
        ├── statistics.csv           # 统计数据
        ├── products.csv             # 产品列表
        ├── scores.csv               # 评分详情
        └── raw_data.json            # JSON 原始数据
```

#### CSV 数据文件说明

所有 CSV 文件使用 UTF-8-BOM 编码，可在 Excel 中直接打开：

**statistics.csv** - 统计指标
```
指标,数值
总销量,1878842
总销额,28121040.07
平均价格,17.239
...
```

**products.csv** - 产品列表
```
排名,ASIN,标题,品牌,价格,月销量,评分
1,B0FH655984,SUPFINE Magnetic...,SUPFINE,5.59,228880,4.6
2,B0FLT3RL8C,Miracase...,Miracase,16.93,96199,4.3
...
```

**scores.csv** - 评分详情
```
维度,得分,满分,占比%
市场规模,20,20,100.0
增长潜力,14,25,56.0
...
```

#### 报告结构

```markdown
# 亚马逊品类选品分析报告

## 分析对象
- 品类名称: [品类]
- 亚马逊站点: [站点]
- 分析时间: [时间]
- 数据来源: Sorftime MCP

## 执行摘要
- 综合评级: [优秀/良好/一般/较差]
- 总分: [XX]/100
- 建议: [简要建议]

## 一、市场规模分析
### 市场规模评分: [XX]/20

### 市场数据
- Top100 月销量: [数量]
- Top100 月销额: [金额]
- 平均价格: [价格]
- 中位数价格: [价格]

### 市场规模评估
[分析市场规模的大小和潜力]

## 二、增长潜力分析
### 增长潜力评分: [XX]/25

### 新品机会指标
- 低评论产品销量占比: [百分比]
- 分析: [新品进入空间评估]

### 增长潜力评估
[分析品类增长潜力]

## 三、竞争格局分析
### 竞争烈度评分: [XX]/20

### 品牌集中度
- Top3 品牌销量占比: [百分比]
- 集中度评估: [低度/中度/高度集中]

### Amazon 自营影响
- Amazon 自营销量占比: [百分比]
- 影响评估: [对第三方卖家的影响]

### 竞争格局评估
[分析竞争环境和机会]

## 四、进入壁垒分析
### 进入壁垒评分: [XX]/20

### 壁垒因素分析
- Amazon 自营压力: [评估]
- 新品竞争空间: [评估]
- 评价积累要求: [评估]

### 进入难度评估
[分析进入该品类的难易程度]

## 五、利润空间分析
### 利润空间评分: [XX]/15

### 价格分析
- 平均价格: [价格]
- 价格分布: [分析]

### 利润空间评估
[分析利润空间和定价策略]

## 六、Top 产品分析

### Top 10 产品
| 排名 | ASIN | 标题 | 价格 | 销量 | 评分 | 品牌 |
|------|------|------|------|------|------|------|
| 1 | [ASIN] | [标题] | [价格] | [销量] | [评分] | [品牌] |
| ... | ... | ... | ... | ... | ... | ... |

### 竞品特点分析
[分析头部产品的共同特点和成功因素]

## 七、选品建议

### 进入策略
[基于数据分析给出具体的进入策略]

### 产品定位建议
[产品差异化定位建议]

### 定价策略建议
[基于价格分析的定价建议]

### 运营策略建议
[运营和推广策略建议]

### 风险提示
[需要规避的风险和注意事项]

---

## Sorftime MCP 工具参考

### 1. 类目名称搜索 (category_name_search)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"品类名称"}}}'
```

### 2. 类目报告 (category_report)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_report","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

### 3. 产品详情 (product_detail)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 4. 类目关键词 (category_keywords)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"category_keywords","arguments":{"amzSite":"US","nodeId":"NODE_ID","page":1}}}'
```

### 5. 1688 采购 (products_1688)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"products_1688","arguments":{"searchName":"产品名称"}}}'
```

## 并发请求最佳实践

```bash
# 并发获取多个数据
curl ... '{"id":1,...}' &
curl ... '{"id":2,...}' &
curl ... '{"id":3,...}' &
wait
```

## 支持的亚马逊站点

US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

## 故障排查

### 问题1：类目未找到

**现象**: 返回 "未查询到对应类目"

**解决方案**:
1. 检查类目名称拼写
2. 使用更通用的类目名称
3. 尝试英文类目名称

### 问题2：数据保存到临时文件

**现象**: 返回 "Output too large... Full output saved to: ..."

**解决方案**: 使用 Read 工具读取临时文件

### 问题3：Unicode 转义字符

**现象**: 中文显示为 `\u4ea7\u54c1`

**解决方案**: 大多数现代工具会自动解码，如需手动解码使用 Python 的 `json.loads()` 或 `codecs.decode()`

## 注意事项

1. **参数名称**: 使用 `amzSite` 而非 `site`
2. **节点ID**: 确保使用正确的 `nodeId`
3. **并发限制**: 建议最多 5 个并发请求
4. **数据时效**: 数据可能有一定延迟
5. **报告保存**: 每次分析保存独立文件便于对比

---

*本技能文档版本: v4.0 | 最后更新: 2026-03-03*
*重构为 MCP 风格，与 amazon-analyse 保持一致*
