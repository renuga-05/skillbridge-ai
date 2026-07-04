import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Roadmap from './pages/Roadmap';
import History from './pages/History';
import { Cpu, History as HistoryIcon, LayoutDashboard, Code } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [candidate, setCandidate] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [selectedMatchId, setSelectedMatchId] = useState(null);

  // Callbacks for routing/navigation
  const handleMatchSuccess = () => {
    // Potentially trigger any global updates, or just keep state
  };

  const handleViewRoadmap = (matchId) => {
    setSelectedMatchId(matchId);
    setActiveTab('roadmap');
  };

  return (
    <div className="min-h-screen flex flex-col">
      
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

          {/* Navigation Links */}
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
          />
        )}
        
        {activeTab === 'roadmap' && (
          <Roadmap 
            matchId={selectedMatchId} 
            onBack={() => {
              setActiveTab('dashboard');
              setSelectedMatchId(null);
            }} 
          />
        )}
        
        {activeTab === 'history' && (
          <History 
            onViewRoadmap={handleViewRoadmap} 
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-white/5 py-6 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-1.5 justify-center">
            <Code className="w-4 h-4 text-slate-600" />
            <span>FastAPI + React + Tailwind CSS + ChromaDB + Groq LLaMA 3.1</span>
          </div>
          <div>
            <span>SkillBridge AI &copy; 2026 - Renuga D Final Year Student</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
