import yfinance as yf
import json
import os

TW_NAME_MAP = {
    "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2308.TW": "台達電", "2881.TW": "富邦金",
    "2882.TW": "國泰金", "2412.TW": "中華電", "2891.TW": "中信金", "3711.TW": "日月光投控", "1301.TW": "台塑",
    "2002.TW": "中鋼", "2886.TW": "兆豐金", "5880.TW": "合庫金", "1216.TW": "統一", "2912.TW": "統一超",
    "2884.TW": "玉山金", "5871.TW": "中租-KY", "3034.TW": "聯詠", "2357.TW": "華碩", "2382.TW": "廣達",
    "3231.TW": "緯創", "2211.TW": "長榮鋼", "1101.TW": "台泥", "1227.TW": "佳格", "1402.TW": "遠東新",
    "2603.TW": "長榮", "2609.TW": "陽明", "2615.TW": "萬海", "2880.TW": "華南金", "2883.TW": "凱基金",
    "2885.TW": "元大金", "2887.TW": "台新新光金", "2892.TW": "第一金", "3045.TW": "台灣大", "3702.TW": "大聯大",
    "4904.TW": "遠傳", "5876.TW": "上海商銀", "6505.TW": "台塑化", "9910.TW": "豐泰", "2345.TW": "智邦",
    "2379.TW": "瑞昱", "3008.TW": "大立光", "5347.TW": "世界", "6669.TW": "緯穎", "8046.TW": "南電",
    "2408.TW": "南亞科", "3037.TW": "欣興", "3661.TW": "世芯-KY", "6415.TW": "矽力-KY",
    "1303.TW": "南亞", "2303.TW": "聯電", "2383.TW": "台光電", "3017.TW": "奇鋐", "2327.TW": "國巨*",
    "2890.TW": "永豐金", "3443.TW": "創意", "2360.TW": "致茂", "2301.TW": "光寶科", "3653.TW": "健策",
    "6446.TW": "藥華藥", "2059.TW": "川湖", "2344.TW": "華邦電", "2368.TW": "金像電", "4958.TW": "臻鼎-KY",
    "3665.TW": "貿聯-KY", "2395.TW": "研華", "2449.TW": "京元電子", "7769.TW": "鴻勁"
}

