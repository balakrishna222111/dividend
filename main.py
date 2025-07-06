import requests
import pandas as pd
from bs4 import BeautifulSoup
from tabulate import tabulate

def fetch_trendlyne_dividends(symbol):
    url = f"https://trendlyne.com/equity/Dividend/{symbol}/630/infosys-ltd-dividend/"
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevents being blocked
    resp = requests.get(url, headers=headers)

    # Check if page was fetched successfully
    if resp.status_code != 200:
        print(f"❌ Failed to fetch data. HTTP status code: {resp.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")

    if table is None:
        print("❌ Dividend table not found on the page. It may have changed or is unavailable.")
        return pd.DataFrame()

    # Parse table rows
    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = [td.text.strip() for td in tr.find_all("td")]
        if len(cols) >= 3:
            rows.append({
                "Ex-Date": cols[0],
                "Amount (₹)": cols[1],
                "Type": cols[2]
            })

    return pd.DataFrame(rows)

# User input
symbol = input("Enter NSE stock symbol (e.g., INFY, TCS): ").strip().upper()

# Fetch and process
df = fetch_trendlyne_dividends(symbol)

if df.empty:
    print("No dividend data available.")
else:
    df['Ex-Date'] = pd.to_datetime(df['Ex-Date'], format='mixed', dayfirst=True)
    filtered = df[(df['Ex-Date'].dt.year >= 2010) & (df['Ex-Date'].dt.year <= 2025)].copy()
    filtered['Ex-Date'] = filtered['Ex-Date'].dt.strftime('%d-%b-%Y')

    # Save to CSV
    filtered.to_csv(f"{symbol.lower()}_dividend_2010_2025.csv", index=False)

    # Print table
    print(tabulate(filtered, headers="keys", tablefmt="pretty"))
