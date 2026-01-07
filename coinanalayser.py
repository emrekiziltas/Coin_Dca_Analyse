import os
import requests
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import warnings
import configparser
from typing import Optional, Dict

warnings.simplefilter(action='ignore', category=FutureWarning)


def load_config() -> configparser.ConfigParser:
    """Config dosyasını yükler"""
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    config.read(config_path)
    return config


def fetch_binance_price(symbol: str, start_ms: int, url: str, max_retries: int = 3) -> Optional[float]:
    """Binance'den fiyat çeker - retry mantığı ile"""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                params={'symbol': symbol, 'interval': '1d', 'limit': 1, 'startTime': start_ms},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                return float(data[0][4])  # close price

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                print(f"   ⚠ {symbol} çekilemedi: {e}")
            time.sleep(1)  # Retry öncesi bekle

    return None


def fetch_usdtry_price(target_date: datetime.datetime) -> Optional[float]:
    """Yahoo Finance'den USDTRY kurunu çeker"""
    try:
        yf_df = yf.download(
            "USDTRY=X",
            start=(target_date - datetime.timedelta(days=4)).strftime('%Y-%m-%d'),
            end=(target_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            progress=False,
            auto_adjust=True
        )

        if not yf_df.empty:
            last_close = yf_df['Close'].iloc[-1]
            return float(last_close)

    except Exception as e:
        print(f"   ⚠ USDTRY çekilemedi: {e}")

    return None


def calculate_investment_metrics(df: pd.DataFrame, monthly_tl: int) -> pd.DataFrame:
    """Yatırım metriklerini hesaplar"""

    # Aylık alım miktarları
    df['Alinan_Dolar'] = monthly_tl / df['USDTRY']
    df['Alinan_BTC'] = df['Alinan_Dolar'] / df['BTCUSDT']
    df['Toplam_BTC'] = df['Alinan_BTC'].cumsum()

    df['Alinan_ETH'] = df['Alinan_Dolar'] / df['ETHUSDT']
    df['Toplam_ETH'] = df['Alinan_ETH'].cumsum()

    df['Toplam_Dolar'] = df['Alinan_Dolar'].cumsum()
    df['Toplam_Yatirilan_TRY'] = monthly_tl * (df.index + 1)

    # Güncel değerler (son satırdaki fiyatları kullan)
    son_btc = df['BTCUSDT'].iloc[-1]
    son_eth = df['ETHUSDT'].iloc[-1]
    son_kur = df['USDTRY'].iloc[-1]

    # USD bazlı güncel değerler
    df['BTC_Guncel_Deger_USD'] = df['Toplam_BTC'] * son_btc
    df['ETH_Guncel_Deger_USD'] = df['Toplam_ETH'] * son_eth
    df['Dolar_Guncel_Deger_USD'] = df['Toplam_Dolar']

    # TRY bazlı güncel değerler
    df['BTC_Guncel_Deger_TRY'] = df['BTC_Guncel_Deger_USD'] * son_kur
    df['ETH_Guncel_Deger_TRY'] = df['ETH_Guncel_Deger_USD'] * son_kur
    df['Dolar_Guncel_Deger_TRY'] = df['Dolar_Guncel_Deger_USD'] * son_kur

    # Kar/Zarar hesaplamaları
    df['BTC_Kar_Zarar_TRY'] = df['BTC_Guncel_Deger_TRY'] - df['Toplam_Yatirilan_TRY']
    df['BTC_Kar_Zarar_Yuzde'] = (df['BTC_Kar_Zarar_TRY'] / df['Toplam_Yatirilan_TRY']) * 100

    df['ETH_Kar_Zarar_TRY'] = df['ETH_Guncel_Deger_TRY'] - df['Toplam_Yatirilan_TRY']
    df['ETH_Kar_Zarar_Yuzde'] = (df['ETH_Kar_Zarar_TRY'] / df['Toplam_Yatirilan_TRY']) * 100

    df['Dolar_Kar_Zarar_TRY'] = df['Dolar_Guncel_Deger_TRY'] - df['Toplam_Yatirilan_TRY']
    df['Dolar_Kar_Zarar_Yuzde'] = (df['Dolar_Kar_Zarar_TRY'] / df['Toplam_Yatirilan_TRY']) * 100

    return df


def save_to_excel(df: pd.DataFrame, directory: str) -> str:
    """DataFrame'i formatlanmış Excel'e kaydeder"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"combined_crypto_data_{timestamp}.xlsx"
    file_path = os.path.join(directory, filename)

    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        # Ana veri sayfası
        df.to_excel(writer, sheet_name='Detayli_Veri', index=False)

        workbook = writer.book
        worksheet = writer.sheets['Detayli_Veri']

        # Format tanımlamaları
        money_fmt = workbook.add_format({'num_format': '#,##0.00', 'align': 'right'})
        percent_fmt = workbook.add_format({'num_format': '0.00%', 'align': 'right'})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BD', 'border': 1})

        # Kolon genişlikleri
        worksheet.set_column('A:A', 12)  # Tarih
        worksheet.set_column('B:Z', 16, money_fmt)  # Tüm sayılar

        # Header formatı
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)

        # Özet sayfa oluştur
        create_summary_sheet(writer, df, workbook)

    return file_path


def create_summary_sheet(writer, df: pd.DataFrame, workbook):
    """Özet sayfa oluşturur"""
    summary_data = {
        'Yatırım Türü': ['Bitcoin (BTC)', 'Ethereum (ETH)', 'Dolar (USD)'],
        'Toplam Yatırılan (TRY)': [df['Toplam_Yatirilan_TRY'].iloc[-1]] * 3,
        'Güncel Değer (TRY)': [
            df['BTC_Guncel_Deger_TRY'].iloc[-1],
            df['ETH_Guncel_Deger_TRY'].iloc[-1],
            df['Dolar_Guncel_Deger_TRY'].iloc[-1]
        ],
        'Kar/Zarar (TRY)': [
            df['BTC_Kar_Zarar_TRY'].iloc[-1],
            df['ETH_Kar_Zarar_TRY'].iloc[-1],
            df['Dolar_Kar_Zarar_TRY'].iloc[-1]
        ],
        'Kar/Zarar (%)': [
            df['BTC_Kar_Zarar_Yuzde'].iloc[-1] / 100,
            df['ETH_Kar_Zarar_Yuzde'].iloc[-1] / 100,
            df['Dolar_Kar_Zarar_Yuzde'].iloc[-1] / 100
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Ozet', index=False)

    # Özet sayfası formatları
    worksheet = writer.sheets['Ozet']
    money_fmt = workbook.add_format({'num_format': '#,##0.00 ₺'})
    percent_fmt = workbook.add_format({'num_format': '0.00%'})

    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:D', 20, money_fmt)
    worksheet.set_column('E:E', 15, percent_fmt)


def fetch_all_monthly_26th_data():
    """Ana fonksiyon - tüm veriyi çeker ve işler"""
    try:
        # Config yükle
        config = load_config()
        directory = config.get('PATHS', 'base_directory')
        years_back = config.getint('SETTINGS', 'years_back')
        monthly_tl = config.getint('SETTINGS', 'monthly_income_tl')
        binance_url = config.get('API', 'binance_url')

        os.makedirs(directory, exist_ok=True)

        # Tarih aralığı
        today = datetime.datetime.now()
        start_date = today - relativedelta(years=years_back)
        current_month = start_date
        rows = []

        print(f"\n{'=' * 60}")
        print(f"📊 Kripto Analiz Başlıyor")
        print(f"{'=' * 60}")
        print(f"Dönem: {start_date.date()} → {today.date()}")
        print(f"Aylık Yatırım: {monthly_tl:,} TL")
        print(f"Kayıt Yeri: {directory}\n")

        # Her ayın 26'sı için veri çek
        while current_month <= today:
            target_date = datetime.datetime(current_month.year, current_month.month, 26)
            if target_date > today:
                break

            start_ms = int(target_date.timestamp() * 1000)

            print(f"⏳ {target_date.strftime('%Y-%m-%d')} işleniyor...")

            # Fiyatları çek
            btc_price = fetch_binance_price('BTCUSDT', start_ms, binance_url)
            eth_price = fetch_binance_price('ETHUSDT', start_ms, binance_url)
            usd_try = fetch_usdtry_price(target_date)

            rows.append({
                'Tarih': target_date.strftime('%Y-%m-%d'),
                'BTCUSDT': btc_price,
                'ETHUSDT': eth_price,
                'USDTRY': usd_try
            })

            print(f"   ✓ BTC: ${btc_price:,.2f} | ETH: ${eth_price:,.2f} | Kur: ₺{usd_try:.2f}")

            current_month += relativedelta(months=1)
            time.sleep(0.3)  # Rate limiting

        # DataFrame oluştur
        df = pd.DataFrame(rows)

        # Eksik veri kontrolü
        missing_data = df.isnull().sum()
        if missing_data.any():
            print(f"\n⚠ Eksik veriler var:\n{missing_data[missing_data > 0]}")

        # Metrikleri hesapla
        df = calculate_investment_metrics(df, monthly_tl)

        # Excel'e kaydet
        file_path = save_to_excel(df, directory)

        # Sonuç özeti
        print(f"\n{'=' * 60}")
        print(f"✅ BAŞARILI!")
        print(f"{'=' * 60}")
        print(f"📁 Dosya: {file_path}")
        print(f"📊 Toplam Veri: {len(df)} ay")
        print(f"\n💰 SON DURUM:")
        print(f"   Toplam Yatırılan: {df['Toplam_Yatirilan_TRY'].iloc[-1]:,.2f} TL")
        print(
            f"   BTC Değeri: {df['BTC_Guncel_Deger_TRY'].iloc[-1]:,.2f} TL ({df['BTC_Kar_Zarar_Yuzde'].iloc[-1]:+.2f}%)")
        print(
            f"   ETH Değeri: {df['ETH_Guncel_Deger_TRY'].iloc[-1]:,.2f} TL ({df['ETH_Kar_Zarar_Yuzde'].iloc[-1]:+.2f}%)")
        print(
            f"   Dolar Değeri: {df['Dolar_Guncel_Deger_TRY'].iloc[-1]:,.2f} TL ({df['Dolar_Kar_Zarar_Yuzde'].iloc[-1]:+.2f}%)")
        print(f"{'=' * 60}\n")

    except FileNotFoundError as e:
        print(f"❌ Hata: {e}")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    fetch_all_monthly_26th_data()