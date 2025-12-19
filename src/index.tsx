import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Ensure window.electronAPI exists (for development without Electron)
if (!window.electronAPI) {
  console.warn('⚠️ window.electronAPI not found - running in browser-only mode');
  
  // In-memory store for browser-only development
  let inMemoryTrades: any[] = [];
  let nextTradeId = 1;
  
  // Create a minimal mock for development
  (window as any).electronAPI = {
    // Futures contracts management
    getFuturesContracts: async () => [
      { symbol: 'NQ', description: 'Nasdaq 100 E-mini', point_value: 20, currency: 'USD' },
      { symbol: 'NQH5', description: 'Nasdaq 100 E-mini (March 2025)', point_value: 20, currency: 'USD' },
      { symbol: 'ES', description: 'S&P 500 E-mini', point_value: 50, currency: 'USD' }
    ],
    addFuturesContract: async () => ({}),
    updateFuturesContract: async () => ({}),
    deleteFuturesContract: async () => ({}),
    getFuturesPointValue: async (symbol: string) => {
      const contracts: any = {
        'NQ': 20, 'NQH5': 20, 'NQZ5': 20,
        'ES': 50, 'YM': 5, 'RTY': 50,
        'CL': 1000, 'GC': 100
      };
      return contracts[symbol] || null;
    },
    
    // File operations
    onImportTrades: (callback: any) => { console.warn('onImportTrades not available'); },
    onExportData: (callback: any) => { console.warn('onExportData not available'); },
    onToggleTheme: (callback: any) => { console.warn('onToggleTheme not available'); },
    
    // Database operations
    saveTrade: async (trade: any) => {
      const savedTrade = { id: nextTradeId++, ...trade };
      inMemoryTrades.push(savedTrade);
      console.log('✅ Trade saved (in-memory):', savedTrade);
      return savedTrade;
    },
    saveTradesBulk: async (trades: any[]) => {
      const savedTrades = trades.map(trade => {
        const savedTrade = { id: nextTradeId++, ...trade };
        inMemoryTrades.push(savedTrade);
        return savedTrade;
      });
      console.log(`✅ ${savedTrades.length} trades saved (in-memory)`);
      return savedTrades;
    },
    getTrades: async () => {
      console.log('📊 Returning', inMemoryTrades.length, 'trades from in-memory store');
      return inMemoryTrades;
    },
    updateTrade: async (id: number, trade: any) => {
      const index = inMemoryTrades.findIndex(t => t.id === id);
      if (index >= 0) {
        inMemoryTrades[index] = { ...inMemoryTrades[index], ...trade };
        return inMemoryTrades[index];
      }
      throw new Error('Trade not found');
    },
    deleteTrade: async (id: number) => {
      const index = inMemoryTrades.findIndex(t => t.id === id);
      if (index >= 0) {
        inMemoryTrades.splice(index, 1);
      }
    },
    
    // Analytics
    getPerformanceMetrics: async () => ({}),
    getCalendarData: async () => [],
    
    // Daily notes
    saveDailyNote: async () => { throw new Error('Not available in browser-only mode'); },
    getDailyNote: async () => null,
    deleteDailyNote: async () => { throw new Error('Not available in browser-only mode'); },
    
    // Settings
    saveSettings: async () => ({}),
    loadSettings: async () => ({}),
    
    // Backup/Restore
    backupDatabase: async () => { throw new Error('Not available in browser-only mode'); },
    restoreDatabase: async () => { throw new Error('Not available in browser-only mode'); },
    purgeDatabase: async () => { throw new Error('Not available in browser-only mode'); },
    
    // CSV Import/Export
    exportCsv: async () => { throw new Error('Not available in browser-only mode'); },
    importCsv: async () => { throw new Error('Not available in browser-only mode'); },
    
    // Debug Logger
    setDebugEnabled: async () => { throw new Error('Not available in browser-only mode'); },
    
    // Database status debugging
    getDatabaseStatus: async () => ({ status: 'browser-only' }),
    
    // P&L Matching
    matchPnL: async () => { throw new Error('Not available in browser-only mode'); },
    
    // Update checking
    checkForUpdates: async () => { throw new Error('Not available in browser-only mode'); },
    
    // External links
    openExternal: async () => { throw new Error('Not available in browser-only mode'); },
    
    // System paths
    getDownloadsPath: async () => '',
    
    // Yahoo Finance API
    fetchStockData: async () => ({}),
    
    // Database refresh events (to avoid window reloads)
    onDatabasePurged: (callback: any) => { console.warn('onDatabasePurged not available'); },
    onDatabaseRestored: (callback: any) => { console.warn('onDatabaseRestored not available'); },
    onDatabaseError: (callback: any) => { console.warn('onDatabaseError not available'); },
    
    // Cleanup function for database listeners
    removeDatabaseListeners: () => {}
  };
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
