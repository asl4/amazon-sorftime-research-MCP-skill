# Category-Selection Skill 变更日志

## [4.1.0] - 2026-03-03

### Bug 修复 - 一体化分析脚本

**背景**: 优化分析流程，解决数据处理、编码和报告生成的多个问题。

### 修复内容

#### 1. SSE 响应解析修复
- **问题**: `codecs.decode(text, 'unicode-escape')` 错误地二次解码已由 JSON 解码的中文字符
- **修复**: 移除不必要的 unicode-escape 解码，JSON 解析器已正确处理 Unicode 转义
- **影响**: 中文键名 (`Top100产品`, `类目统计报告`) 现在可以正确提取

#### 2. JSON 对象提取逻辑修复
- **问题**: 解析器查找最后一个 JSON 对象，但产品数据在第一个对象中
- **修复**: 改为查找第一个完整的 JSON 对象
- **影响**: 产品列表 (100个产品) 现在可以正确提取

#### 3. 数值格式化修复
- **问题**: 模板变量替换时对字符串值使用数字格式 (`,`) 导致错误
- **修复**: 添加 `_safe_float()` 和 `_safe_int()` 方法安全转换数值
- **影响**: 价格、销量等数值现在可以正确格式化显示

#### 4. Excel Font 作用域问题修复
- **问题**: `OpenpyxlFont` 在 `generate_excel()` 方法内导入，但辅助方法无法访问
- **修复**: 将 Font/PatternFill 类作为参数传递给辅助方法
- **影响**: Excel 报告现在可以正常生成

### 新增功能

#### 一体化分析脚本 (`analyze_category.py`)

一个命令完成完整的品类分析流程：

```bash
python .claude/skills/category-selection/scripts/analyze_category.py "品类名称" [站点] [数量]
```

**功能特点**:
- 自动搜索类目获取 nodeId
- 调用 category_report API
- 解析 SSE 响应和中文编码
- 计算五维评分
- 生成所有格式报告 (Markdown, Excel, HTML, CSV, JSON)

**报告输出结构**:
```
category-reports/
└── YYYY/MM/
    └── {品类名}_{站点}/
        ├── category_analysis_report.md
        ├── category_analysis_report.xlsx
        ├── dashboard.html
        └── data/
            ├── statistics.csv
            ├── products.csv
            ├── scores.csv
            └── raw_data.json
```

### 技术细节

#### SSE 解析流程
```python
# 旧代码 (错误):
decoded = codecs.decode(text, 'unicode-escape')  # 二次解码导致乱码

# 新代码 (正确):
decoded = text  # JSON 已自动解码 Unicode 转义
```

#### JSON 对象提取
```python
# 旧代码:
last_obj_start = decoded.rfind('{')  # 查找最后一个对象

# 新代码:
first_obj_start = decoded.find('{')  # 查找第一个对象 (包含产品数据)
```

### 支持的亚马逊站点
US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

### 已知限制
- 部分统计数据包含中文描述前缀 (如 "销量前的80%产品平均价格：")
- 模板中的部分变量 (如 `{{SCORE_建议}}`, `{{ANALYSIS_*}}`) 尚未实现

---

## [4.0.0] - 2026-03-03

### 重大重构 - MCP 风格化

**背景**: 原版本使用 Python 脚本绕过 MCP 服务器直接调用 API，与 MCP 设计理念不符。

### 变更内容

#### 删除的文件
- `scripts/sorftime_client.py` - 独立的 HTTP 客户端（绕过 MCP）
- `scripts/sorftime_parser.py` - SSE 响应解析器（MCP 已处理）
- `scripts/analyze.py` - 主分析脚本（由 SKILL.md 替代）
- `scripts/category_analysis_template.py` - 模板脚本
- `scripts/__pycache__/` - Python 缓存目录

#### 重写的文件
- `SKILL.md` - 完全重写为 MCP 风格，与 `amazon-analyse` 保持一致

### 架构变化

**旧架构** (v3.x):
```
Claude Code
    ↓
运行 Python 脚本 (analyze.py)
    ↓
SorftimeMCPClient (直接 HTTP 请求)
    ↓
Sorftime API (绕过 MCP)
    ↓
自定义解析器
```

**新架构** (v4.0):
```
Claude Code
    ↓
MCP 工具调用 (curl via Bash)
    ↓
Sorftime MCP 服务器
    ↓
SSE 响应
    ↓
Claude Code 解析
```

### 功能保持

以下功能保持不变，继续提供：

#### 必需工具
1. `category_name_search` - 搜索类目获取 nodeId
2. `category_report` - 获取类目 Top100 产品和统计数据
3. `product_detail` - 获取产品详情

#### 可选工具
4. `category_keywords` - 获取类目核心关键词
5. `products_1688` - 1688 采购成本分析

#### 保留的辅助工具
- `scripts/data_utils.py` - 数据处理工具（HHI、分组、评分计算等）
- `scripts/generate_excel_report.py` - Excel 报告生成（可选）

### SKILL.md 主要变化

| 章节 | v3.x | v4.0 |
|------|------|------|
| MCP 调用 | 描述 Python 脚本 | 描述 curl 调用 MCP |
| 数据解析 | 导入 Python 模块 | Claude Code 直接处理 |
| 工具参考 | 混合描述 | 统一 curl 格式 |
| 报告生成 | Python 脚本 | Write 工具 |

### 五维评分计算

评分逻辑保持不变：

| 维度 | 分值 | 数据来源 |
|------|------|----------|
| 市场规模 | 20分 | top100产品月销额 |
| 增长潜力 | 25分 | low_reviews_sales_volume_share |
| 竞争烈度 | 20分 | top3_brands_sales_volume_share |
| 进入壁垒 | 20分 | amazonOwned + low_reviews |
| 利润空间 | 15分 | average_price |

### 兼容性

- 与 `amazon-analyse` skill 保持一致的 MCP 调用风格
- 支持相同的亚马逊站点 (US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA)
- 使用相同的 Sorftime MCP 配置

### 迁移指南

如果用户之前使用 `analyze.py` 脚本，现在可以直接使用 `/category-select` 命令：

**旧方式**:
```bash
python .claude/skills/category-selection/scripts/analyze.py "Sofas" --site US --limit 20
```

**新方式**:
```
/category-select "Sofas" US --limit 20
```

---

## [3.0.0] - 2026-03-02

### 新增
- 添加 sorftime_parser.py 内置解析器
- 修复 Unicode 转义中文解析问题
- 修复 JSON 嵌套和控制字符问题
- 添加大文件处理方案

---

## [2.0.0] - 2026-03-01

### 初始版本
- 基础品类选品分析功能
- 五维评分模型
- Python 脚本驱动架构
