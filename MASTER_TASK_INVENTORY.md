# TradingBook - Master Task Inventory
**Last Updated: December 19, 2025**

---

## 📊 TASK SUMMARY STATISTICS

- **Total Tasks**: 67
- **Completed**: 8
- **High Priority**: 12
- **Medium Priority**: 18
- **Low Priority**: 10
- **Redundant/Duplicates Flagged**: 7
- **Categories**: 11

---

## ✅ COMPLETED TASKS (DO NOT REPEAT)

### CSV Import & Futures Support
1. ✅ **DONE** - Fixed action validation for futures (Buy to Open, Sell to Close patterns)
2. ✅ **DONE** - Fixed futures symbol detection with month/year codes (NQH5, ESZ5, etc.)
3. ✅ **DONE** - Added point value fetching via IPC
4. ✅ **DONE** - Fixed IPC communication for getFuturesPointValue
5. ✅ **DONE** - Database schema updates (point_value, contract_currency columns)
6. ✅ **DONE** - Created futures_contracts table with default contracts
7. ✅ **DONE** - Fixed race condition in addBulkTrades()
8. ✅ **DONE** - Created browser-only development mode with mock electronAPI

---

## 🔴 HIGH PRIORITY TASKS (P0 - Critical)

### Category: Bug Fixes & Critical Issues

#### 1. **BUGFIX: electronAPI undefined error**
- **Status**: 🔴 OPEN
- **Description**: Error getting debug status - window.electronAPI is undefined
- **Impact**: Blocks debugging functionality
- **Files**: Check preload.js, electron.js, and components using electronAPI
- **Priority**: P0
- **Source**: 00_Enhancements_TBD.md

#### 2. **Analytics Page - No Data Display**
- **Status**: 🔴 OPEN (Duplicate tracking below)
- **Description**: Analytics page shows no data despite trades being imported
- **Impact**: Blocks user from viewing P&L analysis and charts
- **Root Causes**:
  - Analytics component not fetching trades correctly
  - getTrades() method may not return data to Analytics
  - Data aggregation logic (P&L calculations) may have issues
  - Chart.js initialization may fail silently
- **Files**: src/components/Analytics.tsx, src/components/Dashboard.tsx
- **Priority**: P0
- **Source**: 00_WORK_IN_PROGRESS.md

#### 3. **Entry/Exit Price Import Verification**
- **Status**: 🔴 OPEN
- **Description**: Verify CSV structure includes exit prices; currently only mapping entryPrice
- **Impact**: P&L calculations may be incomplete or incorrect
- **Action Items**:
  - Review sample CSV files in sample_data/
  - Check actual CSV column headers and data
  - Update CSVImport if exitPrice column exists
  - Verify P&L calculation depends on both entry AND exit prices
  - Document expected CSV format in README
- **Files**: src/components/CSVImport.tsx (lines 177-187), src/types/Trade.ts
- **Priority**: P0
- **Source**: 00_WORK_IN_PROGRESS.md

#### 4. **Fix Launch Scripts for Portable & Installer**
- **Status**: 🔴 OPEN
- **Description**: Update all scripts to work with newly built portable and native Windows Installer
- **Current Issue**: start_tradingbook.bat not recognized (needs .\ prefix in PowerShell)
- **Files**: start_tradingbook.bat, build_portable.bat, build_installer.bat, create-installs.sh
- **Priority**: P0
- **Source**: 00_Enhancements_TBD.md

---

## 🟠 MEDIUM PRIORITY TASKS (P1 - Important)

### Category: Schwab CSV Import Enhancements

#### 5. **Make Import Capabilities Fault-Tolerant & Robust**
- **Status**: 🟠 OPEN
- **Description**: Improve error handling, validation, and user feedback for CSV imports
- **Requirements**:
  - Better error messages with specific line numbers
  - Graceful handling of malformed data
  - Skip invalid rows instead of failing entire import
  - Validation preview before import
  - Progress indicators for large files
- **Files**: src/components/CSVImport.tsx
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md, 00_WORK_IN_PROGRESS.md (Category E)

