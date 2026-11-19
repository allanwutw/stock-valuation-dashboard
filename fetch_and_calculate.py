import yfinance as yf
import json
import os

TW_NAME_MAP = {
    # 原有台股清單
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
    # 補齊 0050 其餘成分股（確保 50 檔 100% 納入計算）
    "1303.TW": "南亞", "2303.TW": "聯電", "2383.TW": "台光電", "3017.TW": "奇鋐", "2327.TW": "國巨*",
    "2890.TW": "永豐金", "3443.TW": "創意", "2360.TW": "致茂", "2301.TW": "光寶科", "3653.TW": "健策",
    "6446.TW": "藥華藥", "2059.TW": "川湖", "2344.TW": "華邦電", "2368.TW": "金像電", "4958.TW": "臻鼎-KY",
    "3665.TW": "貿聯-KY", "2395.TW": "研華", "2449.TW": "京元電子", "7769.TW": "鴻勁"
}

# === ETF 成分股與權重設定區（未來擴充 009800, 00830, SPY, QQQ, SOXX 可直接加在這裡） ===
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
    }
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
        weights = { "ddm": 0.5, "pb": 0.3, "analyst