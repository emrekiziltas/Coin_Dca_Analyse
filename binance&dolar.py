import os
import requests
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import warnings

# Gereksiz kalabalığı önlemek için uyarıları susturabilirsiniz
warnings.simplefilter(action='ignore', category=FutureWarning)


def fetch_monthly_26th_data(symbol, years_back=2):
    base_directory = r"C:\Users\ek675\Binance_Connect\data"
    directory = os.path.join(base_directory, "data_historical_26th")
    os.makedirs(directory, exist_ok=True)

    today = datetime.datetime.now()
    start_date = today - relativedelta(years=years_back)

    current_month = start_date
    rows = []

    print(f"{symbol} ve USDTRY için son {years_back} yılın verileri hazırlanıyor...")

    while current_month <= today:
        target_date = datetime.datetime(current_month.year, current_month.month, 26)
        if target_date > today: break

        # 1. Binance
        start_ms = int(target_date.timestamp() * 1000)
        crypto_price = None
        try:
            url = 'https://api.binance.com/api/v3/klines'
            params = {'symbol': symbol.upper(), 'interval': '1d', 'limit': 1, 'startTime': start_ms}
            res = requests.get(url, params=params)
            data = res.json()
            if data: crypto_price = float(data[0][4])
        except:
            pass

        # 2. Yahoo Finance (USDTRY)
        usd_try_price = None
        try:
            yf_df = yf.download("USDTRY=X",
                                start=(target_date - datetime.timedelta(days=4)).strftime('%Y-%m-%d'),
                                end=(target_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                                progress=False, auto_adjust=True)
            if not yf_df.empty:
                # En güncel veriyi güvenli şekilde al
                last_val = yf_df['Close'].iloc[-1]
                usd_try_price = float(last_val.iloc[0]) if isinstance(last_val, pd.Series) else float(last_val)
        except:
            pass

        rows.append({
            'Tarih': target_date.strftime('%Y-%m-%d'),
            'Sembol': symbol.upper(),
            'Fiyat_USD': crypto_price,
            'Dolar_Kuru': usd_try_price,
            'Fiyat_TRY': (crypto_price * usd_try_price) if (crypto_price and usd_try_price) else None
        })

        print(f"Bitti: {target_date.strftime('%Y-%m-%d')} | Kur: {usd_try_price}")
        current_month += relativedelta(months=1)
        time.sleep(0.1)

    df = pd.DataFrame(rows)
    file_path = os.path.join(directory, f"{symbol.lower()}_final_report.xlsx")
    df.to_excel(file_path, index=False)
    print(f"\nDosya Hazır: {file_path}")


fetch_monthly_26th_data('BTCUSDT', years_back=2)