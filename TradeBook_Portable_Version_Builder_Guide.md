# TradingBook Portable Version Builder Guide

## Overview

This guide provides step-by-step instructions to build the **TradingBook Portable Version** - a single executable file that runs without installation on any Windows 10/11 computer.

**Output**: `TradingBook 1.0.3.exe` (~350MB portable executable)

**Build Time**:
- First build: ~8-12 minutes (includes dependency installation)
- Subsequent builds: ~3-4 minutes (with caching)

---

## Prerequisites

Before building, ensure you have the following installed:

### Required Software

| Software | Version | Download Link |
|----------|---------|---------------|
| Node.js | 18.x or 20.x LTS | https://nodejs.org/ |
| npm | 8.x or higher | (Included with Node.js) |
| Git | Latest | https://git-scm.com/download/win |

### Optional (for native module compilation)

| Software | Purpose |
|----------|---------|
| Visual Studio Build Tools | Compile better-sqlite3 native bindings |
| Python 3.x | Required by node-gyp |

**Note**: If native compilation fails, TradingBook will automatically use JSON file storage as a fallback.

---

## Quick Build (Recommended)

### Option A: Use the Build Script

1. **Open Command Prompt** in the TradingBook folder:
   ```cmd
   cd C:\Users\PowerUser\Documents\TradingBook
   ```

2. **Run the portable build script**:
   ```cmd
   build_portable.bat
   ```
   
   Or for a clean rebuild (ignores cache):
   ```cmd
   build_portable.bat --force
   ```

3. **Find your portable executable** in:
   ```
   portable_version_kit\TradingBook 1.0.3.exe
   ```

---

## Manual Build Steps

If you prefer to build manually or the script fails:

### Step 1: Open Command Prompt

```cmd
cd C:\Users\PowerUser\Documents\TradingBook
```

### Step 2: Install Dependencies

```cmd
npm install --legacy-peer-deps
```

**Expected time**: 2-5 minutes

**Note**: The `--legacy-peer-deps` flag resolves TypeScript version conflicts between packages.

### Step 3: Build React Production Bundle

```cmd
npm run build
```

**Expected output**:
```
Creating an optimized production build...
Compiled successfully.

File sizes after gzip:
  163.31 kB  build\static\js\main.xxxxxxxx.js
  6.36 kB    build\static\css\main.xxxxxxxx.css
```

### Step 4: Build Portable Executable

```cmd
npm run pack-portable
```

**Note**: Use `npm run build-windows-portable` if you skipped Step 3 (it includes the React build).

**Expected time**: 3-5 minutes

**Expected output**:
```
• electron-builder  version=26.0.12
• packaging       platform=win32 arch=x64 electron=38.2.2
• building        target=portable file=dist\TradingBook 1.0.3.exe
```

### Step 5: Locate Output File

The portable executable is created at:
```
dist\TradingBook 1.0.3.exe
```

### Step 6: Copy to Distribution Folder

```cmd
if not exist "portable_version_kit" mkdir portable_version_kit
copy "dist\TradingBook 1.0.3.exe" "portable_version_kit\"
```

---

## Build Output Structure

After a successful build:

```
TradingBook/
├── dist/
│   ├── TradingBook 1.0.3.exe          # Portable executable
│   ├── win-unpacked/                   # Unpacked app directory
│   └── builder-effective-config.yaml   # Build configuration
├── portable_version_kit/
│   ├── TradingBook 1.0.3.exe          # Copy for distribution
│   └── QuickStart_Portable_Instructions_Guide.md
└── build/
    └── (React production files)
```

---

## Troubleshooting

### Issue: `npm install` fails with peer dependency errors

**Solution**: Use the legacy peer deps flag:
```cmd
npm install --legacy-peer-deps
```

### Issue: `better-sqlite3` compilation fails

**Solution 1**: Install Visual Studio Build Tools
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Select "Desktop development with C++"

**Solution 2**: TradingBook will automatically use JSON storage fallback

### Issue: Build fails with "Access is denied"

**Cause**: Files are locked by another process (VS Code, Explorer, antivirus)

**Solution**:
1. Close VS Code
2. Close any Explorer windows viewing the `dist` folder
3. Temporarily disable antivirus real-time scanning
4. Delete the `dist` folder manually and rebuild:
   ```cmd
   rmdir /s /q dist
   npm run build-windows-portable
   ```

### Issue: Node.js version warnings (EBADENGINE)

**Cause**: Some packages prefer Node.js 20+

**Solution**: These are warnings only, not errors. The build will succeed. Consider upgrading to Node.js 20 LTS for cleaner builds.

---

## Verifying the Build

### Check File Size

The portable executable should be approximately **150-200MB**:
```cmd
dir "dist\TradingBook 1.0.3.exe"
```

### Test Run

1. Copy `TradingBook 1.0.3.exe` to a test location (e.g., Desktop)
2. Double-click to run
3. Verify the application opens and displays the Dashboard

---

## Distribution

### Sharing the Portable Version

1. Copy `portable_version_kit\TradingBook 1.0.3.exe` to:
   - USB drive
   - Cloud storage (OneDrive, Google Drive, Dropbox)
   - File sharing service (WeTransfer)

2. Include the `QuickStart_Portable_Instructions_Guide.md` for end users

### Requirements for End Users

- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **No installation required**
- **No administrator privileges needed**
- **No Node.js or other software required**

---

## Data Storage Location

The portable version stores user data at:
```
%APPDATA%\tradingbook\
```

This includes:
- `trades.db` - SQLite database (or `trades.json` fallback)
- `settings.json` - User preferences
- Database backups

**Note**: Data persists between sessions and survives moving the executable to a different location.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.3 | Dec 2025 | Current release |

---

## See Also

- [QuickStart_Portable_Instructions_Guide.md](portable_version_kit/QuickStart_Portable_Instructions_Guide.md) - How to run the portable version
- [Build_TradeBook_Windows_Installer_Guide.md](Build_TradeBook_Windows_Installer_Guide.md) - Build the installer version
