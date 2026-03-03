#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品类选品数据处理工具
包含: HHI计算、价格/评分分组、新产品筛选、增长率计算等
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


class DataProcessor:
    """品类数据处理工具类"""

    @staticmethod
    def calculate_hhi(brand_shares: Dict[str, float]) -> float:
        """
        计算HHI指数 (Herfindahl-Hirschman Index)

        Args:
            brand_shares: {品牌名: 市场份额百分比}

        Returns:
            HHI指数
        """
        hhi = 0
        for share in brand_shares.values():
            hhi += share ** 2
        return round(hhi, 2)

    @staticmethod
    def calculate_cr(brand_shares: Dict[str, float], top_n: int = 3) -> float:
        """
        计算CRn集中度 (Concentration Ratio)

        Args:
            brand_shares: {品牌名: 市场份额百分比}
            top_n: 前n个品牌

        Returns:
            CRn百分比
        """
        # 按市场份额降序排序
        sorted_brands = sorted(brand_shares.items(), key=lambda x: x[1], reverse=True)
        top_shares = sorted_brands[:top_n]
        cr = sum(share for _, share in top_shares)
        return round(cr, 2)

    @staticmethod
    def group_by_price_range(products: List[Dict], ranges: List[Dict] = None) -> List[Dict]:
        """
        按价格区间分组产品

        Args:
            products: 产品列表
            ranges: 自定义价格区间，默认为5个区间

        Returns:
            分组结果
        """
        if ranges is None:
            ranges = [
                {"name": "超低价", "min": 0, "max": 20},
                {"name": "低价", "min": 20, "max": 50},
                {"name": "中价", "min": 50, "max": 100},
                {"name": "高价", "min": 100, "max": 200},
                {"name": "超高价", "min": 200, "max": float('inf')},
            ]

        result = []
        for range_def in ranges:
            group = {
                "range": f"{range_def['name']} (${range_def['min']}-{range_def['max'] if range_def['max'] != float('inf') else '+'})",
                "count": 0,
                "sales": 0,
                "revenue": 0,
                "ratings": [],
                "products": []
            }

            for product in products:
                price = product.get("price", 0)
                if range_def['min'] <= price < range_def['max']:
                    group["count"] += 1
                    group["sales"] += product.get("monthly_sales", 0)
                    group["revenue"] += product.get("monthly_revenue", 0)
                    if product.get("rating"):
                        group["ratings"].append(product["rating"])
                    group["products"].append(product)

            # 计算占比和平均评分
            total_products = len(products)
            total_revenue = sum(p.get("monthly_revenue", 0) for p in products)

            group["percentage"] = round(group["count"] / total_products * 100, 1) if total_products > 0 else 0
            group["avg_rating"] = round(sum(group["ratings"]) / len(group["ratings"]), 2) if group["ratings"] else 0

            result.append(group)

        return result

    @staticmethod
    def group_by_rating_range(products: List[Dict], ranges: List[Dict] = None) -> List[Dict]:
        """
        按评分区间分组产品

        Args:
            products: 产品列表
            ranges: 自定义评分区间，默认为5个区间

        Returns:
            分组结果
        """
        if ranges is None:
            ranges = [
                {"name": "低分", "min": 0, "max": 3.5},
                {"name": "中低分", "min": 3.5, "max": 4.0},
                {"name": "中等", "min": 4.0, "max": 4.3},
                {"name": "中高分", "min": 4.3, "max": 4.7},
                {"name": "高分", "min": 4.7, "max": 5.0},
            ]

        result = []
        for range_def in ranges:
            group = {
                "range": f"{range_def['name']} ({range_def['min']}-{range_def['max']})",
                "count": 0,
                "sales": 0,
                "sales_percentage": 0
            }

            for product in products:
                rating = product.get("rating", 0)
                if range_def['min'] <= rating < range_def['max']:
                    group["count"] += 1
                    group["sales"] += product.get("monthly_sales", 0)

            # 计算占比
            total_sales = sum(p.get("monthly_sales", 0) for p in products)
            group["sales_percentage"] = round(group["sales"] / total_sales * 100, 1) if total_sales > 0 else 0
            group["percentage"] = round(group["count"] / len(products) * 100, 1) if products else 0

            result.append(group)

        return result

    @staticmethod
    def filter_new_products(products: List[Dict], days_threshold: int = 90) -> List[Dict]:
        """
        筛选新产品 (上架时间小于指定天数)

        Args:
            products: 产品列表
            days_threshold: 天数阈值，默认90天(3个月)

        Returns:
            新产品列表
        """
        today = datetime.now()
        threshold_date = today - timedelta(days=days_threshold)

        new_products = []
        for product in products:
            days_online = product.get("days_online", 0)
            if days_online and days_online <= days_threshold:
                new_products.append(product)

        return new_products

    @staticmethod
    def analyze_brand_distribution(products: List[Dict]) -> List[Dict]:
        """
        分析品牌分布

        Args:
            products: 产品列表

        Returns:
            品牌分析列表，按市场份额降序排序
        """
        brand_data = {}

        for product in products:
            brand = product.get("brand", "Unknown")
            if brand not in brand_data:
                brand_data[brand] = {
                    "brand": brand,
                    "product_count": 0,
                    "monthly_sales": 0,
                    "monthly_revenue": 0,
                    "ratings": []
                }

            brand_data[brand]["product_count"] += 1
            brand_data[brand]["monthly_sales"] += product.get("monthly_sales", 0)
            brand_data[brand]["monthly_revenue"] += product.get("monthly_revenue", 0)
            if product.get("rating"):
                brand_data[brand]["ratings"].append(product["rating"])

        # 计算总销额
        total_revenue = sum(b["monthly_revenue"] for b in brand_data.values())

        # 计算市场份额和平均评分
        for brand in brand_data.values():
            brand["market_share"] = round(brand["monthly_revenue"] / total_revenue * 100, 2) if total_revenue > 0 else 0
            brand["avg_rating"] = round(sum(brand["ratings"]) / len(brand["ratings"]), 2) if brand["ratings"] else 0

        # 按市场份额降序排序
        sorted_brands = sorted(brand_data.values(), key=lambda x: x["market_share"], reverse=True)

        return sorted_brands

    @staticmethod
    def analyze_seller_distribution(products: List[Dict]) -> Dict[str, Dict]:
        """
        分析卖家来源分布

        Args:
            products: 产品列表

        Returns:
            按来源地分组的统计数据
        """
        source_data = {
            "中国": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "美国": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "品牌": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "其他": {"seller_count": set(), "product_count": 0, "revenue": 0}
        }

        for product in products:
            seller = product.get("seller", "")
            source = product.get("seller_source", "其他")

            if source in source_data:
                source_data[source]["seller_count"].add(seller)
                source_data[source]["product_count"] += 1
                source_data[source]["revenue"] += product.get("monthly_revenue", 0)

        # 转换为列表格式
        result = []
        total_revenue = sum(s["revenue"] for s in source_data.values())

        for source, data in source_data.items():
            result.append({
                "source": source,
                "seller_count": len(data["seller_count"]),
                "product_count": data["product_count"],
                "revenue": data["revenue"],
                "percentage": round(data["revenue"] / total_revenue * 100, 1) if total_revenue > 0 else 0
            })

        # 按销额降序排序
        result.sort(key=lambda x: x["revenue"], reverse=True)

        return result

    @staticmethod
    def calculate_growth_rate(trend_data: List[Dict], period_months: int = 3) -> Dict[str, float]:
        """
        计算增长率和环比

        Args:
            trend_data: 趋势数据列表，每个元素包含 {date, value}
            period_months: 对比周期月数

        Returns:
            {同比增长率, 环比增长率}
        """
        if len(trend_data) < period_months + 1:
            return {"yoy": 0, "mom": 0}

        current_avg = sum(d["value"] for d in trend_data[-period_months:]) / period_months
        previous_avg = sum(d["value"] for d in trend_data[-(period_months*2+1):-period_months]) / period_months

        yoy = round((current_avg - previous_avg) / previous_avg * 100, 2) if previous_avg > 0 else 0

        # 环比 (上个月 vs 这个月)
        if len(trend_data) >= 2:
            last_month = trend_data[-1]["value"]
            prev_month = trend_data[-2]["value"]
            mom = round((last_month - prev_month) / prev_month * 100, 2) if prev_month > 0 else 0
        else:
            mom = 0

        return {"yoy": yoy, "mom": mom}

    @staticmethod
    def calculate_five_dimension_score(data: Dict) -> Dict[str, float]:
        """
        计算五维评分

        Args:
            data: 包含所有市场数据的字典

        Returns:
            五维评分结果
        """
        scores = {}

        # 1. 市场规模 (20分)
        total_sales = data.get("total_monthly_sales", 0)
        if total_sales > 10_000_000:
            scores["market_size"] = 18
        elif total_sales > 5_000_000:
            scores["market_size"] = 15
        elif total_sales > 1_000_000:
            scores["market_size"] = 12
        elif total_sales > 500_000:
            scores["market_size"] = 8
        else:
            scores["market_size"] = 4

        # 2. 增长潜力 (25分) - 基于同比增长率
        growth_rate = data.get("yoy_growth_rate", 0)
        if growth_rate > 50:
            scores["growth_potential"] = 22
        elif growth_rate > 30:
            scores["growth_potential"] = 18
        elif growth_rate > 10:
            scores["growth_potential"] = 14
        elif growth_rate > 0:
            scores["growth_potential"] = 8
        else:
            scores["growth_potential"] = 3

        # 3. 竞争烈度 (20分) - HHI 和 CR3 综合评估
        hhi = data.get("hhi", 0)
        cr3 = data.get("cr3", 0)

        if hhi < 1000 and cr3 < 30:
            scores["competition"] = 18
        elif hhi < 1800 and cr3 < 50:
            scores["competition"] = 13
        else:
            scores["competition"] = 6

        # 4. 进入壁垒 (20分)
        avg_reviews = data.get("avg_review_count", 0)
        amazon_own_share = data.get("amazon_own_share", 0)
        new_product_share = data.get("new_product_share", 0)

        entry_score = 20  # 起始分

        # 评论数壁垒 (0-7分扣分)
        if avg_reviews > 1000:
            entry_score -= 7
        elif avg_reviews > 500:
            entry_score -= 4
        elif avg_reviews < 500:
            entry_score -= 0

        # 亚马逊自营挤压 (0-7分扣分)
        if amazon_own_share > 40:
            entry_score -= 7
        elif amazon_own_share > 20:
            entry_score -= 4

        # 新品空间 (反向扣分)
        if new_product_share > 15:
            entry_score -= 0  # 低壁垒
        elif new_product_share > 5:
            entry_score -= 3
        else:
            entry_score -= 7

        scores["entry_barrier"] = max(0, entry_score)

        # 5. 利润空间 (15分)
        margin = data.get("estimated_margin", 0)
        if margin > 40:
            scores["profit_margin"] = 13
        elif margin > 30:
            scores["profit_margin"] = 10
        elif margin > 20:
            scores["profit_margin"] = 6
        else:
            scores["profit_margin"] = 3

        # 计算总分
        scores["total"] = (
            scores["market_size"] +
            scores["growth_potential"] +
            scores["competition"] +
            scores["entry_barrier"] +
            scores["profit_margin"]
        )

        return scores

    @staticmethod
    def prepare_html_data(data: Dict) -> Dict:
        """
        准备HTML报告所需的数据格式

        Args:
            data: 原始数据

        Returns:
            HTML模板变量字典
        """
        return {
            # 基础信息
            "CATEGORY_NAME": data.get("category_name", ""),
            "SITE": data.get("site", "US"),
            "DATA_DATE": datetime.now().strftime("%Y-%m-%d"),

            # 五维评分
            "MARKET_SIZE_SCORE": data.get("scores", {}).get("market_size", 0),
            "MARKET_SIZE_PERCENT": int(data.get("scores", {}).get("market_size", 0) / 20 * 100),
            "GROWTH_POTENTIAL_SCORE": data.get("scores", {}).get("growth_potential", 0),
            "GROWTH_POTENTIAL_PERCENT": int(data.get("scores", {}).get("growth_potential", 0) / 25 * 100),
            "COMPETITION_SCORE": data.get("scores", {}).get("competition", 0),
            "COMPETITION_PERCENT": int(data.get("scores", {}).get("competition", 0) / 20 * 100),
            "ENTRY_BARRIER_SCORE": data.get("scores", {}).get("entry_barrier", 0),
            "ENTRY_BARRIER_PERCENT": int(data.get("scores", {}).get("entry_barrier", 0) / 20 * 100),
            "PROFIT_MARGIN_SCORE": data.get("scores", {}).get("profit_margin", 0),
            "PROFIT_MARGIN_PERCENT": int(data.get("scores", {}).get("profit_margin", 0) / 15 * 100),
            "TOTAL_SCORE": data.get("scores", {}).get("total", 0),
            "RATING": data.get("rating", ""),
            "RECOMMENDATION": data.get("recommendation", ""),

            # KPI
            "TOTAL_PRODUCTS": data.get("total_products", 0),
            "AVG_PRICE": f"${data.get("avg_price", 0):.2f}",
            "AVG_SALES": f"{data.get("avg_sales", 0):.0f}",
            "AVG_RATING": f"{data.get("avg_rating", 0):.2f}",
            "TOTAL_SALES": f"${data.get("total_sales", 0):,.0f}",
            "CR3": f"{data.get("cr3", 0):.2f}",

            # 趋势数据 (需要JSON序列化)
            "SALES_TREND_DATA": json.dumps(data.get("sales_trend", {"dates": [], "sales": []})),
            "PRICE_TREND_DATA": json.dumps(data.get("price_trend", {"dates": [], "prices": []})),
            "PRICE_DIST_DATA": json.dumps(data.get("price_dist", [])),
            "RATING_DIST_DATA": json.dumps(data.get("rating_dist", {"ranges": [], "counts": []})),
            "BRAND_SHARE_DATA": json.dumps(data.get("brand_share", {"brands": [], "shares": []})),
            "SELLER_SOURCE_DATA": json.dumps(data.get("seller_source", [])),
            "BRAND_RATING_TREND_DATA": json.dumps(data.get("brand_rating_trend", {"brands": [], "dates": [], "data": {}})),
            "TOP50_PRODUCTS": json.dumps(data.get("top50_products", [])),

            # 关键发现
            "CONCENTRATION_LEVEL": data.get("concentration_level", ""),
            "HHI": f"{data.get('hhi', 0):.2f}",
            "CR3_RAW": f"{data.get('cr3_raw', 0)}",
            "CONCLUSION_CR3": data.get("conclusion_cr3", ""),
            "BRAND_COUNT": data.get("brand_count", 0),
            "BRAND_DIVERSITY": data.get("brand_diversity", ""),
            "NEW_PRODUCT_PERCENT": f"{data.get('new_product_percent', 0)}%",
            "NEW_PRODUCT_CONCLUSION": data.get("new_product_conclusion", ""),
            "SELLER_DISTRIBUTION": data.get("seller_distribution", ""),
            "COMPETITION_CONCLUSION": data.get("competition_conclusion", ""),
            "STRATEGY": data.get("strategy", ""),
            "GENERATED_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# 使用示例
if __name__ == "__main__":
    # 示例产品数据
    sample_products = [
        {"asin": "B001", "brand": "Sony", "price": 150, "rating": 4.5, "monthly_sales": 1000,
         "monthly_revenue": 150000, "seller": "Amazon", "seller_source": "品牌", "days_online": 45},
        {"asin": "B002", "brand": "Samsung", "price": 120, "rating": 4.2, "monthly_sales": 800,
         "monthly_revenue": 96000, "seller": "Seller1", "seller_source": "中国", "days_online": 200},
        {"asin": "B003", "brand": "LG", "price": 180, "rating": 4.6, "monthly_sales": 500,
         "monthly_revenue": 90000, "seller": "Seller2", "seller_source": "韩国", "days_online": 30},
    ]

    processor = DataProcessor()

    # 品牌分布分析
    brands = processor.analyze_brand_distribution(sample_products)
    print("品牌分布:", brands)

    # 价格分组
    price_groups = processor.group_by_price_range(sample_products)
    print("价格分组:", price_groups)

    # 评分分组
    rating_groups = processor.group_by_rating_range(sample_products)
    print("评分分组:", rating_groups)

    # 新产品筛选
    new_products = processor.filter_new_products(sample_products)
    print("新产品:", new_products)
