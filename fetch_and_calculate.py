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

def _extract_positive_number(val):
    try:
        if val is None or isinstance(val, bool):
            return None
        num = float(val)
        if num > 0:
            return num
    except Exception:
        pass
    return None

def get_etf_current_price(etf, info=None):
    """多層備援取得 ETF 現價：info -> fast_info -> 歷史收盤價"""
    info_dict = info if isinstance(info, dict) else {}

    # 1. info 常見價格欄位
    for key in ("currentPrice", "regularMarketPrice", "navPrice", "previousClose", "regularMarketPreviousClose", "open"):
        price = _extract_positive_number(info_dict.get(key))
        if price is not None:
            return round(price, 2)

    # 2. fast_info 欄位
    try:
        fast = getattr(etf, "fast_info", None)
        if fast is not None:
            for key in ("lastPrice", "regularMarketPreviousClose", "previousClose"):
                raw_val = fast.get(key) if hasattr(fast, "get") else getattr(fast, key, None)
                price = _extract_positive_number(raw_val)
                if price is not None:
                    return round(price, 2)
    except Exception:
        pass

    # 3. 近 10 日歷史收盤價
    for period in ("5d", "10d", "1mo"):
        try:
            hist = etf.history(period=period)
            if hist is not None and not hist.empty and "Close" in hist.columns:
                closes = hist["Close"].dropna()
                if not closes.empty:
                    price = _extract_positive_number(closes.iloc[-1])
                    if price is not None:
                        return round(price, 2)
        except Exception:
            pass

    return None

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
    info = stock.info or {}
    
    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    if not current_price or current_price <= 0:
        raise ValueError("無效的當前股價")

    eps = info.get('trailingEps', 0) or 0
    forward_eps = info.get('forwardEps', eps) or eps
    pe_ratio = info.get('trailingPE', 15) or 15