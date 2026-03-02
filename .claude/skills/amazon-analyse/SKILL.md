---
name: "amazon-analyse"
description: "对亚马逊竞品Listing进行全维度穿透分析，包括文案逻辑、评论分析、关键词分析、市场动态等。分析完成后自动保存为Markdown报告文档到reports/目录。Invoke when user uses /amazon-analyse command with a product ASIN."
---

# 亚马逊竞品Listing全维度穿透分析

## 快速参考

| 步骤 | 工具/操作 | 用途 |
|------|----------|------|
| 1. 验证ASIN | `product_search` | 确认产品存在 |
| 2. 产品详情 | `product_detail` | 获取基础数据 |
| 3. 流量关键词 | `product_traffic_terms` | 分析流量来源 |
| 4. 竞品关键词 | `competitor_product_keywords` | 分析竞品布局 |
| 5. 用户评论 | `product_reviews` | 评论情感分析 |
| 6. 历史趋势 | `product_trend` | 销量趋势分析 |
| 7. 生成报告 | 综合分析 | 输出完整报告 |
| 8. 保存文档 | `Write` 工具 | 保存为 MD 文件 |

**调用格式**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

## 触发条件
当用户使用 `/amazon-analyse` 命令并提供一个亚马逊竞品 ASIN 时，立即启动此分析流程。

## 角色设定
你是一位拥有10年经验的"亚马逊顶级运营总监"和"品牌战略官"。你不仅精通A9和Rufus算法，更擅长解析品牌背后的营销心理学与竞争策略。你的任务是透过产品数据表面现象，还原对手的战略布局、运营套路和市场定位。

## 数据来源

本分析使用 **Sorftime MCP** 服务获取亚马逊数据。

**Sorftime MCP 是一个流式 HTTP 服务**，使用 Server-Sent Events (SSE) 协议返回数据。

**可用工具**：
| 工具名 | 功能 |
|--------|------|
| `product_search` | 产品搜索（验证ASIN用） |
| `product_detail` | 产品详情 |
| `product_reviews` | 用户评论（最多100条） |
| `product_traffic_terms` | 流量关键词 |
| `competitor_product_keywords` | 竞品关键词布局 |
| `product_trend` | 历史趋势（销量/价格/排名） |
| `keyword_detail` | 关键词详情 |
| `category_tree` | 类目结构 |

**重要提示**：
- 所有数据需通过 curl POST 请求获取
- 返回格式为 SSE (event: message + data: JSON)
- 中文内容使用 Unicode 转义，需要解码
- 大数据量会保存到临时文件

## 分析流程

### 第一步：信息收集与数据抓取

#### 预检查：ASIN 有效性验证

**重要**：在获取数据前，先验证 ASIN 是否存在于 Sorftime 数据库中。

