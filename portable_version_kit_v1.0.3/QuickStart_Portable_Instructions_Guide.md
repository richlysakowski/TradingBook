# TradingBook Portable Version - Quick Start Guide

## What is TradingBook?

TradingBook is a **privacy-focused desktop trading journal** that helps you track your trades, analyze performance, and improve your trading. All your data stays on your computer - no cloud, no subscriptions.

---

## Getting Started (3 Easy Steps)

### Step 1: Run the Application

1. **Double-click** `TradingBook 1.0.3.exe`
2. Wait 5-10 seconds for the application to load
3. The **Dashboard** will appear

**Note**: Windows SmartScreen may show a warning on first run. Click "More info" → "Run anyway" (the app is safe but not digitally signed).

### Step 2: Import Your Trades

#### Option A: Import from Schwab CSV

1. Go to **File → Import CSV** (or click "Import CSV" button)
2. Select your Schwab export file
3. Preview the trades and click **Import**
4. Trades will be automatically matched and P&L calculated

#### Option B: Add Trades Manually

1. Click **"+ Add Trade"** in the sidebar
2. Fill in the trade details:
   - Symbol (e.g., AAPL, TSLA)
   - Side (Buy/Sell)
   - Quantity
   - Entry Price
   - Entry Date
3. Click **Save**

### Step 3: View Your Performance

- **Dashboard**: Overview with P&L calendar and metrics
- **Trade List**: All your trades with filtering
- **Analytics**: Charts, win rate, drawdown analysis

---

## Key Features

| Feature | Description |
|---------|-------------|
| 📊 **Dashboard** | P&L calendar, daily performance, recent trades |
| 📈 **Analytics** | Win rate, profit factor, cumulative P&L charts |
| 📝 **Trade List** | Filter, sort, and manage all trades |
| 💹 **Stock Charts** | View price history with your entry/exit points |
| 🔄 **CSV Import** | Import from Schwab and other brokers |
| 💾 **Backup/Restore** | Protect your data with easy backups |
| 🌙 **Dark Mode** | Easy on the eyes for late-night analysis |
| 🧾 **Wash Sale Watch** | Track 30-day windows to avoid wash sales |

---

## Where is My Data Stored?

Your trading data is stored locally at:
```
C:\Users\[YourUsername]\AppData\Roaming\tradingbook\
```

**Files stored**:
- `trades.db` - Your trades database
- `settings.json` - Application preferences

**To find this folder**:
1. Press `Win + R`
2. Type `%APPDATA%\tradingbook`
3. Press Enter

---

## Backup Your Data

**Regular backups are recommended!**

### Create a Backup

1. Go to **File → Backup Database**
2. A timestamped backup file is saved to your Downloads folder

### Restore from Backup

1. Go to **File → Restore Database**
2. Select your backup file
3. Confirm the restore

---

## Importing Schwab CSV Files

TradingBook supports Schwab's transaction export format:

### Expected CSV Format

```csv
Date,Action,Symbol,Description,Quantity,Price,Fees & Comm,Amount
01/15/2024,Buy,AAPL,APPLE INC,100,185.50,0.65,-18550.65
01/20/2024,Sell,AAPL,APPLE INC,100,190.25,0.65,19024.35
```

### Steps to Export from Schwab

1. Log into Schwab.com
2. Go to **Accounts → History**
3. Select date range
4. Click **Export** → **CSV**
5. Save the file

### Import into TradingBook

1. Click **File → Import CSV**
2. Select the Schwab CSV file
3. Preview the trades
4. Click **Import**

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + N` | New Trade |
| `Ctrl + I` | Import CSV |
| `Ctrl + E` | Export CSV |
| `Ctrl + D` | Toggle Dark Mode |

---

## Troubleshooting

### App won't start

- Ensure you're running Windows 10 or 11 (64-bit)
- Try running as Administrator (right-click → Run as administrator)
- Check if antivirus is blocking the application

### Windows SmartScreen warning

This is normal for unsigned applications:
1. Click **"More info"**
2. Click **"Run anyway"**

### CSV import not working

- Ensure the CSV is in Schwab format (comma-separated)
- Check that the file isn't open in Excel
- Try saving the CSV with UTF-8 encoding

### Data not showing after import

1. Wait for the import to complete
2. Check the **Trade List** view
3. Clear any filters that might be hiding trades

---

## Getting Help

- **Issues/Bugs**: https://github.com/appatalks/TradingBook/issues
- **Documentation**: See README.md in the project folder

---

## Moving the Portable App

You can move `TradingBook 1.0.3.exe` anywhere:
- USB drive
- Different folder
- Another computer

**Your data stays in** `%APPDATA%\tradingbook\` on each computer.

To transfer data to another computer:
1. Backup on original computer (**File → Backup Database**)
2. Copy backup file to new computer
3. Restore on new computer (**File → Restore Database**)

---

**Happy Trading! 📈**
