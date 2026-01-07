import os
import requests
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import warnings
import configparser

warnings.simplefilter(action='ignore', category=FutureWarning)


def load_config():
    config = configparser.ConfigParser()
    # This ensures it finds the config.ini even if you run from a different folder
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    config.read(config_path)
    return config


def fetch_all_monthly_26th_data():
    # 1. Load Config
    config = load_config()

    # 2. Get Variables (Removing subfolder logic)
    directory = config.get('PATHS', 'base_directory')
    years_back = config.getint('SETTINGS', 'years_back')
    monthly_tl = config.getint('SETTINGS', 'monthly_income_tl')
    binance_url = config.get('API', 'binance_url')

    os.makedirs(directory, exist_ok=True)

    today = datetime.datetime.now()
    start_date = today - relativedelta(years=years_back)
    current_month = start_date
    rows = []

    print(f"Veriler çekiliyor. Kayıt yeri: {directory}\n")

    while current_month <= today:
        target_date = datetime.datetime(current_month.year, current_month.month, 26)
        if target_date > today: break

        start_ms = int(target_date.timestamp() * 1000)

        # Data fetching logic
        btc_p, eth_p, usd_p = None, None, None

        # BTC/ETH (Binance)
        for symbol in ['BTCUSDT', 'ETHUSDT']:
            try:
                res = requests.get(binance_url,
                                   params={'symbol': symbol, 'interval': '1d', 'limit': 1, 'startTime': start_ms})
                val = float(res.json()[0][4])
                if symbol == 'BTCUSDT':
                    btc_p = val
                else:
                    eth_p = val
            except:
                pass

        # USDTRY (Yahoo)
        try:
            yf_df = yf.download("USDTRY=X", start=(target_date - datetime.timedelta(days=4)),
                                end=(target_date + datetime.timedelta(days=1)), progress=False)
            usd_p = float(yf_df['Close'].iloc[-1])
        except:
            pass

        rows.append({
            'Tarih': target_date.strftime('%Y-%m-%d'),
            'BTCUSDT': btc_p,
            'ETHUSDT': eth_p,
            'USDTRY': usd_p
        })
        print(f"✓ {target_date.date()} işlendi.")
        current_month += relativedelta(months=1)

    # 3. Calculations and Excel
    df = pd.DataFrame(rows)

    # Simple Math for the Summary
    df['Alinan_BTC'] = (monthly_tl / df['USDTRY']) / df['BTCUSDT']
    df['Alinan_ETH'] = (monthly_tl / df['USDTRY']) / df['ETHUSDT']
    df['Toplam_BTC'] = df['Alinan_BTC'].cumsum()
    df['Toplam_ETH'] = df['Alinan_ETH'].cumsum()
    df['Toplam_Yatirilan_TRY'] = monthly_tl * (df.index + 1)
    # En son satırdaki (güncel) fiyatları alıyoruz
    son_btc_fiyat = df['BTCUSDT'].iloc[-1]
    son_eth_fiyat = df['ETHUSDT'].iloc[-1]

    # Elimizdeki toplam miktarın GÜNCEL fiyattan kaç DOLAR ettiği
    df['BTC_Guncel_Deger_USD'] = df['Toplam_BTC'] * son_btc_fiyat
    df['ETH_Guncel_Deger_USD'] = df['Toplam_ETH'] * son_eth_fiyat

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"combined_crypto_data_{timestamp}.xlsx"
    file_path = os.path.join(directory, filename)
    df.to_excel(file_path, index=False)

    print(f"\n{'=' * 30}\nBaşarılı! Dosya: {file_path}\n{'=' * 30}")


if __name__ == "__main__":
    fetch_all_monthly_26th_data()