#### 6. **Support Tab-Separated Values (TSV)**
- **Status**: 🟠 OPEN
- **Description**: Schwab exports TSV files with ".csv" extension - need to auto-detect and parse
- **Requirements**:
  - Auto-detect delimiter (comma vs tab)
  - Parse TSV correctly
  - Update parsing instructions in Import Dialog
- **Files**: src/components/CSVImport.tsx
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

#### 7. **Add Column Formatting Instructions in Import Dialog**
- **Status**: 🟠 OPEN
- **Description**: Display expected CSV format in Import Dialog Box
- **Requirements**:
  - List required columns: Date, Action, Symbol, Quantity, Price
  - Show optional columns: Fees & Comm, Amount, Description
  - Provide example row
  - Link to sample CSV files
- **Files**: src/components/CSVImport.tsx, src/components/Settings.tsx
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

#### 8. **Create Sample Schwab CSV with 100+ Stock Trades**
- **Status**: 🟠 OPEN
- **Description**: Generate comprehensive test data for validation
- **Requirements**:
  - 100+ stock trades in Schwab format
  - Include various scenarios: winning/losing trades, fees, partial fills
  - Both tab-separated and comma-separated versions
- **Location**: sample_data/
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

#### 9. **Parse Schwab Account Statement Headers**
- **Status**: 🟠 OPEN
- **Description**: Current error - "Missing required columns" when parsing account statement header rows
- **Error Example**: "Account Statement for D-70029726 (ira) since 10/28/25 through 11/26/25"
- **Requirements**:
  - Skip header rows until data table found
  - Detect actual data start row
  - Handle multiple table formats in same file
- **Files**: src/components/CSVImport.tsx
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

### Category: Futures Trading Support

#### 10. **Futures Point-Values Mapping Table**
- **Status**: 🟠 OPEN (Partially Complete - Default contracts added)
- **Description**: Create comprehensive mapping table for futures contract point values
- **Requirements**:
  - Focus on Top 10 contracts by volume
  - Default standard values for popular contracts
  - User-editable table for less common contracts
  - UI for adding/editing point values
- **Contracts**: ES, NQ, YM, RTY, CL, GC, ZB, ZN, 6E, 6J, MES, MNQ, MYM, M2K, MCL, MGC, SIL
- **Files**: src/database/Database.js (futures_contracts table), src/components/Settings.tsx
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

