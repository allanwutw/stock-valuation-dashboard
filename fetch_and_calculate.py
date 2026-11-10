import yfinance as yf
import json
import os

TW_NAME_MAP = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2308.TW": "台達電", "2881.TW": "富邦金",
    "2882.TW": "國泰金", "2412.TW": "中華電", "2891.TW": "中信金", "3711.TW": "日月光投控", "1301.TW": "台塑",
    "2002.TW": "中鋼", "2886.TW": "兆豐金", "5880.TW": "合庫金", "1216.TW": "統一", "2912.TW": "統一超",
    "2884.TW": "玉山金", "5871.TW": "中租-KY", "3034.TW": "聯詠", "2357.TW": "華碩", "2382.TW": "廣達",
    "3231.TW": "緯創", "2211.TW": "長榮鋼", "1101.TW": "台泥", "1227.TW": "佳格", "1402.TW": "遠東新",
    "2603.TW": "長榮", "2609.TW": "陽明", "2615.TW": "萬海", "2880.TW": "華南金", "2883.TW": "開發金",
    "2885.TW": "元大金", "2887.TW": "台新金", "2892.TW": "第一金", "3045.TW": "台灣大哥大", "3702.TW": "大聯大",
    "4904.TW": "遠傳", "5876.TW": "上海商銀", "6505.TW": "台塑化", "9910.TW": "豐泰", "2345.TW": "智邦",
    "2379.TW": "瑞昱", "3008.TW": "大立光", "5347.TW": "世界", "6669.TW": "緯穎", "8046.TW": "南電",
    "2408.TW": "南亞科", "3037.TW": "欣興", "3661.TW": "世芯-KY", "6415.TW": "矽力-KY"
}

TICKERS = list(TW_NAME_MAP.keys()) + [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", 
    "BRK-B", "UNH", "JNJ", "JPM", "V", "XOM", "PG", "MA",
    "COST", "HD", "AVGO", "LLY", "NFLX", "AMD", "ABBV", "CRM",
    "BAC", "CVX", "MRK", "PEP", "ADBE", "TMO", "ACN",
    "MCD", "CSCO", "ABT", "LIN", "WMT", "DHR", "DIS", "VZ",
    "INTC", "QCOM", "TXN", "AMGN", "IBM", "NOW", "PFE", "INTU"
]