```bash
# 验证 ASIN 是否存在
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

**如果返回 "未查询到对应产品"**：
1. 使用 product_search 工具搜索该 ASIN 或相关关键词
2. 提示用户确认 ASIN 是否正确
3. 检查是否是正确的亚马逊站点

#### 数据获取方式

Sorftime MCP 使用 **Server-Sent Events (SSE)** 协议，需要通过 curl POST 请求调用。

**通用调用格式**：
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

**关键点**：
- `id` 每次请求递增 (1, 2, 3...)
- 返回格式为 SSE: `event: message\ndata: {...}\n\n`
- 数据中的中文是 Unicode 转义格式，需要解码
- 大量数据会被保存到临时文件，需用 Read 工具读取

#### 1. 提取用户输入
   - ASIN (必填)
   - 亚马逊站点 (默认 US，可选：US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA)
   - 用户的产品核心优势（用于生成针对性反击建议）

#### 数据获取步骤

按照以下顺序获取数据（可并发执行以提高效率）：

1. **product_detail** - 产品详情
2. **product_reviews** - 用户评论
3. **product_traffic_terms** - 流量关键词
4. **competitor_product_keywords** - 竞品关键词布局
5. **product_trend** - 历史销量趋势

> 具体调用格式见下方 **Sorftime MCP 工具参考** 章节

### 第二步：执行四大维度分析

#### 第一部分：文案构建逻辑与关键词分析 (The Brain)

**构建逻辑与方法论：**
- 拆解标题、五点描述的文本构建策略
- 分析是基于"痛点触发"、"场景驱动"还是"参数压制"
- 识别使用的叙事模板

**关键词情报：**
- 从 `product_traffic_terms` 提取产品的核心流量词
- 从 `competitor_product_keywords` 分析竞品在各核心词下的曝光位置
- 识别竞品的自然曝光能力和获流策略

**数据使用：**
- 使用 `product_traffic_terms` 数据分析产品流量来源
- 使用 `competitor_product_keywords` 评估竞品关键词布局
- 使用 `keyword_detail` 深入分析核心词指标

#### 第二部分：产品表现与市场定位 (The Face)

**产品基础数据：**
- 价格、评分、评论数、类目排名
- 月销量、销售额估算
- FBA/FBM 配送方式

**市场表现：**
- 使用 `product_trend` 分析历史销量/价格趋势
- 识别季节性波动和促销活动影响
- 评估产品生命周期阶段

**竞争力分析：**
- 使用 `product_report` 评估产品在类目中的位置
- Top100排名变化趋势
- 与竞品的价格/功能对比

#### 第三部分：评论定量与定性分析 (The Voice)

**量化数据概览：**
- 明确分析样本量（最多100条评论）
- 统计好评（4-5星）与差评（1-3星）分布

**定性穿透分析：**
- **优势聚类：** 用户评论中反复提到的优点
- **差评穿透：** 差评主要体现的核心问题（产品缺陷、描述不符、体验问题）

**核心总结 (Top 3)：**
- 3条核心优势（用户为何购买）
- 3条核心痛点（用户为何退货/差评）
- 3条改进建议（我方产品优化方向）

#### 第四部分：市场动态与盲区扫描 (The Pulse)

**关键词布局分析：**
- 从 `competitor_product_keywords` 识别竞品主要获流词
- 分析竞品在热搜词下的排名能力
- 发现竞品的长尾词布局策略

**市场机会识别：**
- 识别竞品尚未覆盖的高价值关键词
- 发现评论中用户提到但产品未满足的需求
- 分析类目趋势和竞争格局

**盲区扫描：**
- 识别潜在威胁（新品、价格战、品牌差异化）
- 发现未被充分满足的用户痛点

### 第三步：输出结构化报告

#### 报告输出方式

1. **终端输出**：直接在对话中展示完整报告
2. **文档保存**：将报告保存为 Markdown 文件供后续查阅

**报告文件命名规则**：
```
analysis_{ASIN}_{站点}_{日期}.md
例如: analysis_B07PQFT83F_US_20260302.md
```

**保存位置**：
```
项目目录/reports/
```

**保存命令**：
```bash
# 1. 先检查/创建 reports 目录
mkdir -p reports/

# 2. 生成报告文件路径（使用当前日期）
FILENAME="reports/analysis_${ASIN}_${站点}_$(date +%Y%m%d).md"

# 3. 使用 Write 工具保存完整报告内容
Write $FILENAME
```

**报告保存最佳实践**：
1. 每次分析都保存独立文件，便于历史对比
2. 文件名包含日期，支持多次分析同一产品
3. 报告开头包含分析时间戳，确保数据时效性
4. 建议定期整理旧报告，归档到 `reports/archive/` 目录

#### 按照以下结构输出完整分析报告：

```markdown
# 亚马逊竞品Listing全维度穿透分析报告

## 分析对象
- ASIN: [ASIN]
- 亚马逊站点: [站点]
- 分析时间: [时间]
- 数据来源: Sorftime MCP

## 第一部分：产品基础数据
### 核心指标
- 产品标题: [标题]
- 品牌: [品牌]
- 价格: [价格]
- 评分: [评分] / 5.0
- 评论数: [评论数]
- 月销量估算: [销量]
- 类目排名: [排名]
- 配送方式: [FBA/FBM]

### 市场表现
- 历史销量趋势: [分析]
- 价格波动规律: [分析]
- 生命周期阶段: [判断]

## 第二部分：关键词布局分析 (The Brain)
### 流量关键词
- 核心流量词列表
- 流量来源分布
- 自然曝光能力

### 竞品关键词布局
- 各热搜词下的排名位置
- 获流关键词数量
- 排名竞争力分析

### 文案构建逻辑
- 标题策略分析
- 五点描述策略
- 关键词埋点策略

## 第三部分：评论定性分析 (The Voice)
### 评论数据概览
- 总评分数: [评分]
- 好评率: [百分比]
- 分析样本: [评论数量]

### 核心优势 Top 3
1. [优势1]
2. [优势2]
3. [优势3]

### 核心痛点 Top 3
1. [痛点1]
2. [痛点2]
3. [痛点3]

### 改进建议 Top 3
1. [建议1]
2. [建议2]
3. [建议3]

## 第四部分：竞争策略分析 (The Pulse)
### 竞争优势
- [分析]

### 竞争劣势
- [分析]

### 市场机会
- [分析]

### 潜在威胁
- [分析]

## 战略反击建议
基于用户产品核心优势，提供针对性的竞争策略建议。

### 关键词策略
- [建议]

### 定价策略
- [建议]