#### 11. **🔁 DUPLICATE: Support Futures Trades**
- **Status**: 🟡 DUPLICATE (Already completed - see tasks #1-8)
- **Description**: Parse Schwab CSV format for Futures trades
- **Note**: This is redundant with completed futures CSV import support
- **Action**: ❌ **FLAG FOR REMOVAL**
- **Source**: 00_Enhancements_TBD.md

### Category: UI/UX Improvements

#### 12. **UI Layout - Center Controls**
- **Status**: 🟠 OPEN
- **Description**: Center import buttons and search fields for better organization
- **Requirements**:
  - Center-align import buttons and search field in Dashboard
  - Add consistent spacing/padding
  - Consider collapsible sections for secondary controls
  - Ensure responsive layout on smaller screens
  - Improve visual hierarchy
- **Files**: src/components/Dashboard.tsx, src/App.tsx, Tailwind CSS classes
- **Priority**: P1
- **Source**: 00_WORK_IN_PROGRESS.md

#### 13. **Settings Page Import Functionality**
- **Status**: 🟠 OPEN
- **Description**: Verify and fix import button in Settings page
- **Requirements**:
  - Test import function in Settings.tsx
  - Verify IPC method usage
  - Test with sample CSV file
  - Ensure user feedback (success/error messages)
  - Check file picker dialog works on Windows
- **Files**: src/components/Settings.tsx
- **Priority**: P1
- **Source**: 00_WORK_IN_PROGRESS.md

#### 14. **TradeList.tsx Layout Improvements**
- **Status**: 🟡 PARTIALLY COMPLETE
- **Description**: Further refinements to symbol/badge/point value display
- **Current State**: Symbol + badge horizontal, point value below
- **Additional Improvements**:
  - Responsive column widths
  - Sortable columns
  - Filterable columns
- **Files**: src/components/TradeList.tsx
- **Priority**: P1
- **Source**: 00_WORK_IN_PROGRESS.md

### Category: Build & Deployment

#### 15. **Update Portable Build Scripts (v1.0.4)**
- **Status**: 🟠 OPEN
- **Description**: Create new portable application runtime kit
- **Requirements**:
  - Run build_portable.bat
  - Save as v1.0.4 in portable_version_kit_v1.0.4/
  - Add semantic version number and date stamp
  - Update startup script with version info
- **Files**: build_portable.bat, portable_version_kit_v1.0.4/
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

#### 16. **Update Windows Installer Build Scripts**
- **Status**: 🟠 OPEN
- **Description**: Create new native Windows Installer for latest version
- **Files**: build_installer.bat, scripts/
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

#### 17. **Update About Dialog Box**
- **Status**: 🟠 OPEN
- **Description**: Add maintainer info and documentation links
- **Requirements**:
  - Add Rich Lysakowski, Ph.D. as maintainer for futures version
  - Link to QuickStart Guide in Rich's GitHub repo
  - Link to User Manual documentation
  - Add version number and date stamp
- **Files**: src/components/Settings.tsx or create src/components/About.tsx
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

#### 18. **Update Release Notes (v1.0.4)**
- **Status**: 🟠 OPEN
- **Description**: Document all changes since last release
- **Requirements**:
  - Version number: 1.0.4
  - Date stamp: December 2025
  - List of new features (futures support, CSV import improvements)
  - List of bug fixes
  - Known issues
- **Files**: Create RELEASE_NOTES.md or update README.md
- **Priority**: P1
- **Source**: 00_Enhancements_TBD.md

---

## 🟡 LOW-MEDIUM PRIORITY TASKS (P2 - Nice to Have)

### Category: Application Features

#### 19. **Support Options Trades**
- **Status**: 🟡 OPEN
- **Description**: Add support for importing and tracking options trades
- **Requirements**:
  - Parse options symbols (ticker + expiration + strike + type)
  - Handle options P&L calculations (premium, assignment, exercise)
  - Display options chains in UI
  - Support covered calls, protective puts, spreads
- **Files**: src/types/Trade.ts, src/components/CSVImport.tsx, src/database/Database.js
- **Priority**: P2
- **Source**: 00_Enhancements_TBD.md

#### 20. **Add QuickStart Utility and Guide**
- **Status**: 🟡 OPEN
- **Description**: Create simple launch utility and QuickStart Guide
- **Requirements**:
  - One-click launcher for portable version
  - Interactive setup wizard for first-time users
  - QuickStart Guide PDF/HTML
  - Sample data pre-loaded for demo
- **Files**: Create scripts/quickstart.bat, docs/QuickStart_Guide.md
- **Priority**: P2
- **Source**: 00_Enhancements_TBD.md

#### 21. **Intraday Futures Trading Support**
- **Status**: 🟡 OPEN (NEW - Category D)
- **Description**: Add support for short-term (intraday) futures trading analytics
- **Requirements**:
  - Import intraday tick/1-min/5-min candle data
  - Calculate intraday P&L by session (overnight vs regular hours)
  - Time-weighted analytics (average hold time, session P&L)
  - Support multiple contracts traded same day
  - Intraday position sizing analysis
- **Files**: New component src/components/IntradayAnalytics.tsx, Database.js extensions
- **Priority**: P2
- **Source**: User request (Category D)

#### 22. **Better Analytics for Intraday P&L**
- **Status**: 🟡 OPEN (NEW - Category D)
- **Description**: Enhanced reporting for intraday trading performance
- **Requirements**:
  - Session-based P&L (by trading session/day part)
  - Time-of-day analysis (best/worst trading hours)
  - Win rate by time bucket (morning vs afternoon)
  - Average profit per trade duration
  - Intraday drawdown tracking
- **Files**: src/components/Analytics.tsx, new src/components/IntradayReports.tsx
- **Priority**: P2
- **Source**: User request (Category D)

---

## 🟢 LOW PRIORITY TASKS (P3 - Future Enhancements)

### Category: Developer Experience

#### 23. **Fix Deprecation Warning on Startup**
- **Status**: 🟢 OPEN
- **Description**: Webpack dev server middleware deprecation warnings
- **Error**: 'onAfterSetupMiddleware' and 'onBeforeSetupMiddleware' options deprecated
- **Solution**: Migrate to 'setupMiddlewares' option in webpack config
- **Files**: Check react-scripts config or create custom webpack.config.js override
- **Priority**: P3
- **Source**: 00_Enhancements_TBD.md

#### 24. **Browser Cache / Hot Reload Issues**
- **Status**: 🟢 OPEN
- **Description**: Need Ctrl+F5 to clear cache between imports
- **Solutions**:
  - Implement React hot reload properly
  - Add cache-busting headers
  - Document manual browser refresh strategy
  - Consider Redux/Zustand for global state management
- **Files**: webpack config, src/index.tsx
- **Priority**: P3
- **Source**: 00_WORK_IN_PROGRESS.md

### Category: Logging & Debugging (NEW - Category B)

#### 25. **Implement Full Debug Mode**
- **Status**: 🟢 OPEN (NEW - Category B)
- **Description**: Add comprehensive debug mode for troubleshooting
- **Requirements**:
  - Toggle debug mode in Settings
  - Verbose logging to file and console
  - Performance metrics tracking
  - Network/IPC call logging
  - Database query logging with execution times
  - Memory usage monitoring
- **Files**: Create src/utils/DebugLogger.ts, update all components
- **Priority**: P3
- **Source**: User request (Category B)

#### 26. **Comprehensive Operation Logging**
- **Status**: 🟢 OPEN (NEW - Category B)
- **Description**: Log all operations to file for audit trail
- **Requirements**:
  - Log file rotation (daily/size-based)
  - Log levels (DEBUG, INFO, WARN, ERROR)
  - Structured logging (JSON format)
  - Include timestamps, user actions, system events
  - CSV import operations with row-by-row status
  - Database operations (CREATE, UPDATE, DELETE)
- **Files**: Enhance src/utils/debugLogger.js, add logs/ directory support
- **Priority**: P3
- **Source**: User request (Category B)

#### 27. **Enhanced Error Messages**
- **Status**: 🟢 OPEN (NEW - Category B)
- **Description**: Make error messages more informative and actionable
- **Requirements**:
  - Include error codes for easy reference
  - Suggest corrective actions
  - Link to documentation/FAQ
  - Include context (file name, line number, operation)
  - User-friendly language (avoid technical jargon)
- **Files**: All components with error handling
- **Priority**: P3
- **Source**: User request (Category B)

#### 28. **Schwab Import Comprehensive Logging**
- **Status**: 🟢 OPEN (NEW - Category E)
- **Description**: Fully-logged, fault-tolerant Schwab import process
- **Requirements**:
  - Log each row parsed from CSV
  - Log validation results (pass/fail with reasons)
  - Log database insertion status
  - Generate import summary report
  - Export failed rows to separate CSV for review
  - Include import session ID for tracking
- **Files**: src/components/CSVImport.tsx, src/utils/importLogger.ts (new)
- **Priority**: P3
- **Source**: User request (Category E)

---

## 📚 DOCUMENTATION TASKS (P2-P3)

### Category: SDLC Documentation (NEW - Category C)

#### 29. **Extract Requirements from Codebase**
- **Status**: 🟡 OPEN
- **Description**: Backfill functional requirements from implemented code
- **Requirements**:
  - Ingest entire codebase
  - Use requirements template provided
  - Document all implemented functionality
  - Create Functional Requirements Specification
- **Files**: Create docs/FUNCTIONAL_REQUIREMENTS.md
- **Priority**: P2
- **Source**: 00_Enhancements_TBD.md, User request (Category C)

#### 30. **Full SDLC Documentation (7D Agile-Style)**
- **Status**: 🟡 OPEN (NEW - Category C)
- **Description**: Create comprehensive SDLC documentation using 7D Agile templates
- **Requirements**:
  - **Discover**: Requirements gathering, user stories
  - **Design**: Architecture diagrams, database schema, API design
  - **Develop**: Coding standards, branching strategy
  - **Debug**: Testing strategy, bug tracking
  - **Deploy**: Build/release process, environment setup
  - **Deliver**: Release notes, user documentation
  - **Data**: Analytics, metrics, KPIs
- **Files**: Create docs/SDLC/ directory with all templates
- **Priority**: P2
- **Source**: User request (Category C)

#### 31. **User Manual & QuickStart Guide**
- **Status**: 🟡 OPEN
- **Description**: Create comprehensive user documentation
- **Requirements**:
  - QuickStart Guide (10 pages max)
  - Full User Manual (detailed feature documentation)
  - Video tutorials (optional)
  - FAQ section
  - Troubleshooting guide
- **Files**: docs/USER_MANUAL.md, docs/QUICKSTART_GUIDE.md
- **Priority**: P2
- **Source**: 00_Enhancements_TBD.md

#### 32. **Developer Documentation**
- **Status**: 🟡 OPEN
- **Description**: Document codebase architecture and development process
- **Requirements**:
  - Architecture overview
  - Database schema documentation
  - IPC communication patterns
  - Component hierarchy
  - Build process explanation
  - Contribution guidelines
- **Files**: docs/DEVELOPER_GUIDE.md, docs/ARCHITECTURE.md
- **Priority**: P2
- **Source**: Implied by Category C requirements

---

## 🔮 FUTURE FEATURES (P4 - Backlog)

### Category: Schwab API Integration

#### 33. **Develop Schwab Developer API Application**
- **Status**: 🔵 BACKLOG
- **Description**: Create application to access Schwab account data programmatically
- **Requirements**:
  - Implement OAuth 2.0 authentication
  - Fetch account balances
  - Retrieve transaction history
  - Download trade confirmations
  - Real-time position monitoring
- **Files**: Create src/api/schwabAPI.ts
- **Priority**: P4
- **Source**: 00_Enhancements_TBD.md

#### 34. **Get Schwab API Access Approved**
- **Status**: 🔵 BACKLOG
- **Description**: Register TradingBook with Schwab Developer Portal
- **Requirements**:
  - Submit application for API access
  - Get approval for paper trading environment
  - Get approval for live trading environment
  - Implement rate limiting
  - Handle API errors gracefully
- **Priority**: P4
- **Source**: 00_Enhancements_TBD.md

---

## ⚠️ REDUNDANT/DUPLICATE TASKS (FLAG FOR REMOVAL)

### 🔁 Duplicates Identified

1. **🔁 DUPLICATE #11: Support Futures Trades**
   - **Original**: Tasks #1-8 (Completed CSV Import & Futures Support)
   - **Reason**: Futures CSV import already implemented
   - **Action**: ❌ **REMOVE FROM 00_Enhancements_TBD.md**

2. **🔁 SIMILAR: "Make Import Robust" appears in multiple forms**
   - Task #5: Make Import Capabilities Fault-Tolerant & Robust
   - Task #9: Parse Schwab Account Statement Headers (specific case)
   - Task #28: Schwab Import Comprehensive Logging (logging aspect)
   - **Action**: ✅ **KEEP ALL** - Different aspects of robustness (validation, parsing, logging)

3. **🔁 SIMILAR: "Add Instructions" appears twice**
   - Task #7: Add Column Formatting Instructions in Import Dialog
   - From 00_Enhancements_TBD.md: "Add instructions in Import Dialog Box"
   - **Action**: ✅ **MERGE** - Same task, single implementation

4. **🔁 SIMILAR: "Update Build Scripts"**
   - Task #4: Fix Launch Scripts for Portable & Installer (fix existing)
   - Task #15: Update Portable Build Scripts (create v1.0.4)
   - Task #16: Update Windows Installer Build Scripts (create v1.0.4)
   - **Action**: ✅ **KEEP ALL** - Related but distinct tasks

5. **🔁 POTENTIAL OVERLAP: Analytics Issues**
   - Task #2: Analytics Page - No Data Display (current bug)
   - Task #21-22: Intraday Analytics (new feature)
   - **Action**: ✅ **KEEP BOTH** - Bug fix vs new feature

6. **🔁 REDUNDANT: QuickStart Documentation**
   - Task #20: Add QuickStart Utility and Guide
   - Task #31: User Manual & QuickStart Guide
   - **Action**: ✅ **MERGE** - Create one comprehensive QuickStart as part of Task #31

7. **🔁 SIMILAR: Debug/Logging Features**
   - Task #25: Implement Full Debug Mode
   - Task #26: Comprehensive Operation Logging
   - Task #27: Enhanced Error Messages
   - Task #28: Schwab Import Comprehensive Logging
   - **Action**: ✅ **KEEP ALL BUT GROUP** - Related debugging infrastructure, implement together

---

## 📋 TASK CATEGORIES SUMMARY

1. **Bug Fixes & Critical Issues** (4 tasks) - P0
2. **Schwab CSV Import Enhancements** (5 tasks) - P1
3. **Futures Trading Support** (2 tasks) - P1-P2
4. **UI/UX Improvements** (3 tasks) - P1
5. **Build & Deployment** (4 tasks) - P1
6. **Application Features** (3 tasks) - P2
7. **Logging & Debugging** (4 tasks) - P3
8. **Documentation** (4 tasks) - P2-P3
9. **Schwab API Integration** (2 tasks) - P4 (Backlog)
10. **Developer Experience** (2 tasks) - P3
11. **Completed** (8 tasks) - ✅ DONE

**Total Active Tasks**: 34 (excluding completed and duplicates)

---

## 🎯 RECOMMENDED EXECUTION ORDER

### Sprint 1: Critical Fixes (Week 1-2)
1. Task #1: Fix electronAPI undefined error
2. Task #2: Analytics Page - No Data Display
3. Task #3: Entry/Exit Price Import Verification
4. Task #4: Fix Launch Scripts

### Sprint 2: Import Robustness (Week 3-4)
5. Task #5: Make Import Fault-Tolerant
6. Task #6: Support TSV
7. Task #7: Add Column Formatting Instructions
8. Task #9: Parse Schwab Account Statement Headers
9. Task #8: Create Sample CSV with 100+ trades

### Sprint 3: UI & Build (Week 5-6)
10. Task #12: UI Layout - Center Controls
11. Task #13: Settings Page Import
12. Task #15-18: Update Build Scripts, About Dialog, Release Notes

### Sprint 4: Features & Documentation (Week 7-8)
13. Task #10: Futures Point-Values Mapping Table UI
14. Task #21-22: Intraday Futures Trading Support
15. Task #29: Extract Requirements from Codebase
16. Task #31: User Manual & QuickStart Guide

### Sprint 5: Quality & DevEx (Week 9-10)
17. Task #25-28: Debug Mode, Logging, Enhanced Error Messages
18. Task #30: Full SDLC Documentation
19. Task #23-24: Fix Deprecation Warnings, Hot Reload

### Sprint 6: Future Features (Backlog)
20. Task #19: Support Options Trades
21. Task #33-34: Schwab API Integration

---

## 📝 NOTES

- **Source Documents**: 00_Enhancements_TBD.md, 00_WORK_IN_PROGRESS.md
- **Priority Scale**: P0 (Critical) → P1 (High) → P2 (Medium) → P3 (Low) → P4 (Backlog)
- **Status Indicators**: 🔴 OPEN (P0), 🟠 OPEN (P1), 🟡 OPEN (P2), 🟢 OPEN (P3), 🔵 BACKLOG (P4), ✅ DONE
- **Duplicate Actions**: ❌ REMOVE, ✅ MERGE, ✅ KEEP ALL

---

## 🔄 MAINTENANCE

This document should be updated:
- Weekly during active development
- After completing each task (move to ✅ COMPLETED section)
- When new requirements emerge
- Before sprint planning meetings
- After user feedback sessions

**Next Review Date**: December 26, 2025
