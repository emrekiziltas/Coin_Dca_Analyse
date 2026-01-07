# Crypto DCA Analyzer 📊

A powerful Python tool for analyzing Dollar Cost Averaging (DCA) investment strategies across cryptocurrency and fiat assets. Track the historical performance of monthly investments in Bitcoin (BTC), Ethereum (ETH), and US Dollar (USD) using Turkish Lira (TRY).

## 🎯 Overview

This analyzer simulates systematic monthly investments over a configurable time period, fetching real-time market data from Binance and Yahoo Finance to generate comprehensive performance reports in Excel format.

## ✨ Key Features

- **Automated Data Retrieval**
  - Real-time and historical cryptocurrency prices via Binance API
  - USD/TRY exchange rates from Yahoo Finance

- **DCA Strategy Simulation**
  - Calculate asset accumulation from fixed monthly TRY investments
  - Track purchases over customizable time periods

- **Comprehensive Performance Metrics**
  - Total invested amount (TRY)
  - Current portfolio values in both USD and TRY
  - Profit/Loss calculations with percentage returns for each asset

- **Professional Excel Reports**
  - **Detailed Data Sheet**: Monthly breakdown of prices, purchase amounts, and cumulative holdings
  - **Summary Sheet**: High-level comparison with automated formatting for currencies and percentages

- **Flexible Configuration**
  - Easy management of investment parameters via `config.ini`
  - Customizable look-back periods and monthly investment amounts

## 🛠 Installation

### Prerequisites
- Python 3.7 or higher

### Setup Steps

1. **Clone the Repository**
```bash
   git clone https://github.com/emrekiziltas/Coin_Dca_Analyse
   cd dca
```

2. **Install Required Dependencies**
```bash
   pip install pandas requests yfinance python-dateutil xlsxwriter
```

3. **Configure Settings**
   
   Create a `config.ini` file in the project root directory:
```ini
   [SETTINGS]
   # The number of years to look back
   years_back = 2
   # Monthly investment amount in TL
   monthly_income_tl = 30000

   [PATHS]
   # Base directory for saving data
   base_directory = ./outputs

   [API]
   # Binance API URL
   binance_url = https://api.binance.com/api/v3/klines
   # Symbols to track
   crypto_symbols = BTCUSDT, ETHUSDT
   # Yahoo Finance symbol
   fiat_symbol = USDTRY=X
```

## 🚀 Usage

Run the analyzer from the command line:
```bash
python coinanalyser.py
```

The tool will generate an Excel report named `combined_crypto_data_YYYY-MM-DD_HH-MM-SS.xlsx` in your configured output directory.

### Sample Console Output
```
💰 FINAL STATUS:
   Total Invested: 120,000.00 TL
   BTC Value: 245,350.50 TL (+104.46%)
   ETH Value: 185,120.20 TL (+54.27%)
   Dollar Value: 135,450.00 TL (+12.87%)
```

## 📁 Project Structure
```
dca/
├── coinanalyser.py      # Main execution script
├── config.ini           # Configuration file
├── outputs/             # Generated Excel reports
└── README.md
```

## ⚙️ Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `years_back` | Historical analysis period (years) | `2` |
| `monthly_income_tl` | Fixed monthly investment amount (TRY) | `30000` |
| `base_directory` | Output directory for reports | `./outputs` |
| `binance_url` | Binance API endpoint | `https://api.binance.com/api/v3/klines` |
| `crypto_symbols` | Cryptocurrency pairs to track | `BTCUSDT, ETHUSDT` |
| `fiat_symbol` | Yahoo Finance fiat symbol | `USDTRY=X` |

## 🔧 Technologies

- **Python 3.x** - Core programming language
- **Pandas** - Data manipulation and analysis
- **Requests** - HTTP requests to Binance API
- **yfinance** - Yahoo Finance data retrieval
- **XlsxWriter** - Excel report generation
- **python-dateutil** - Date parsing and manipulation

## 📊 Report Details

The generated Excel file contains two sheets:

1. **Detailed Data**: Month-by-month breakdown including:
   - Asset prices at purchase time
   - Amount purchased with monthly investment
   - Cumulative holdings
   - Running totals

2. **Summary**: Portfolio overview with:
   - Total investment amount
   - Current values for each asset
   - Profit/Loss in both absolute and percentage terms
   - Comparative performance metrics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. Always conduct your own research and consult with financial professionals before making investment decisions.

## 📧 Contact

For questions or feedback, please open an issue on GitHub or contact [@emrekiziltas](https://github.com/emrekiziltas).

---

**Note**: Past performance does not guarantee future results. Cryptocurrency investments carry significant risk.