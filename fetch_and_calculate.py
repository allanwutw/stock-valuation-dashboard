import yfinance as yf
import json
import os

# 台灣市值代表股與美國前兩百大熱門市值股票清單
TICKERS = [
    # 台灣重要權值股 (台股請加 .TW)
    "2330.TW", "2317.TW", "2454.TW", "2308.TW", "2881.TW", 
    "2882.TW", "2412.TW", "2891.TW", "3711.TW", "1301.TW",
    # 美國標竿與前百大市值熱門股
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", 
    "BRK-B", "UNH", "JNJ", "JPM", "V", "XOM", "PG", "MA"
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
    
    growth_rate = 0.08
    if eps > 0 and forward_eps > eps:
        growth_rate = min((forward_eps - eps) / eps, 0.25)
    
    pe_fair = round(eps * pe_ratio, 2) if eps else None
    pb_fair = round(book_value * pb_ratio, 2) if book_value else None
    dcf_fair = calculate_dcf(eps, growth_rate) if eps > 0 else None

    valid_models = [m for m in [pe_fair, pb_fair, dcf_fair] if m is not None]
    fair_value = round(sum(valid_models) / len(valid_models), 2) if valid_models else current_price
    upside = round(((fair_value - current_price) / current_price) * 100, 2) if current_price else 0

    return {
        "symbol": ticker_symbol,
        "name": info.get('shortName', ticker_symbol) or ticker_symbol,
        "current_price": current_price,
        "fair_value": fair_value,
        "upside_percent": upside,
        "models": {
            "pe_multiples": pe_fair,
            "pb_multiples": pb_fair,
            "dcf_5yr": dcf_fair
        }
    }

def main():
    results = []
    for t in TICKERS:
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
