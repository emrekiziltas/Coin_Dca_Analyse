import os
import requests
import pandas as pd
import time
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import warnings
import configparser
from typing import Optional

warnings.simplefilter(action='ignore', category=FutureWarning)


def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config dosyasi bulunamadi: {config_path}")
    config.read(config_path)
    return config


def fetch_binance_price(symbol: str, start_ms: int, url: str) -> Optional[float]:
    try:
        response = requests.get(
            url,
            params={'symbol': symbol, 'interval': '1d', 'limit': 1, 'startTime': start_ms},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return float(data[0][4]) if data else None
    except Exception:
        return None


def fetch_usdtry_price(target_date: datetime.datetime) -> Optional[float]:
    try:
        yf_df = yf.download(
            "USDTRY=X",
            start=(target_date - datetime.timedelta(days=5)).strftime('%Y-%m-%d'),
            end=(target_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
            progress=False, auto_adjust=True
        )
        return float(yf_df['Close'].iloc[-1]) if not yf_df.empty else None
    except Exception:
        return None


def calculate_investment_metrics(df: pd.DataFrame, per_transaction_tl: int) -> pd.DataFrame:
    df[['USDTRY', 'BTCUSDT', 'ETHUSDT']] = df[['USDTRY', 'BTCUSDT', 'ETHUSDT']].ffill()

    df['Alinan_Dolar'] = per_transaction_tl / df['USDTRY']
    df['Alinan_BTC'] = df['Alinan_Dolar'] / df['BTCUSDT']
    df['Alinan_ETH'] = df['Alinan_Dolar'] / df['ETHUSDT']

    df['Toplam_BTC'] = df['Alinan_BTC'].cumsum()
    df['Toplam_ETH'] = df['Alinan_ETH'].cumsum()
    df['Toplam_Dolar'] = df['Alinan_Dolar'].cumsum()
    df['Toplam_Yatirilan_TRY'] = per_transaction_tl * (df.index + 1)

    last_btc, last_eth, last_kur = df['BTCUSDT'].iloc[-1], df['ETHUSDT'].iloc[-1], df['USDTRY'].iloc[-1]

    df['BTC_Deger_TRY'] = df['Toplam_BTC'] * last_btc * last_kur
    df['ETH_Deger_TRY'] = df['Toplam_ETH'] * last_eth * last_kur
    df['USD_Deger_TRY'] = df['Toplam_Dolar'] * last_kur

    df['BTC_ROI_%'] = ((df['BTC_Deger_TRY'] - df['Toplam_Yatirilan_TRY']) / df['Toplam_Yatirilan_TRY']) * 100
    df['ETH_ROI_%'] = ((df['ETH_Deger_TRY'] - df['Toplam_Yatirilan_TRY']) / df['Toplam_Yatirilan_TRY']) * 100
    df['USD_ROI_%'] = ((df['USD_Deger_TRY'] - df['Toplam_Yatirilan_TRY']) / df['Toplam_Yatirilan_TRY']) * 100

    return df


def save_to_excel(df: pd.DataFrame, directory: str):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(directory, f"Yatirim_Analizi_{timestamp}.xlsx")
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Detayli_Veri', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Detayli_Veri']
        num_fmt = workbook.add_format({'num_format': '#,##0.00'})
        pct_fmt = workbook.add_format({'num_format': '0.0"%"'})
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#CFE2F3', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            if '%' in value:
                worksheet.set_column(col_num, col_num, 12, pct_fmt)
            else:
                worksheet.set_column(col_num, col_num, 15, num_fmt)
    return path


def run_analysis():
    try:
        config = load_config()
        mode = config.get('SETTINGS', 'mode', fallback='fixed_day')
        inv_day = config.getint('SETTINGS', 'investment_day', fallback=26)
        inv_interval = config.getint('SETTINGS', 'interval_days', fallback=30)
        years = config.getint('SETTINGS', 'years_back')
        amount = config.getint('SETTINGS', 'monthly_income_tl')
        base_dir = config.get('PATHS', 'base_directory')
        api_url = config.get('API', 'binance_url')

        os.makedirs(base_dir, exist_ok=True)
        end_date = datetime.datetime.now()

        # Başlangıç tarihini ayarla ve istenen güne sabitle
        current_date = (end_date - relativedelta(years=years))
        if mode == 'fixed_day':
            try:
                current_date = current_date.replace(day=inv_day)
            except ValueError:
                # Eğer o ay o gün yoksa (31 Şubat vb), ayın son günü yap
                current_date = (current_date + relativedelta(months=1)).replace(day=1) - datetime.timedelta(days=1)

        rows = []
        print(f"📊 Analiz Modu: {mode} | Baslangic: {current_date.date()}")

        while current_date <= end_date:
            ts = int(current_date.timestamp() * 1000)
            btc = fetch_binance_price('BTCUSDT', ts, api_url)
            eth = fetch_binance_price('ETHUSDT', ts, api_url)
            usd = fetch_usdtry_price(current_date)

            rows.append({
                'Tarih': current_date.strftime('%Y-%m-%d'),
                'BTCUSDT': btc, 'ETHUSDT': eth, 'USDTRY': usd
            })

            print(f"✅ {current_date.strftime('%Y-%m-%d')} islendi.")

            # --- TARİH İLERLETME MANTIĞI ---
            if mode == 'fixed_day':
                # Bir sonraki aya geç ve günü koru
                current_date += relativedelta(months=1)
                try:
                    current_date = current_date.replace(day=inv_day)
                except ValueError:
                    # Ay sonu kontrolü
                    current_date = (current_date + relativedelta(months=1)).replace(day=1) - datetime.timedelta(days=1)
            else:
                # Sadece belirlenen gün kadar ekle
                current_date += datetime.timedelta(days=inv_interval)

            time.sleep(0.1)

        df = calculate_investment_metrics(pd.DataFrame(rows), amount)
        file_path = save_to_excel(df, base_dir)
        print(f"\n🚀 Islem tamamlandi!\nDosya: {file_path}")

    except Exception as e:
        print(f"❌ Hata: {e}")


if __name__ == "__main__":
    run_analysis()