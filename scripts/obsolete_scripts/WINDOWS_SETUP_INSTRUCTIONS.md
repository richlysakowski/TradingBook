# TradingBook - Windows Installation & Setup Guide

## Overview

**TradingBook** is a privacy-focused, desktop trading journal application built with:
- **Electron 38** - Desktop application framework
- **React 18** - User interface
- **SQLite/better-sqlite3** - Local database storage (with JSON fallback)
- **Chart.js** - Performance visualization
- **TailwindCSS** - Styling

All your trading data stays on your machine - no cloud required!

---

## Quick Start Options

### Option 1: Download Pre-built Installer (Easiest)

1. Go to [TradingBook Releases](https://github.com/appatalks/TradingBook/releases)
2. Download the latest `TradingBook-Setup-x.x.x.exe` installer
3. Run the installer and follow the prompts
4. Launch TradingBook from Start Menu or Desktop shortcut

### Option 2: Build from Source (This Guide)

Follow the instructions below to set up the development environment and build TradingBook yourself.

---

## Prerequisites

Before running the setup script, ensure you have:

### 1. Node.js (Required)
- **Version**: Node.js 18.x or 20.x LTS recommended
- **Download**: https://nodejs.org/
- Verify installation: `node --version` and `npm --version`

### 2. Git (Optional, for cloning)
- **Download**: https://git-scm.com/download/win
- Verify installation: `git --version`

### 3. Visual Studio Build Tools (Required for native modules)
- Required to compile `better-sqlite3` native bindings
- **Download**: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- During installation, select: **"Desktop development with C++"**

### 4. Python 3.x (Required for node-gyp)
- Usually installed with Node.js
- Verify installation: `python --version`

---

## Installation Methods

### Method A: Using the Setup Script (Recommended)

1. Open **Command Prompt** or **PowerShell** as Administrator
2. Navigate to the TradingBook folder:
   ```cmd
   cd "C:\Users\PowerUser\Documents\!!000_PyPaperTrader\TradingBook-by-Appatalks\TradingBook"
   ```
3. Run the setup script:
   ```cmd
   scripts\windows_setup.bat
   ```

### Method B: Manual Installation

1. Open Command Prompt in the TradingBook folder
2. Install dependencies:
   ```cmd
   npm install
   ```
3. If `better-sqlite3` fails to compile:
   ```cmd
   npm rebuild better-sqlite3
   ```
   Or install Windows Build Tools:
   ```cmd
   npm install --global windows-build-tools
   ```

---

## Running TradingBook

### Development Mode (with hot-reload)
```cmd
npm run electron-dev
```

### Production Mode
```cmd
npm run build
npm run electron-prod
```

### Build Windows Installer
```cmd
npm run build-windows-installer
```
Creates: `dist/TradingBook-Setup-x.x.x.exe`

### Build Windows Portable
```cmd
npm run build-windows-portable
```
Creates: `dist/TradingBook-x.x.x-portable.exe`

---

## Data Storage

TradingBook stores your data locally:

| File | Location | Description |
|------|----------|-------------|
| Database | `%APPDATA%\tradingbook\trades.db` | SQLite database |
| JSON Fallback | `%APPDATA%\tradingbook\trades.json` | Used if SQLite fails |
| Settings | `%APPDATA%\tradingbook\settings.json` | App preferences |
| Backups | `%USERPROFILE%\Downloads\` | Database exports |

To find your data folder:
```cmd
echo %APPDATA%\tradingbook
```

---

## Features

### Dashboard
- P&L Calendar with color-coded days
- Performance metrics (Win Rate, Profit Factor, Sharpe Ratio)
- Recent trades widget with symbol charts
- Daily notes for journaling

### Trade Management
- Add/Edit/Delete trades
- Support for: Stocks, Options, Crypto, Forex
- Bulk CSV import/export (ThinkorSwim compatible)
- Auto P&L matching for open positions

### Analytics
- NET Daily P&L charts
- Cumulative P&L tracking
- Win/Loss day analysis
- Drawdown monitoring
- **Wash Sale Watch** - IRS compliance helper

### Data Portability
- CSV Import: `File > Import CSV`
- CSV Export: `File > Export CSV`
- Database Backup: `File > Backup Database`
- Database Restore: `File > Restore Database`

---

## CSV Import Format

TradingBook accepts CSV files with the following columns:

```csv
Symbol,Side,Quantity,Entry Price,Exit Price,Entry Date,Exit Date,Commission,Strategy,Notes,Asset Type
AAPL,BUY,100,150.00,155.00,2024-01-15,2024-01-20,1.00,Momentum,Earnings play,STOCK
SPY,LONG,50,450.00,455.00,2024-01-16,2024-01-18,0.65,Breakout,Gap fill,STOCK
```

### ThinkorSwim Import
Export your activity from ThinkorSwim and use `File > Import CSV` to automatically parse trades.

---

## Troubleshooting

### Issue: `better-sqlite3` compilation fails

**Solution 1**: Rebuild native modules
```cmd
npm rebuild better-sqlite3
```

**Solution 2**: Install Visual Studio Build Tools
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Restart terminal and run `npm install` again

**Solution 3**: Use JSON fallback
TradingBook automatically falls back to JSON storage if SQLite fails. Your data is still safe!

### Issue: App shows blank screen

**Solution**: Clear cache and rebuild
```cmd
npm run clean
npm install
npm run electron-dev
```

### Issue: Permission denied on install

**Solution**: Run Command Prompt as Administrator

### Issue: Can't find trades.db

Your database is at: `%APPDATA%\tradingbook\trades.db`

Open File Explorer and paste: `%APPDATA%\tradingbook`

---

## Backup Your Data

### Regular Backups
1. Open TradingBook
2. Go to `File > Backup Database`
3. Saves to Downloads folder with timestamp

### Manual Backup
Copy this folder to a safe location:
```
%APPDATA%\tradingbook\
```

---

## Updating TradingBook

### From GitHub
```cmd
cd "C:\path\to\TradingBook"
git pull origin main
npm install
npm run electron-dev
```

### In-App Update Check
TradingBook checks for updates automatically and notifies you when a new version is available.

---

## Uninstalling

### If installed via Installer
1. Open Windows Settings > Apps
2. Find "TradingBook" and uninstall

### If built from source
1. Delete the TradingBook folder
2. (Optional) Delete data: `%APPDATA%\tradingbook`

---

## Getting Help

- **GitHub Issues**: https://github.com/appatalks/TradingBook/issues
- **Documentation**: Check the README.md in the project folder

---

## License

TradingBook is open-source software. See LICENSE file for details.