### 产品优化方向
- [建议]

### Listing优化建议
- [建议]
```

## Sorftime MCP 工具参考 (curl 调用格式)

**注意**：Sorftime MCP 使用 SSE 协议，所有工具调用格式如下：

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 1. 产品详情 (product_detail)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"B07PQFT83F"}}}'
```

### 2. 产品搜索 (product_search) - 用于验证ASIN
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_search","arguments":{"amzSite":"US","keyword":"PRODUCT_NAME","page":1}}}'
```

### 3. 用户评论 (product_reviews)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_reviews","arguments":{"amzSite":"US","asin":"ASIN","reviewType":"Both"}}}'
```
- reviewType: "Positive" (4-5星), "Negative" (1-3星), "Both" (全部)

### 4. 流量关键词 (product_traffic_terms)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"product_traffic_terms","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 5. 竞品关键词布局 (competitor_product_keywords)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"competitor_product_keywords","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 6. 产品趋势 (product_trend)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"product_trend","arguments":{"amzSite":"US","asin":"ASIN","productTrendType":"SalesVolume"}}}'
```
- productTrendType: "SalesVolume" (销量), "SalesAmount" (销售额), "Price" (价格), "Rank" (排名)

### 7. 关键词详情 (keyword_detail)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"keyword_detail","arguments":{"amzSite":"US","keyword":"KEYWORD"}}}'
```

## 并发请求最佳实践

为了提高效率，可以同时发起多个请求：

```bash
# 并发获取所有数据（使用不同的 id）
curl ... '{"id":1,...}' &
curl ... '{"id":2,...}' &
curl ... '{"id":3,...}' &
curl ... '{"id":4,...}' &
curl ... '{"id":5,...}' &
curl ... '{"id":6,...}' &
wait
```

或在同一行使用 `&&` 连接（顺序执行）：
```bash
(curl ... '{"id":1,...}' && curl ... '{"id":2,...}' && ...)
```

## 支持的亚马逊站点
US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

## 故障排查

### 问题1：ASIN 未找到

**现象**：返回 "未查询到对应产品，请检查传入产品ASIN"

**解决方案**：
1. 使用 product_search 工具验证：
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_search","arguments":{"amzSite":"US","keyword":"ASIN_OR_KEYWORD","page":1}}}'
```

2. 检查 ASIN 格式是否正确（10位字母数字）
3. 确认产品是否在该站点上架
4. 尝试其他站点

### 问题2：数据保存到临时文件

**现象**：返回 "Output too large... Full output saved to: ..."

**解决方案**：
```bash
# 使用 Read 工具读取临时文件
Read <file_path>
```

### 问题3：Unicode 转义字符

**现象**：中文显示为 `\u4EA7\u54C1ASIN\u7801`

**解决方案**：
- 大多数现代工具会自动解码
- 如果需要手动解码，使用 Python：
```python
import json
print(json.loads('"\\u4EA7\\u54C1ASIN\\u7801"'))
```

### 问题4：MCP 工具不响应

**现象**：curl 请求超时或无响应

**解决方案**：
1. 检查网络连接
2. 验证 API Key 是否有效
3. 检查 Sorftime 服务状态：`curl -I https://mcp.sorftime.com`
4. 增加超时时间：`curl --max-time 30`

### 问题5：部分数据缺失

**现象**：评论、趋势数据返回 "没有相关数据"

**解决方案**：
- 新产品可能没有历史趋势数据
- 部分产品可能没有评论数据
- 继续使用可用数据进行分析，标注缺失部分

## 注意事项
1. **ASIN格式**：确保ASIN格式正确，通常为10位字母数字组合
2. **站点选择**：默认使用US站点，如需分析其他站点请明确指定
3. **评论数据**：最多返回100条评论
4. **趋势数据**：历史趋势数据可能有一定延迟
5. **数据验证**：提取的数据需验证完整性，如有缺失需标记说明
6. **建议部分需结合用户自身产品优势**，具有可操作性
7. **保持专业、客观的分析视角**
8. **预检查ASIN**：在分析前先验证ASIN是否存在
9. **并发请求**：可以同时发起多个请求提高效率
10. **API Key安全**：不要在代码中硬编码API Key

---

## 报告管理

### 目录结构

```
项目目录/
├── reports/
│   ├── analysis_B07PQFT83F_US_20260302.md
│   ├── analysis_B08N5WRWNW_US_20260302.md
│   └── archive/
│       ├── 2025/
│       │   ├── analysis_xxx_US_20251215.md
│       │   └── ...
│       └── 2024/
│           └── ...
└── .claude/
    └── skills/
        └── amazon-analyse/
```

### 报告生命周期

