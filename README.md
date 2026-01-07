Crypto & Fiat DCA Analyzer 📊
A robust Python-based tool designed to analyze Dollar Cost Averaging (DCA) strategies. This tool calculates the historical performance of investing a fixed amount of Turkish Lira (TRY) into Bitcoin (BTC), Ethereum (ETH), and US Dollar (USD) on a monthly basis.

It fetches real-time and historical data from the Binance API and Yahoo Finance, processing the results into a formatted, professional Excel report.

✨ Features
Automated Data Retrieval: Pulls historical crypto prices from Binance API and currency exchange rates (USD/TRY) from Yahoo Finance.

DCA Strategy Analysis: Calculates how much asset you would have accumulated by investing a fixed amount of TRY every month.

Comprehensive Metrics: * Total invested amount (TRY).

Current portfolio value in both USD and TRY.

Profit/Loss (P/L) amounts and percentages for each asset class.

Professional Excel Reporting:

Detailed Data Sheet: Monthly breakdown of prices, purchases, and cumulative totals.

Summary Sheet: A high-level comparison table with automated currency and percentage formatting.

Robust Configuration: Manage API endpoints, investment amounts, and look-back periods via an external config.ini file.

🛠 Installation
Clone the Repository:

Bash

git clone https://github.com/emrekiziltas/dca.git
cd dca
Install Dependencies:

Bash

pip install pandas requests yfinance python-dateutil xlsxwriter
Setup Configuration: Create a config.ini file in the root directory:

Ini, TOML

[PATHS]
base_directory = ./outputs

[SETTINGS]
years_back = 2
monthly_income_tl = 5000

[API]
binance_url = https://api.binance.com/api/v3/klines
🚀 Usage
Run the analyzer using the following command:

Bash

python main.py
Once the process is complete, an Excel file named combined_crypto_data_YYYY-MM-DD_HH-MM-SS.xlsx will be generated in your specified output directory.

📊 Sample Output
The console will display a summary like the one below:

Plaintext

💰 FINAL STATUS:
   Total Invested: 120,000.00 TL
   BTC Value: 245,350.50 TL (+104.46%)
   ETH Value: 185,120.20 TL (+54.27%)
   Dollar Value: 135,450.00 TL (+12.87%)
📝 Technologies Used
Python 3.x

Pandas: For data manipulation and metric calculations.

Yfinance: To fetch historical USD/TRY exchange rates.

Requests: For Binance API communication.
