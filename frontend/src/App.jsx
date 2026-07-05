import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Roadmap from './pages/Roadmap';
import History from './pages/History';
import Login from './pages/Login';
import LoadingOverlay from './components/LoadingOverlay';
import { Cpu, History as HistoryIcon, LayoutDashboard, Code, LogOut, User } from 'lucide-react';

export default function App() {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('skillbridge_active_user'));
    } catch {
      return null;
    }
  });

  const [activeTab, setActiveTab] = useState('dashboard');
  const [candidate, setCandidate] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [selectedMatchId, setSelectedMatchId] = useState(null);

  // Global loading states
  const [globalLoading, setGlobalLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Processing...');

  const handleMatchSuccess = () => {
    // Refresh states or trigger callbacks
  };

  const handleViewRoadmap = (matchId) => {
    setSelectedMatchId(matchId);
    setActiveTab('roadmap');
  };

  const handleLogout = () => {
    localStorage.removeItem('skillbridge_active_user');
    setUser(null);
    setCandidate(null);
    setMatchResult(null);
    setSelectedMatchId(null);
    setActiveTab('dashboard');
  };

  // If not logged in, render Login Page
  if (!user) {
    return <Login onLoginSuccess={setUser} />;
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Global Writing Loading Overlay */}
      {globalLoading && <LoadingOverlay message={loadingMessage} />}
      
      {/* Header */}
      <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-white/5 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="bg-gradient-to-tr from-brand-indigo to-brand-purple p-2 rounded-xl text-white shadow-lg shadow-brand-indigo/25">
              <Cpu className="w-6 h-6 animate-pulse-slow" />
            </div>
            <div>
              <span className="text-xl font-black bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent tracking-tight font-display">
                SkillBridge <span className="text-brand-indigo">AI</span>
              </span>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold -mt-1">
                RAG Upskilling Agent
              </p>
            </div>
          </div>

          {/* Navigation Links & User Bar */}
          <div className="flex items-center gap-4 sm:gap-6">
            <nav className="flex items-center gap-1 sm:gap-2">
              <button
                onClick={() => {
                  setActiveTab('dashboard');
                  setSelectedMatchId(null);
                }}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === 'dashboard'
                    ? 'bg-white/5 text-white border border-white/10'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <LayoutDashboard className="w-4 h-4 text-brand-indigo" />
                <span className="hidden sm:inline">Dashboard</span>
              </button>
              
              <button
                onClick={() => {
                  setActiveTab('history');
                  setSelectedMatchId(null);
                }}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === 'history'
                    ? 'bg-white/5 text-white border border-white/10'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <HistoryIcon className="w-4 h-4 text-brand-purple" />
                <span className="hidden sm:inline">History & Analytics</span>
              </button>
            </nav>

            <div className="h-6 w-px bg-white/10 hidden sm:block"></div>

            {/* Profile & Log Out */}
            <div className="flex items-center gap-3">
              <div className="hidden md:flex items-center gap-2.5 bg-slate-900/80 border border-slate-800 rounded-xl px-3 py-1.5">
                <div className="w-6 h-6 rounded-full bg-brand-indigo/20 flex items-center justify-center text-brand-indigo text-xs font-bold">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="text-left">
                  <p className="text-xs font-semibold text-slate-200 leading-none">{user.name}</p>
                  <p className="text-[9px] text-slate-500 font-bold tracking-tight mt-0.5">{user.email}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-slate-900 hover:bg-rose-500/10 text-slate-400 hover:text-rose-400 border border-slate-800 hover:border-rose-500/20 transition-all duration-200"
                title="Log Out"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Log Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
        {activeTab === 'dashboard' && (
          <Dashboard 
            onMatchSuccess={handleMatchSuccess}
            candidate={candidate}
            setCandidate={setCandidate}
            matchResult={matchResult}
            setMatchResult={setMatchResult}
            setViewRoadmapMatchId={handleViewRoadmap}
            setGlobalLoading={setGlobalLoading}
            setLoadingMessage={setLoadingMessage}
          />
        )}
        
        {activeTab === 'roadmap' && (
          <Roadmap 
            matchId={selectedMatchId} 
            onBack={() => {
              setActiveTab('dashboard');
              setSelectedMatchId(null);
            }} 
            setGlobalLoading={setGlobalLoading}
            setLoadingMessage={setLoadingMessage}
          />
        )}
        
        {activeTab === 'history' && (
          <History 
            onViewRoadmap={handleViewRoadmap} 
            setGlobalLoading={setGlobalLoading}
            setLoadingMessage={setLoadingMessage}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-white/5 py-6 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-1.5 justify-center">
            <Code className="w-4 h-4 text-slate-600" />
            <span>FastAPI + React + Tailwind CSS + NumPy Vector Store + Groq LLaMA 3.1</span>
          </div>
          <div>
            <span>SkillBridge AI &copy; 2026 - Renuga D Final Year Student</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
