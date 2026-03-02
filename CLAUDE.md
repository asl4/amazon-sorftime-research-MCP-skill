# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an Amazon product analysis workspace configured with MCP (Model Context Protocol) servers and Claude skills. The primary purpose is competitive intelligence analysis for Amazon listings.

## MCP Servers

The `.mcp.json` file configures two MCP servers:

### Sorftime (`sorftime`)
- **Purpose**: Cross-border e-commerce data service for Amazon, TikTok, and 1688
- **Type**: `streamableHttp` (uses Server-Sent Events protocol)
- **Key Tools**:
  - `product_search` - Real-time Amazon product search
  - `product_detail` - Product details by ASIN
  - `product_report` - Product analysis report
  - `product_reviews` - User reviews (up to 100)
  - `product_trend` - Historical trend data
  - `product_traffic_terms` - Traffic keywords analysis
  - `competitor_product_keywords` - Competitor keyword exposure
  - `keyword_list` - Hot search keywords ranking
  - `category_tree` - Category structure
  - `category_report` - Category Top100 report
  - `keyword_detail` - Keyword detailed metrics
- **Primary Use Case**: Amazon competitor analysis, keyword research, market intelligence
- **Supported Sites**: Amazon 14 sites (US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA), TikTok 6 sites, 1688

### DuckDuckGo Search (`ducksearch`)
- General web search for research and context gathering

### Sorftime (`sorftime`)
- Cross-border e-commerce platform data service
- Supports Amazon 14 sites, TikTok 6 sites, and 1688 supply chain platform

## Skills Architecture

Skills are located in `.claude/skills/` and follow this structure:

```
skill-name/
├── SKILL.md          # Required: Metadata + instructions
├── scripts/          # Optional: Executable code
├── references/       # Optional: Documentation for context loading
└── assets/           # Optional: Files for output (templates, fonts, etc.)
```

### Current Skills

**amazon-analyse** (`/amazon-analyse` command)
- Performs comprehensive Amazon competitor listing analysis
- Uses Sorftime MCP for data collection (50+ e-commerce tools)
- Analyzes: product details, reviews, keywords, trends, competitor positioning
- Output: Structured competitive intelligence report with strategic recommendations

**skill-creator**
- Meta-skill for creating new Claude skills
- Includes helper scripts:
  - `init_skill.py` - Create new skill template
  - `package_skill.py` - Validate and package as .skill file
  - `quick_validate.py` - Quick validation check

### Creating New Skills

Use the skill-creator to add new capabilities:

```bash
# Initialize a new skill
.claude/skills/skill-creator/scripts/init_skill.py <skill-name> --path .claude/skills

# Package a completed skill
.claude/skills/skill-creator/scripts/package_skill.py <skill-folder>
```

### Skill Design Principles

1. **YAML frontmatter** is the trigger mechanism - include comprehensive `description` with WHEN to use
2. **Progressive disclosure** - Keep SKILL.md lean (<500 lines), move details to references/
3. **Scripts** for code that gets rewritten repeatedly or needs deterministic execution
4. **References** for documentation loaded as-needed (API docs, schemas, guides)
5. **Assets** for output files (templates, images, fonts)

## Amazon Analysis Workflow

The amazon-analyse skill implements a four-stage analysis using Sorftime MCP:

1. **Data Collection** - Get product details, reviews, trends, keywords via Sorftime MCP
2. **Keyword Analysis** - Traffic keywords, competitor keyword layout, exposure analysis
3. **Review Analysis** - Sentiment analysis, strengths/pain points extraction (up to 100 reviews)
4. **Market Intelligence** - Price trends, sales volume trends, competitive positioning

### Key Sorftime MCP Tools for Analysis
- `product_detail` + `product_report` - Comprehensive product data
- `product_reviews` - User sentiment analysis
- `product_traffic_terms` - Natural traffic keyword discovery
- `competitor_product_keywords` - Competitor keyword exposure analysis
- `product_trend` - Historical performance tracking
