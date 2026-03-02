# amazon sorftime research MCP skill - 亚马逊竞品分析工作区

基于 Sorftime MCP 服务和 Claude Skills 的亚马逊竞品分析工具集。

## 项目简介

本项目配置了 Sorftime 跨境电商数据服务的 MCP (Model Context Protocol) 服务器，并开发了 `amazon-analyse` 技能，用于对亚马逊竞品 Listing 进行全维度穿透分析。

### 核心功能

- **竞品Listing分析**: 自动获取产品详情、评论、关键词、趋势数据
- **关键词分析**: 流量来源、竞品布局、长尾词挖掘
- **评论情感分析**: 优势聚类、痛点识别、改进建议
- **市场洞察**: 季节性趋势、竞争格局、机会识别

---

## 快速开始

### 环境要求

- Claude Code CLI
- 有效的 Sorftime API Key
- Bash shell 环境



### 安装 MCP 服务器

MCP 配置文件位于 `.mcp.json`，已配置 Sorftime 服务：

```json
{
  "mcpServers": {
    "sorftime": {
      "type": "streamableHttp",
      "url": "https://mcp.sorftime.com?key=YOUR_API_KEY",
      "name": "Sorftime MCP"
    }
  }
}
```

### 使用分析技能

```bash
# 分析美国站竞品
/amazon-analyse B07PWTJ4H1 US

# 分析欧洲站竞品
/amazon-analyse B08N5WRWNW DE
```

分析完成后，报告将自动保存到 `reports/` 目录。

---

## Sorftime MCP 服务

### 支持的亚马逊站点

| 站点 | 代码 | 站点 | 代码 |
|------|------|------|------|
| 美国 | US | 墨西哥 | MX |
| 英国 | GB | 阿联酋 | AE |
| 德国 | DE | 澳大利亚 | AU |
| 法国 | FR | 巴西 | BR |
| 印度 | IN | 沙特 | SA |
| 加拿大 | CA | - | - |
| 日本 | JP | - | - |
| 西班牙 | ES | - | - |
| 意大利 | IT | - | - |

### 可用接口 (25个)

#### 产品相关 (9个)
| 接口 | 功能 |
|------|------|
| `product_detail` | 产品详情 |
| `product_variations` | 子体明细 |
| `product_trend` | 销量/价格/排名趋势 |
| `product_reviews` | 用户评论 |
| `product_traffic_terms` | 流量关键词 |
| `competitor_product_keywords` | 竞品关键词布局 |
| `product_search` | 产品搜索筛选 |
| `potential_product_search` | 潜力产品挖掘 |

#### 类目相关 (7个)
| 接口 | 功能 |
|------|------|
| `category_report` | 类目实时报告 |
| `category_trend` | 类目趋势分析 |
| `category_keywords` | 类目核心词 |
| `category_market_search` | 类目市场搜索 |

#### 关键词相关 (4个)
| 接口 | 功能 |
|------|------|
| `keyword_detail` | 关键词详情 |
| `keyword_trend` | 关键词趋势 |
| `keyword_related_words` | 长尾词挖掘 |
| `keyword_search_result` | 搜索结果排名 |

---

## 项目结构

```
amazon-mcp/
├── .mcp.json                    # MCP 配置文件
├── .claude/
│   └── skills/
│       └── amazon-analyse/      # 竞品分析技能
│           ├── SKILL.md         # 技能主文档
│           └── references/
│               └── sorftime-mcp-api.md  # API 完整文档
├── reports/                     # 分析报告目录
│   ├── analysis_XXX_US_YYYYMMDD.md
│   └── archive/
│       ├── 2025/
│       └── 2024/
└── README.md                    # 本文档
```

---

## 分析报告说明

### 报告结构

每份分析报告包含以下部分：

1. **产品基础数据** - 价格、评分、排名、销量
2. **关键词布局分析** - 流量词、竞品布局、文案策略
3. **评论定性分析** - 优势/痛点 Top 3、改进建议
4. **竞争策略分析** - SWOT 分析、市场机会
5. **战略反击建议** - 关键词、定价、产品、Listing 优化

### 报告命名规范

```
analysis_{ASIN}_{站点}_{日期}.md
例: analysis_B07PWTJ4H1_US_20260302.md
```

### 报告管理

| 阶段 | 时间范围 | 位置 |
|------|----------|------|
| 活跃期 | 最近30天 | `reports/` |
| 参考期 | 1-6个月 | `reports/archive/YYYY/` |
| 归档期 | 6个月+ | 可删除或压缩 |

---

## 常见问题

### Q: API Key 在哪里配置？

A: 编辑 `.mcp.json` 文件，将 `YOUR_API_KEY` 替换为你的 Sorftime API Key。
sorftime mcp key 地址：
https://sorftime.com/zh-cn/mcp

### Q: 支持哪些分析维度？

A: 支持 15+ 维度分析，包括：
- 产品基础信息
- 销量/价格趋势
- 用户评价情感
- 流量来源分析
- 竞品关键词布局
- 类目市场分析
- 长尾词挖掘

### Q: 分析需要多长时间？

A: 通常 30-60 秒，取决于数据量和网络状况。

### Q: 报告可以导出吗？

A: 报告为 Markdown 格式，可转换为 PDF、HTML、Excel。

---

## 技能开发

### 创建新技能

使用 `skill-creator` 技能快速创建：

```bash
# 初始化新技能模板
.claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path .claude/skills

# 打包技能为 .skill 文件
.claude/skills/skill-creator/scripts/package_skill.py <skill-folder>
```

### 技能设计原则

1. **YAML frontmatter** - 包含完整的 `description` 说明使用场景
2. **Progressive disclosure** - SKILL.md 保持精简，细节放入 references/
3. **Scripts** - 用于需要确定性执行的代码
4. **References** - 存放 API 文档、指南等参考资料
5. **Assets** - 输出文件所需的模板、图片等

---

## 更新日志

### v2.1 (2026-03-02)
- 新增 Sorftime MCP API 完整文档
- 添加调研维度与接口对照表
- 优化报告结构

### v2.0 (2026-03-02)
- 重新设计分析框架
- 新增四大维度分析模型
- 改进报告输出格式

### v1.0 (初始版本)
- 基础竞品分析功能
- Sorftime MCP 集成

---

## 许可证

MIT License

---

## 联系方式

- Sorftime 官网: https://www.sorftime.com
- Claude Code 文档: https://claude.ai/code

---

*最后更新: 2026-03-02*