def calculate_dcf(fcf, growth_rate, wacc=0.09, years=5, terminal_growth=0.02):
    if not fcf or fcf <= 0:
        return None
    pv_sum = 0
    curr_fcf = fcf
    for t in range(1, years + 1):
        curr_fcf *= (1 + min(growth_rate, 0.12)) # 嚴格限制現金流成長率上限
        pv_sum += curr_fcf / ((1 + wacc) ** t)
    
    terminal_val = (curr_fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
    pv_terminal = terminal_val / ((1 + wacc) ** years)
    return round(pv_sum + pv_terminal, 2)

def calculate_ddm(dividend, growth_rate=0.03, required_return=0.08):
    if not dividend or dividend <= 0 or required_return <= growth_rate:
        return None
    d1 = dividend * (1 + growth_rate)
    return round(d1 / (required_return - growth_rate), 2)

def analyze_stock(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    if not current_price or current_price <= 0:
        raise ValueError("無效的當前股價")

    eps = info.get('trailingEps', 0)
    forward_eps = info.get('forwardEps', eps)
    pe_ratio = info.get('trailingPE', 15)
    pb_ratio = info.get('priceToBook', 1.5)
    book_value = info.get('bookValue', 0)
    dividend_rate = info.get('dividendRate', 0)
    ev_to_sales = info.get('enterpriseToRevenue', 3.0)
    revenue_per_share = info.get('revenuePerShare', 0)
    sector = info.get('sector', '一般產業')
    
    # 取得原始分析師目標價，並進行極端值防禦（夾擠在現價 0.5 ~ 1.5 倍之間）
    raw_analyst_target = info.get('targetMeanPrice')
    analyst_target = None
    if raw_analyst_target and raw_analyst_target > 0:
        analyst_target = max(current_price * 0.5, min(raw_analyst_target, current_price * 1.5))
    
    sector_map = {
        "Technology": "科技半導體",
        "Financial Services": "金融保險",
        "Consumer Cyclical": "非必需消費",
        "Healthcare": "醫療保健",
        "Communication Services": "通訊服務",
        "Industrials": "工業製造",
        "Consumer Defensive": "必需消費",
        "Energy": "能源原物料",
        "Utilities": "公用事業",
        "Real Estate": "房地產"
    }
    category_name = sector_map.get(sector, "綜合產業")

    if ticker_symbol in TW_NAME_MAP:
        clean_symbol = ticker_symbol.replace(".TW", "")
        stock_name = TW_NAME_MAP[ticker_symbol]
    else:
        clean_symbol = ticker_symbol
        stock_name = info.get('shortName', ticker_symbol) or ticker_symbol

    growth_rate = 0.06
    if eps > 0 and forward_eps > eps:
        growth_rate = min((forward_eps - eps) / eps, 0.15)
    
    # 各模型計算與合理區間過濾
    pe_fair = round(eps * min(pe_ratio, 25), 2) if eps and 0 < pe_ratio < 35 else None
    pb_fair = round(book_value * min(pb_ratio, 3.5), 2) if book_value and 0 < pb_ratio < 5 else None
    dcf_fair = calculate_dcf(eps, growth_rate) if eps > 0 else None
    ddm_fair = calculate_ddm(dividend_rate) if dividend_rate and dividend_rate > 0 else None
    ev_sales_fair = round(revenue_per_share * min(ev_to_sales, 3.5), 2) if revenue_per_share and revenue_per_share > 0 else None

    # === 精細化產業權重對應 ===
    if sector == "Financial Services":
        weights = { "ddm": 0.5, "pb": 0.3, "analyst": 0.2, "pe": 0.0, "dcf": 0.0, "ev_sales": 0.0 }
    elif sector == "Utilities" or sector == "Communication Services":
        weights = { "ddm": 0.4, "dcf": 0.3, "analyst": 0.3, "pe": 0.0, "pb": 0.0, "ev_sales": 0.0 }
    elif sector == "Technology":
        weights = { "dcf": 0.4, "pe": 0.3, "analyst": 0.3, "pb": 0.0, "ddm": 0.0, "ev_sales": 0.0 }
    elif sector == "Energy" or sector == "Industrials":
        weights = { "pb": 0.4, "analyst": 0.4, "pe": 0.2, "dcf": 0.0, "ddm": 0.0, "ev_sales": 0.0 }
    else:
        weights = { "dcf": 0.35, "pe": 0.35, "analyst": 0.3, "pb": 0.0, "ddm": 0.0, "ev_sales": 0.0 }

    models_dict = {
        "dcf": ("DCF模型", dcf_fair),
        "pe": ("P/E本益比", pe_fair),
        "pb": ("P/B淨值比", pb_fair),
        "ddm": ("DDM股利", ddm_fair),
        "ev_sales": ("EV/Sales", ev_sales_fair),
        "analyst": ("分析師目標價", analyst_target)
    }

    weighted_sum = 0
    total_weight = 0
    active_models_list = []

    for key, weight in weights.items():
        name, val = models_dict[key]
        if val is not None and weight > 0:
            # 單一模型極端值夾擠（限制在現價 0.5 倍至 2.0 倍之間）
            val = max(current_price * 0.5, min(val, current_price * 2.0))
            weighted_sum += val * weight
            total_weight += weight
            active_models_list.append(name)

    if total_weight > 0:
        fair_value = round(weighted_sum / total_weight, 2)
    else:
        valid_vals = [v[1] for v in models_dict.values() if v[1] is not None]
        fair_value = round(sum(valid_vals) / len(valid_vals), 2) if valid_vals else current_price

    # 最終整體公允價強效夾擠：限制在現價的 0.6 倍到 1.6 倍之間，確保潛在報酬率合理
    fair_value = max(round(current_price * 0.6, 2), min(fair_value, round(current_price * 1.6, 2)))
    upside = round(((fair_value - current_price) / current_price) * 100, 2)

    confidence = "高"
    if not analyst_target or total_weight < 0.6 or eps <= 0:
        confidence = "低"
    elif total_weight < 0.8:
        confidence = "中"

    models_summary = " + ".join(active_models_list) if active_models_list else "綜合評估"

    return {
        "symbol": clean_symbol,
        "raw_ticker": ticker_symbol,
        "name": stock_name,
        "sector": category_name,
        "current_price": current_price,
        "fair_value": fair_value,
        "upside_percent": upside,
        "confidence": confidence,
        "models_used": models_summary,
        "models": {
            "pe_multiples": pe_fair,
            "pb_multiples": pb_fair,
            "dcf_5yr": dcf_fair,
            "ddm_model": ddm_fair,
            "ev_sales": ev_sales_fair,
            "analyst_target": analyst_target
        }
    }

def main():
    results = []
    seen = set()
    for t in TICKERS:
        if t in seen:
            continue
        seen.add(t)
        try:
            data = analyze_stock(t)
            results.append(data)
            print(f"成功計算 {t}")
        except Exception as e:
            print(f"計算 {t} 失敗: {e}")

    with open('valuation_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
