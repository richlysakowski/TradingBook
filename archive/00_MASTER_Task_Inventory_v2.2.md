# TradingBook - Master Task Inventory v2.2
**Version**: v2.2  
**Last Updated**: January 14, 2026 14:00 UTC

This is an incremental, non-destructive update. It preserves the canonical `00_MASTER_Task_Inventory.md` concept and appends items and administrative actions discovered during the Jan 12, 2026 analysis and subsequent repository review (Jan 14, 2026). This file does NOT overwrite any existing files.

---

## Summary of Changes (v2.2)
- Carried forward all content from `00_MASTER_Task_Inventory_v2.1.md` (IPC task + audit reference).
- Added: Repository housekeeping actions discovered during git audit (files deleted in repo) and recommended archival actions.
- Added: Guidance for restoring or recovering `MASTER_TASK_INVENTORY.md` from git history if needed.

---

## Additions from v2.1 (IPC Security Task)
(See `00_MASTER_Task_Inventory_v2.1.md` for full details; included here for completeness)

### A. IPC Communication Security Verification (Added: January 8, 2026)
- **Status**: 🟡 OPEN
- **Description**: Verify and test IPC communication security across Electron preload and main process. Ensure `contextIsolation: true`, minimize surface area exposed to renderer, and validate inputs received via IPC.
- **Actions**:
  1. Verify `public/preload.js` exposes only approved methods and uses `contextBridge.exposeInMainWorld` correctly.
  2. Confirm `public/electron.js` loads the correct `preload` script path when creating BrowserWindow.
  3. Add unit/integration tests for IPC handlers using a mock `ipcRenderer`/`ipcMain` environment.
  4. Add a security checklist to `docs/DEVELOPER_GUIDE.md` documenting allowed IPC methods and expected input validation.
  5. Add automated audit script to flag any `ipcRenderer.on` listeners that pass arbitrary callbacks or unvalidated payloads.
- **Files to Check**: `public/preload.js`, `public/electron.js`, `src/components/*` (for usage of `window.electronAPI`)
- **Priority**: P3 (raise to P1 if blocking product releases)

---

## Repository Audit Findings (Jan 14, 2026)
- `git status` shows multiple deleted files including `MASTER_TASK_INVENTORY.md` and some docs/build scripts.
- The following deleted files were noted in the repo index (examples):
  - `MASTER_TASK_INVENTORY.md` (deleted)
  - `00_Enhancements_TBD.md` (deleted)
  - `00_WORK_IN_PROGRESS.md` (deleted)
  - Several build docs and scripts

### Recommended Immediate Actions
1. Restore any accidentally deleted canonical files from git history if needed:
   ```powershell
   git checkout -- MASTER_TASK_INVENTORY.md
   git checkout -- 00_Enhancements_TBD.md
   git checkout -- 00_WORK_IN_PROGRESS.md
   ```
   - If files were intentionally removed, move them to an `archive/` folder in the repo and commit the archive.
2. Add `00_MASTER_Task_Inventory_v2.2.md` to version control when ready:
   ```powershell
   git add 00_MASTER_Task_Inventory_v2.2.md
   git commit -m "chore: add master task inventory v2.2 (IPC security + repo audit notes)"
   ```
3. Create an `archive/` folder for superseded materials and move any deleted-but-useful docs there if they were removed inadvertently.

---

## Administrative Notes & Audit Reference
- The Jan 12, 2026 analysis (`TASK_INVENTORY_ANALYSIS_2026.01.12.md`) recommended `00_MASTER_Task_Inventory.md` as canonical. Because `MASTER_TASK_INVENTORY.md` was removed from the git index, this v2.2 file preserves the audit findings and adds operational steps to recover or archive the deleted files.
- Keep `TASK_INVENTORY_ANALYSIS_2026.01.12.md` as a verification artifact (do not delete).

---

## Next Optional Steps (I can perform for you)
- Restore deleted files from git if they were removed accidentally.
- Add `00_MASTER_Task_Inventory_v2.2.md` to git and commit.
- Move superseded files to `archive/` and commit the archive.
- Merge `00_MASTER_Task_Inventory_v2.2.md` contents into a single canonical file (if you want a single canonical record) while preserving history.

---

**Created by**: TradingBook dev assistant  
**Created on**: January 14, 2026 14:00 UTC
