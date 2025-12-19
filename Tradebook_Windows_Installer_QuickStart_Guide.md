# TradingBook Windows Installer - Quick Start Guide

## Welcome to TradingBook!

TradingBook is a professional trading journal application that helps you track, analyze, and improve your trading performance.

---

## Installation

### Step 1: Run the Installer

1. Double-click **TradingBook Setup 1.0.3.exe**
2. If Windows SmartScreen appears, click **More info** → **Run anyway**
3. Follow the installation wizard:
   - Accept the license agreement
   - Choose installation folder (default: `C:\Users\YourName\AppData\Local\Programs\TradingBook`)
   - Select Start Menu folder
   - Choose whether to create a desktop shortcut

### Step 2: Complete Installation

Click **Install** and wait for the process to complete (~30 seconds).

### Step 3: Launch TradingBook

Choose one of these methods:
- Click **Finish** with "Launch TradingBook" checked
- Find **TradingBook** in your Start Menu
- Double-click the desktop shortcut (if created)

---

## First Launch

When TradingBook starts for the first time:

1. **Dashboard** appears showing your trading overview
2. **Database** is automatically created at:
   ```
   C:\Users\YourName\AppData\Roaming\tradingbook\trades.db
   ```
3. The application is ready to use immediately!

---

## Getting Started

### Adding Your First Trade

1. Click **Add Trade** or navigate to **Trades** → **New Trade**
2. Fill in the trade details:
   - **Symbol**: Stock/instrument ticker (e.g., AAPL, MSFT)
   - **Side**: BUY, SELL, LONG, or SHORT
   - **Quantity**: Number of shares/contracts
   - **Entry Price**: Your entry price
   - **Entry Date**: When you entered the trade
   - **Asset Type**: STOCK, OPTION, CRYPTO, or FOREX
3. Click **Save**

### Importing Trades from Schwab/ThinkorSwim

1. Export trades from Schwab:
   - Log into Schwab/ThinkorSwim
   - Go to **Account** → **History** → **Transactions**
   - Export as CSV
2. In TradingBook, click **Import** → **CSV Import**
3. Select your CSV file
4. Map the columns to TradingBook fields
5. Click **Import**

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | Overview of P&L, win rate, and key metrics |
| **Trade Log** | Complete list of all trades with filtering |
| **Analytics** | Charts and statistics for performance analysis |
| **Portfolio** | Track your current positions |
| **Import/Export** | CSV support for data portability |

---

## Where is My Data Stored?

All your trading data is stored locally on your computer:

```
C:\Users\YourName\AppData\Roaming\tradingbook\
└── trades.db  (SQLite database)
```

**To access this folder**:
1. Press `Win + R`
2. Type `%APPDATA%\tradingbook`
3. Press Enter

### Backup Your Data

To backup your trades:
1. Navigate to `%APPDATA%\tradingbook\`
2. Copy `trades.db` to your backup location

---

## Uninstalling

If you need to remove TradingBook:

### Method 1: Settings App
1. Press `Win + I` to open Settings
2. Go to **Apps** → **Installed apps**
3. Find **TradingBook**
4. Click **⋮** (three dots) → **Uninstall**

### Method 2: Control Panel
1. Open **Control Panel**
2. Go to **Programs** → **Programs and Features**
3. Find **TradingBook**
4. Click **Uninstall**

**Note**: Your trading data in `%APPDATA%\tradingbook\` is preserved during uninstallation. Delete manually if you want to remove all data.

---

## Troubleshooting

### TradingBook won't start

1. **Restart your computer** and try again
2. **Reinstall**: Uninstall and run the installer again
3. **Check for error messages** in the Windows Event Viewer

### Database errors

If you see database errors:
1. Navigate to `%APPDATA%\tradingbook\`
2. Rename `trades.db` to `trades.db.backup`
3. Restart TradingBook (creates a fresh database)
4. Re-import your data from CSV if needed

### Import not working

1. Ensure your CSV file uses UTF-8 encoding
2. Check that column headers match expected format
3. Verify dates are in a standard format (MM/DD/YYYY or YYYY-MM-DD)

---

## System Requirements

| Requirement | Minimum |
|-------------|---------|
| **Operating System** | Windows 10 64-bit |
| **Disk Space** | 350MB |
| **RAM** | 4GB |
| **Screen Resolution** | 1280x720 |

---

## Getting Help

- **Documentation**: Check the `docs` folder in the installation directory
- **GitHub Issues**: Report bugs or request features on the project repository
- **Keyboard Shortcuts**: Press `Ctrl + ?` in the app for shortcuts

---

## Version Information

- **Version**: 1.0.3
- **Build Date**: December 2025
- **License**: MIT

---

*Thank you for using TradingBook! Happy trading!* 📈
