# Build TradingBook Windows Installer Guide

## Overview

This guide provides step-by-step instructions to build the **TradingBook Windows Installer** - a professional NSIS-based installer that installs TradingBook like any standard Windows application.

**Output**: `TradingBook Setup 1.0.3.exe` (~98MB installer)

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

---

## Quick Build (Recommended)

### Option A: Use the Build Script

1. **Open Command Prompt** in the TradingBook folder:
   ```cmd
   cd C:\Users\PowerUser\Documents\TradingBook
   ```

2. **Run the installer build script**:
   ```cmd
   build_installer.bat
   ```
   
   Or for a clean rebuild (ignores cache):
   ```cmd
   build_installer.bat --force
   ```

3. **Find your installer** in:
   ```
   dist\TradingBook Setup 1.0.3.exe
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

### Step 4: Build Windows Installer

```cmd
npm run pack-installer
```

**Note**: Use `npm run build-windows-installer` if you skipped Step 3 (it includes the React build).

**Expected time**: 3-5 minutes

**What happens**:
1. Electron app is packaged with all dependencies
2. Native modules are rebuilt for Windows
3. NSIS installer is generated

**Expected output**:
```
• electron-builder  version=26.0.12
• packaging       platform=win32 arch=x64 electron=38.2.2
• building        target=nsis file=dist\TradingBook Setup 1.0.3.exe archs=x64 oneClick=false perMachine=false
```

### Step 5: Locate Output File

The installer is created at:
```
dist\TradingBook Setup 1.0.3.exe
```

---

## Build Both Installer and Portable

To build both versions at once:

```cmd
npm run build-windows-both
```

This creates:
- `dist\TradingBook Setup 1.0.3.exe` - Installer
- `dist\TradingBook 1.0.3.exe` - Portable

---

## Build Output Structure

After a successful build:

```
TradingBook/
├── dist/
│   ├── TradingBook Setup 1.0.3.exe    # NSIS Installer
│   ├── TradingBook 1.0.3.exe          # Portable (if built)
│   ├── win-unpacked/                   # Unpacked app directory
│   └── builder-effective-config.yaml   # Build configuration
└── build/
    └── (React production files)
```

---

## Installer Features

The NSIS installer includes:

| Feature | Description |
|---------|-------------|
| **Custom install location** | Users can choose where to install |
| **Start Menu shortcuts** | Adds TradingBook to Start Menu |
| **Desktop shortcut** | Optional desktop icon |
| **Uninstaller** | Clean removal via Control Panel |
| **Per-user install** | No administrator rights required by default |

### Installer Options

The installer uses `oneClick=false` which provides:
- Installation directory selection
- Component selection
- License agreement display
- Start menu folder customization

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

**Solution 2**: TradingBook will use JSON storage fallback automatically

### Issue: Build fails with "Access is denied"

**Cause**: Files are locked by another process

**Solution**:
1. Close VS Code and Explorer windows viewing `dist` folder
2. Delete the `dist` folder:
   ```cmd
   rmdir /s /q dist
   ```
3. Rebuild:
   ```cmd
   npm run build-windows-installer
   ```

### Issue: NSIS not found

**Solution**: electron-builder downloads NSIS automatically. If it fails:
1. Check internet connection
2. Clear electron-builder cache:
   ```cmd
   rmdir /s /q "%LOCALAPPDATA%\electron-builder\Cache"
   ```
3. Retry the build

### Issue: "default Electron icon is used"

**Note**: This is a warning, not an error. The build will succeed. To add a custom icon:
1. Create a 256x256 PNG icon
2. Add to `build` section of `package.json`:
   ```json
   "build": {
     "win": {
       "icon": "assets/icon.ico"
     }
   }
   ```

---

## Verifying the Build

### Check File Size

The installer should be approximately **90-120MB**:
```cmd
dir "dist\TradingBook Setup 1.0.3.exe"
```

### Test Installation

1. Run `TradingBook Setup 1.0.3.exe`
2. Follow the installation wizard
3. Launch TradingBook from Start Menu or Desktop
4. Verify the Dashboard loads correctly

### Test Uninstallation

1. Go to **Settings → Apps → TradingBook**
2. Click **Uninstall**
3. Verify clean removal

---

## Distribution

### Sharing the Installer

1. Copy `dist\TradingBook Setup 1.0.3.exe` to:
   - USB drive
   - Cloud storage (OneDrive, Google Drive, Dropbox)
   - File sharing service (WeTransfer)

2. Include the `Tradebook_Windows_Installer_QuickStart_Guide.md` for end users

### Requirements for End Users

- **Operating System**: Windows 10 or Windows 11 (64-bit)
- **Disk Space**: ~350MB after installation
- **No additional software required**

---

## Installer vs Portable Comparison

| Feature | Installer | Portable |
|---------|-----------|----------|
| Installation required | Yes | No |
| Start Menu shortcuts | Yes | No |
| Uninstaller | Yes | Delete file |
| Auto-updates (future) | Possible | Manual |
| File size | ~100MB | ~150MB |
| Admin rights needed | No (per-user) | No |
| Best for | Regular users | USB/testing |

---

## Customizing the Installer

### Change Install Behavior

Edit `package.json` → `build` → `nsis` section:

```json
"nsis": {
  "oneClick": false,
  "perMachine": false,
  "allowToChangeInstallationDirectory": true,
  "createDesktopShortcut": true,
  "createStartMenuShortcut": true
}
```

### Add License Agreement

1. Create `LICENSE.txt` in project root
2. Add to `package.json`:
   ```json
   "nsis": {
     "license": "LICENSE.txt"
   }
   ```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.3 | Dec 2025 | Current release |

---

## See Also

- [Tradebook_Windows_Installer_QuickStart_Guide.md](Tradebook_Windows_Installer_QuickStart_Guide.md) - How to install and run
- [TradeBook_Portable_Version_Builder_Guide.md](TradeBook_Portable_Version_Builder_Guide.md) - Build the portable version