# 核心成分股權重設定（涵蓋前大權值股，確保覆蓋率與計算精準度）
ETF_HOLDINGS_CONFIG = {
    "0050.TW": {
        "symbol": "0050",
        "name": "元大台灣50",
        "sector": "ETF - 市值型",
        "holdings": [
            ("2330.TW", 58.92), ("2454.TW", 6.42), ("2317.TW", 2.99), ("2308.TW", 2.27), ("3711.TW", 2.01),
            ("2891.TW", 1.44), ("2881.TW", 1.38), ("1303.TW", 1.38), ("2303.TW", 1.20), ("2882.TW", 1.16),
            ("2383.TW", 1.11), ("3037.TW", 0.97), ("3017.TW", 0.96), ("2887.TW", 0.96), ("2885.TW", 0.82),
            ("2382.TW", 0.78), ("2345.TW", 0.78), ("2884.TW", 0.75), ("2412.TW", 0.70), ("2886.TW", 0.69),
            ("2357.TW", 0.63), ("2327.TW", 0.61), ("2890.TW", 0.61), ("2883.TW", 0.59), ("3443.TW", 0.59),
            ("3231.TW", 0.54), ("6669.TW", 0.51), ("2892.TW", 0.51), ("2880.TW", 0.50), ("2360.TW", 0.47),
            ("3008.TW", 0.46), ("2408.TW", 0.46), ("2301.TW", 0.45), ("3653.TW", 0.44), ("6446.TW", 0.43),
            ("1216.TW", 0.43), ("2059.TW", 0.40), ("2344.TW", 0.37), ("2368.TW", 0.34), ("4958.TW", 0.33),
            ("5880.TW", 0.33), ("3665.TW", 0.31), ("2603.TW", 0.31), ("2395.TW", 0.30), ("2449.TW", 0.25),
            ("7769.TW", 0.22), ("8046.TW", 0.22), ("4904.TW", 0.21), ("3045.TW", 0.20), ("6505.TW", 0.11)
        ]
    },
    "009800.TW": {
        "symbol": "009800",
        "name": "中信NASDAQ",
        "sector": "ETF - 美股科技",
        "holdings": [
            ("AAPL", 8.9), ("NVDA", 8.5), ("MSFT", 8.1), ("AMZN", 5.6), ("AVGO", 4.8),
            ("META", 4.6), ("TSLA", 3.8), ("GOOGL", 4.9), ("COST", 2.7), ("NFLX", 2.4),
            ("AMD", 1.8), ("PEP", 1.5), ("LIN", 1.5), ("CSCO", 1.5), ("TMUS", 1.5),
            ("ADBE", 1.4), ("QCOM", 1.3), ("TXN", 1.2), ("INTU", 1.2), ("ISRG", 1.2),
            ("AMAT", 1.1), ("AMGN", 1.1), ("BKNG", 1.0), ("MU", 0.9), ("LRCX", 0.8)
        ]
    },
    "009815.TW": {
        "symbol": "009815",
        "name": "大華美國MAG7+",
        "sector": "ETF - 美股科技",
        "holdings": [
            ("AAPL", 16.55), ("NVDA", 12.66), ("MSFT", 12.04), ("GOOGL", 9.79), ("AMZN", 8.30),
            ("TSM", 5.44), ("TSLA", 4.87), ("META", 4.69), ("AVGO", 4.59), ("MU", 2.50),
            ("AMD", 2.31), ("ASML", 1.65), ("PLTR", 1.11), ("CSCO", 1.08), ("PANW", 0.90),
            ("AMAT", 0.86), ("TXN", 0.83), ("LRCX", 0.82), ("INTC", 0.77), ("NFLX", 0.75),
            ("IBM", 0.68), ("DIS", 0.65), ("CRWD", 0.65), ("SAP", 0.62), ("ORCL", 0.61),
            ("KLAC", 0.60), ("ADI", 0.58), ("QCOM", 0.56), ("CRM", 0.46), ("BKNG", 0.35)
        ]
    },
    "00830.TW": {
        "symbol": "00830",
        "name": "國泰費城半導體",
        "sector": "ETF - 半導體",
        "holdings": [
            ("NVDA", 11.5), ("AVGO", 9.8), ("AMD", 7.6), ("QCOM", 6.8), ("TXN", 6.2),
            ("AMAT", 5.4), ("MU", 4.8), ("LRCX", 4.6), ("ADI", 4.5), ("KLAC", 4.3),
            ("INTC", 4.1), ("TSM", 4.0), ("ASML", 3.6), ("MRVL", 3.5), ("NXPI", 3.4),
            ("MCHP", 2.9), ("ON", 2.3), ("MPWR", 2.2), ("TER", 1.6), ("SWKS", 1.4)
        ]
    },
    "SPYM": {
        "symbol": "SPYM",
        "name": "SPDR S&P 500 迷你 ETF",
        "sector": "ETF - 美股大盤",
        "holdings": [
            ("AAPL", 7.1), ("NVDA", 6.8), ("MSFT", 6.3), ("AMZN", 3.8), ("META", 2.6),
            ("GOOGL", 3.7), ("TSLA", 1.9), ("BRK-B", 1.7), ("AVGO", 1.7), ("JPM", 1.4),
            ("LLY", 1.4), ("UNH", 1.2), ("XOM", 1.1), ("V", 1.1), ("MA", 0.9),
            ("COST", 0.9), ("HD", 0.8), ("PG", 0.8), ("WMT", 0.8), ("JNJ", 0.8),
            ("NFLX", 0.7), ("BAC", 0.7), ("ABBV", 0.7), ("CRM", 0.7), ("CVX", 0.6)
        ]
    },
    "QQQM": {
        "symbol": "QQQM",
        "name": "Invesco NASDAQ 100",
        "sector": "ETF - 美股科技",
        "holdings": [
            ("AAPL", 8.9), ("NVDA", 8.5), ("MSFT", 8.1), ("AMZN", 5.6), ("AVGO", 4.8),
            ("META", 4.6), ("TSLA", 3.8), ("GOOGL", 4.9), ("COST", 2.7), ("NFLX", 2.4),
            ("AMD", 1.8), ("PEP", 1.5), ("LIN", 1.5), ("CSCO", 1.5), ("TMUS", 1.5),
            ("ADBE", 1.4), ("QCOM", 1.3), ("TXN", 1.2), ("INTU", 1.2), ("ISRG", 1.2),
            ("AMAT", 1.1), ("AMGN", 1.1), ("BKNG", 1.0), ("MU", 0.9), ("LRCX", 0.8)
        ]
    },
    "SOXX": {
        "symbol": "SOXX",
        "name": "iShares 半導體 ETF",
        "sector": "ETF - 半導體",
        "holdings": [
            ("NVDA", 9.2), ("AVGO", 8.8), ("AMD", 7.4), ("QCOM", 6.5), ("TXN", 6.1),
            ("AMAT", 5.1), ("MU", 4.7), ("LRCX", 4.5), ("ADI", 4.4), ("KLAC", 4.2),
            ("INTC", 4.0), ("TSM", 4.0), ("MRVL", 3.7), ("NXPI", 3.5), ("ASML", 3.4),
            ("MCHP", 3.0), ("ON", 2.4), ("MPWR", 2.3), ("TER", 1.7), ("SWKS", 1.5)
        ]
    }
}

