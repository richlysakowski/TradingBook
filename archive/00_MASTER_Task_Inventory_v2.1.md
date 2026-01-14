# TradingBook - Master Task Inventory v2.1
**Version**: v2.1  
**Last Updated**: January 14, 2026 12:00 UTC

Note: This file is an incremental update (v2.1) that preserves the canonical `00_MASTER_Task_Inventory.md` contents and appends additional tasks and analysis findings from `TASK_INVENTORY_ANALYSIS_2026.01.12.md`.

---

## Summary of Change (v2.1)
- Added: `IPC Communication Security Verification` task (extracted from Jan 12 analysis)
- Added: `Administrative note` referencing `TASK_INVENTORY_ANALYSIS_2026.01.12.md` (audit performed Jan 12, 2026)
- Did not overwrite any existing files. This is a new incremental master file for v2.1.

---

## Additional Tasks Extracted from TASK_INVENTORY_ANALYSIS_2026.01.12.md

### A. IPC Communication Security Verification (Added: January 8, 2026; extracted into v2.1 on January 14, 2026)
- **Status**: 🟡 OPEN
- **Description**: Verify and test IPC communication security across Electron preload and main process. Ensure `contextIsolation: true`, minimize surface area exposed to renderer, and validate inputs received via IPC.
- **Actions**:
  1. Verify `public/preload.js` exposes only approved methods and uses `contextBridge.exposeInMainWorld` correctly.
  2. Confirm `public/electron.js` loads the correct `preload` script path when creating BrowserWindow.
  3. Add unit/integration tests for IPC handlers using a mock `ipcRenderer`/`ipcMain` environment.
  4. Add a security checklist to `docs/DEVELOPER_GUIDE.md` documenting allowed IPC methods and expected input validation.
  5. Add automated audit script to flag any `ipcRenderer.on` listeners that pass arbitrary callbacks or unvalidated payloads.
- **Files to Check**: `public/preload.js`, `public/electron.js`, `src/components/*` (for usage of `window.electronAPI`)
- **Priority**: P3 (DevEx/Security) but move to P1 if it's blocking production builds

### B. Administrative / Audit Reference
- **Source**: `TASK_INVENTORY_ANALYSIS_2026.01.12.md` (Analysis Date: January 12, 2026)
- **Note**: The Jan 12 analysis confirmed no tasks were dropped and recommended `00_MASTER_Task_Inventory.md` as canonical. This v2.1 file only adds the IPC security verification task and a reference to the audit.

---

## How this file relates to existing task files
- `00_MASTER_Task_Inventory.md` — Primary canonical master task list (recommended by the Jan 12 analysis). This file should remain the canonical record if present.
- `00_MASTER_Task_Inventory_v2.1.md` — Incremental update containing additional IPC security verification task and audit reference; created without overwriting any existing files.
- `00_MASTER_Task_Inventory-CURRENT-STATUS_2026.01.08.md` — Keep as a verification/audit snapshot (reference only).
- `TASK_INVENTORY_ANALYSIS_2026.01.12.md` — Audit report confirming consolidation; referenced here.

---

## Next steps (optional)
- If you want, I can:
  - Open `00_MASTER_Task_Inventory.md` if it exists and merge this v2.1 content into it (creating a new v2.1 entry without overwriting), OR
  - Add the IPC task into `00_MASTER_Task_Inventory.md` directly if you approve (will not overwrite file, only append), OR
  - Create a `CHANGELOG.md` entry recording v2.1.

---

**Created by**: TradingBook dev assistant (automation)
**Created on**: January 14, 2026 12:00 UTC
