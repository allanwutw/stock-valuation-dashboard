import yfinance as yf
import json
import os

# 台股常用中文名稱對照表 (針對台50成分股)
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
        curr_fcf *= (1 + growth_rate)
        pv_sum += curr_fcf / ((1 + wacc) ** t)
    
    terminal_val = (curr_fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
    pv_terminal = terminal_val / ((1 + wacc) ** years)
    return round(pv_sum + pv_terminal, 2)

def analyze_stock(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    info = stock.info
    
    current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
    eps = info.get('trailingEps', 0)
    forward_eps = info.get('forwardEps', eps)
    pe_ratio = info.get('trailingPE', 15)
    pb_ratio = info.get('priceToBook', 1.5)
    book_value = info.get('bookValue', 0)
    sector = info.get('sector', '一般產業')
    
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

    # 處理股票名稱：台股優先使用自訂中文名，去除 .TW
    if ticker_symbol in TW_NAME_MAP:
        clean_symbol = ticker_symbol.replace(".TW", "")
        stock_name = TW_NAME_MAP[ticker_symbol]
    else:
        clean_symbol = ticker_symbol
        stock_name = info.get('shortName', ticker_symbol) or ticker_symbol

    growth_rate = 0.08
    if eps > 0 and forward_eps > eps:
        growth_rate = min((forward_eps - eps) / eps, 0.25)
    
    pe_fair = round(eps * pe_ratio, 2) if eps else None
    pb_fair = round(book_value * pb_ratio, 2) if book_value else None
    dcf_fair = calculate_dcf(eps, growth_rate) if eps > 0 else None

    valid_models = [m for m in [pe_fair, pb_fair, dcf_fair] if m is not None]
    fair_value = round(sum(valid_models) / len(valid_models), 2) if valid_models else current_price
    upside = round(((fair_value - current_price) / current_price) * 100, 2) if current_price else 0

    confidence = "高"
    if not forward_eps or not eps or eps <= 0:
        confidence = "低"
    elif len(valid_models) < 2:
        confidence = "中"

    return {
        "symbol": clean_symbol,
        "raw_ticker": ticker_symbol,
        "name": stock_name,
        "sector": category_name,
        "current_price": current_price,
        "fair_value": fair_value,
        "upside_percent": upside,
        "confidence": confidence,
        "models_used": "DCF + 倍數法",
        "models": {
            "pe_multiples": pe_fair,
            "pb_multiples": pb_fair,
            "dcf_5yr": dcf_fair
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