# 自動從所有 ETF 成分股提取美股代號，並與核心美股清單合併（避免漏抓成分股）
US_BASE_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", 
    "BRK-B", "UNH", "JNJ", "JPM", "V", "XOM", "PG", "MA",
    "COST", "HD", "AVGO", "LLY", "NFLX", "AMD", "ABBV", "CRM",
    "BAC", "CVX", "MRK", "PEP", "ADBE", "TMO", "ACN",
    "MCD", "CSCO", "ABT", "LIN", "WMT", "DHR", "DIS", "VZ",
    "INTC", "QCOM", "TXN", "AMGN", "IBM", "NOW", "PFE", "INTU",
    "TMUS", "ISRG", "AMAT", "BKNG", "MU", "LRCX", "ADI", "KLAC",
    "TSM", "ASML", "MRVL", "NXPI", "MCHP", "ON", "MPWR", "TER", "SWKS"
]

ETF_COMP_TICKERS = [
    comp for cfg in ETF_HOLDINGS_CONFIG.values()
    for comp, _ in cfg["holdings"]
    if not comp.endswith(".TW")
]

TICKERS = list(dict.fromkeys(list(TW_NAME_MAP.keys()) + US_BASE_TICKERS + ETF_COMP_TICKERS))

def calculate_dcf(fcf, growth_rate, wacc=0.09, years=5, terminal_growth=0.02):
    if not fcf or fcf <= 0:
        return None
    pv_sum = 0
    curr_fcf = fcf
    for t in range(1, years + 1):
        curr_fcf *= (1 + min(growth_rate, 0.12))
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
    
    pe_fair = round(eps * min(pe_ratio, 25), 2) if eps and 0 < pe_ratio < 35 else None
    pb_fair = round(book_value * min(pb_ratio, 3.5), 2) if book_value and 0 < pb_ratio < 5 else None
    dcf_fair = calculate_dcf(eps, growth_rate) if eps > 0 else None
    ddm_fair = calculate_ddm(dividend_rate) if dividend_rate and dividend_rate > 0 else None
    ev_sales_fair = round(revenue_per_share * min(ev_to_sales, 3.5), 2) if revenue_per_share and revenue_per_share > 0 else None

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
            val = max(current_price * 0.5, min(val, current_price * 2.0))
            weighted_sum += val * weight
            total_weight += weight
            active_models_list.append(name)

    if total_weight > 0:
        fair_value = round(weighted_sum / total_weight, 2)
    else:
        valid_vals = [v[1] for v in models_dict.values() if v[1] is not None]
        fair_value = round(sum(valid_vals) / len(valid_vals), 2) if valid_vals else current_price

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

def analyze_etf(etf_ticker, config, stock_results_map):
    etf = yf.Ticker(etf_ticker)
    info = etf.info
    
    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
    if not current_price or current_price <= 0:
        hist = etf.history(period="5d")
        if not hist.empty:
            current_price = round(float(hist['Close'].iloc[-1]), 2)
    if not current_price or current_price <= 0:
        raise ValueError("無法取得 ETF 當前股價")

    weighted_upside_sum = 0.0
    covered_weight = 0.0
    total_config_weight = sum(w for _, w in config["holdings"])
    matched_count = 0

    for comp_ticker, weight in config["holdings"]:
        if comp_ticker in stock_results_map:
            comp_data = stock_results_map[comp_ticker]
            weighted_upside_sum += comp_data["upside_percent"] * weight
            covered_weight += weight
            matched_count += 1

    if covered_weight <= 0:
        raise ValueError("成分股皆無有效估值資料")

    weighted_upside = round(weighted_upside_sum / covered_weight, 2)
    fair_value = round(current_price * (1 + weighted_upside / 100.0), 2)

    coverage_ratio = round((covered_weight / total_config_weight) * 100, 1) if total_config_weight > 0 else 0
    if coverage_ratio >= 80:
        confidence = "高"
    elif coverage_ratio >= 50:
        confidence = "中"
    else:
        confidence = "低"

    models_summary = f"成分股加權 ({matched_count}/{len(config['holdings'])}檔, 覆蓋{coverage_ratio}%)"

    return {
        "symbol": config["symbol"],
        "raw_ticker": etf_ticker,
        "name": config["name"],
        "sector": config["sector"],
        "is_etf": True,
        "current_price": round(float(current_price), 2),
        "fair_value": fair_value,
        "upside_percent": weighted_upside,
        "confidence": confidence,
        "models_used": models_summary,
        "models": {}
    }

def main():
    results = []
    stock_results_map = {}
    seen = set()

    for t in TICKERS:
        if t in seen:
            continue
        seen.add(t)
        try:
            data = analyze_stock(t)
            results.append(data)
            stock_results_map[t] = data
            print(f"成功計算個股 {t}")
        except Exception as e:
            print(f"計算個股 {t} 失敗: {e}")

    etf_results = []
    for etf_ticker, config in ETF_HOLDINGS_CONFIG.items():
        try:
            etf_data = analyze_etf(etf_ticker, config, stock_results_map)
            etf_results.append(etf_data)
            print(f"成功計算 ETF {etf_ticker}: 公允價 {etf_data['fair_value']} ({etf_data['upside_percent']}%)")
        except Exception as e:
            print(f"計算 ETF {etf_ticker} 失敗: {e}")

    final_results = etf_results + results

    with open('valuation_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()