import React, { useState, useEffect } from 'react';
import { MemoryRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import TradeList from './components/TradeList';
import TradeForm from './components/TradeForm';
import Analytics from './components/Analytics';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';
import { Trade } from './types/Trade';
import './App.css';

const App: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      console.log('App mounting, initializing...');
      // Load initial data
      loadSettings();
      loadTrades();
      
      // Set up electron listeners
      if (window.electronAPI) {
        console.log('electronAPI available, setting up listeners...');
        window.electronAPI.onToggleTheme(() => {
          setDarkMode(prev => !prev);
        });
        
        // Listen for database refresh events for other operations (restore, errors)
        const handleDatabaseRestored = () => {
          console.log('Database restored - refreshing data...');
          loadTrades();
          loadSettings();
        };
        
        const handleDatabaseError = (error: string) => {
          console.error('Database error:', error);
          loadTrades();
        };
        
        // Add event listeners (purge now uses window reload)
        console.log('Setting up database event listeners...');
        
        if (window.electronAPI.onDatabaseRestored) {
          console.log('Setting up onDatabaseRestored listener');
          window.electronAPI.onDatabaseRestored(handleDatabaseRestored);
        }
        
        if (window.electronAPI.onDatabaseError) {
          console.log('Setting up onDatabaseError listener');
          window.electronAPI.onDatabaseError(handleDatabaseError);
        }
      } else {
        console.warn('electronAPI not available (running in browser dev mode)');
      }
      
      return () => {
        // Cleanup listeners if available
        window.electronAPI?.removeDatabaseListeners?.();
      };
    } catch (err) {
      console.error('Error in App initialization:', err);
      setError(String(err));
    }
  }, []);

  const loadSettings = async () => {
    try {
      if (window.electronAPI) {
        const savedSettings = await window.electronAPI.loadSettings();
        setSettings(savedSettings);
        if (savedSettings.darkMode !== undefined) {
          setDarkMode(savedSettings.darkMode);
        }
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const loadTrades = async () => {
    try {
      setLoading(true);
      if (window.electronAPI) {
        const tradesData = await window.electronAPI.getTrades({});
        setTrades(tradesData);
      }
    } catch (error) {
      console.error('Failed to load trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const addTrade = async (trade: Omit<Trade, 'id'>) => {
    try {
      if (window.electronAPI) {
        const newTrade = await window.electronAPI.saveTrade(trade);
        setTrades(prev => [...prev, newTrade]);
      }
    } catch (error) {
      console.error('Failed to add trade:', error);
    }
  };

  const addBulkTrades = async (newTrades: Omit<Trade, 'id'>[]) => {
    try {
      console.log(`📥 addBulkTrades called with ${newTrades.length} trades`);
      if (window.electronAPI && newTrades.length > 0) {
        console.log('🔄 Calling saveTradesBulk...');
        // Use bulk save to prevent excessive re-renders and flashing
        // Note: electron.js will reload the window after saving, so we don't need to update state here
        await window.electronAPI.saveTradesBulk(newTrades);
        console.log('✅ saveTradesBulk completed');
      } else {
        console.warn('⚠️ electronAPI not available or no trades to save');
      }
    } catch (error) {
      console.error('❌ Failed to add bulk trades:', error);
      throw error;
    }
  };

  const updateTrade = async (id: number, trade: Partial<Trade>) => {
    try {
      if (window.electronAPI) {
        const updatedTrade = await window.electronAPI.updateTrade(id, trade);
        setTrades(prev => prev.map(t => t.id === id ? updatedTrade : t));
      }
    } catch (error) {
      console.error('Failed to update trade:', error);
    }
  };

  const handleTradeSubmit = async (trade: Omit<Trade, 'id'>, id?: number) => {
    if (id) {
      await updateTrade(id, trade);
    } else {
      await addTrade(trade);
    }
  };

  const deleteTrade = async (id: number) => {
    try {
      if (window.electronAPI) {
        await window.electronAPI.deleteTrade(id);
        setTrades(prev => prev.filter(t => t.id !== id));
      }
    } catch (error) {
      console.error('Failed to delete trade:', error);
    }
  };

  const toggleDarkMode = async () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    
    // Save the dark mode setting
    if (settings && window.electronAPI) {
      try {
        const updatedSettings = { ...settings, darkMode: newDarkMode };
        await window.electronAPI.saveSettings(updatedSettings);
        setSettings(updatedSettings);
      } catch (error) {
        console.error('Failed to save dark mode setting:', error);
      }
    }
  };

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-50">
        <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-2xl">
          <h1 className="text-2xl font-bold text-red-600 mb-4">App Error</h1>
          <p className="text-gray-700 mb-4 font-mono text-sm bg-gray-100 p-4 rounded overflow-auto max-h-96">
            {error}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reload App
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <div className="flex bg-gray-50 dark:bg-gray-900 min-h-screen">
        <Router initialEntries={["/dashboard"]}>
          <Sidebar darkMode={darkMode} />
          <main className="flex-1 p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard trades={trades} />} />
              <Route path="/trades" element={<TradeList trades={trades} onUpdate={updateTrade} onDelete={deleteTrade} onAddTrades={addBulkTrades} />} />
              <Route path="/trades/new" element={<TradeForm onSubmit={handleTradeSubmit} settings={settings} />} />
              <Route path="/trades/edit/:id" element={<TradeForm trades={trades} onSubmit={handleTradeSubmit} settings={settings} />} />
              <Route path="/analytics" element={<Analytics trades={trades} />} />
              <Route path="/settings" element={<Settings darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />} />
            </Routes>
          </main>
        </Router>
      </div>
    </div>
  );
};

export default App;