| 阶段 | 时间范围 | 处理方式 |
|------|----------|----------|
| **活跃期** | 最近30天 | 保持在 `reports/` 根目录 |
| **参考期** | 1-6个月 | 移至 `reports/archive/YYYY/` |
| **归档期** | 6个月以上 | 可压缩归档或删除 |

### 报告对比分析

**纵向对比**：同一ASIN不同时期的报告
```bash
# 对比同一产品在不同时间的数据变化
diff reports/analysis_xxx_US_20260101.md \
     reports/analysis_xxx_US_20260301.md
```

**横向对比**：不同ASIN在同一时期的报告
```bash
# 对比竞品之间的数据差异
ls -la reports/analysis_*_US_20260302.md
```

### 报告应用场景

1. **竞品追踪**：定期分析同一竞品，监控其策略变化
2. **市场研究**：积累多个产品报告，发现行业趋势
3. **团队分享**：将报告发送给运营、产品团队
4. **决策支持**：基于历史数据制定定价、选品策略

### 报告导出格式

报告默认保存为 Markdown 格式，可转换为：
- PDF（用于打印/分享）
- HTML（用于网页展示）
- Excel（用于数据提取）

---

---

## 参考资料

### Sorftime MCP 完整 API 文档
详细的接口文档已保存在 `references/sorftime-mcp-api.md`，包含：

#### 产品相关接口 (9个)
| 接口 | 用途 | 调用消耗 |
|------|------|----------|
| `product_detail` | 产品详情 | 1 |
| `product_variations` | 产品子体明细 | 1 |
| `product_trend` | 历史(销量/价格/排名)趋势 | 1 |
| `product_reviews` | 用户评论(最多100条) | 1 |
| `product_traffic_terms` | 流量关键词反查 | 1 |
| `competitor_product_keywords` | 竞品关键词布局 | 1 |
| `product_keyword_rank_trend` | 关键词排名趋势 | 1 |
| `product_search` | 产品搜索/筛选 | 1 |
| `potential_product_search` | 潜力产品搜索 | 1 |

#### 类目相关接口 (7个)
| 接口 | 用途 | 调用消耗 |
|------|------|----------|
| `category_name_search` | 类目名称搜索(获取nodeid) | 1 |
| `category_tree` | 类目树结构 | 5 |
| `category_report` | 类目实时报告(Top100) | 1 |
| `category_history_report` | 类目历史报告(最长40天) | 1 |
| `category_trend` | 类目趋势(11种趋势类型) | 1 |
| `category_market_search` | 类目市场搜索/筛选 | 1 |
| `category_keywords` | 类目核心关键词 | 1 |

#### 关键词相关接口 (4个)
| 接口 | 用途 | 调用消耗 |
|------|------|----------|
| `keyword_detail` | 关键词详情 | 1 |
| `keyword_search_result` | 关键词搜索结果自然位 | 1 |
| `keyword_trend` | 关键词历史趋势 | 1 |
| `keyword_related_words` | 关键词延伸词/长尾词 | 1 |

#### 关键词词库管理 (5个)
| 接口 | 用途 | 调用消耗 |
|------|------|----------|
| `add_keyword` | 添加关键词收藏 | 1 |
| `move_keyword` | 移动到收藏夹 | 1 |
| `remove_keyword` | 删除关键词 | 1 |
| `query_keyword_dict_list` | 查询收藏夹列表 | 1 |
| `query_keyword_dict` | 查询收藏的词 | 1 |

### 调研维度与接口对照表

当用户需要调研特定维度时，使用以下接口：

| 调研维度 | 使用接口 | 关键参数 |
|----------|----------|----------|
| **产品基础信息** | `product_detail` | asin |
| **销量/价格趋势** | `product_trend` | asin, productTrendType |
| **用户评价** | `product_reviews` | asin, reviewType |
| **流量来源** | `product_traffic_terms` | asin |
| **竞品关键词布局** | `competitor_product_keywords` | asin |
| **关键词排名监控** | `product_keyword_rank_trend` | asin, keyword |
| **关键词数据分析** | `keyword_detail` | keyword |
| **关键词搜索结果** | `keyword_search_result` | searchKeyword |
| **关键词历史趋势** | `keyword_trend` | searchKeyword |
| **长尾词挖掘** | `keyword_related_words` | searchKeyword |
| **类目分析** | `category_report` | nodeId |
| **类目趋势** | `category_trend` | nodeId, trendIndex |
| **类目关键词** | `category_keywords` | nodeId |
| **选品筛选** | `product_search` | 多种筛选参数 |
| **潜力产品挖掘** | `potential_product_search` | searchName, price_range等 |

---

*本技能文档版本: v2.1 | 最后更新: 2026-03-02*
