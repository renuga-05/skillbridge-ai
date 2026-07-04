import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Calendar, Award, Eye, FileText, Loader2, ArrowRight } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function History({ onViewRoadmap }) {
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE_URL}/history`);
      // Recharts likes chronological order, but tables prefer reverse chronological
      setHistoryList(response.data);
    } catch (err) {
      console.error(err);
      setError('Could not retrieve match history logs. Check backend server connection.');
    } finally {
      setLoading(false);
    }
  };

  // Calculations for stats
  const totalMatches = historyList.length;
  const avgScore = totalMatches > 0 
    ? Math.round(historyList.reduce((acc, item) => acc + item.match_score, 0) / totalMatches) 
    : 0;
  const highestScore = totalMatches > 0 
    ? Math.max(...historyList.map(item => item.match_score)) 
    : 0;

  // Formatting historical data for chart: sort chronological, take last 10
  const chartData = [...historyList]
    .reverse()
    .slice(-10)
    .map(item => ({
      name: item.candidate_name.split(' ')[0], // First name for neatness
      score: item.match_score,
      date: new Date(item.timestamp).toLocaleDateString()
    }));

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] space-y-4">
        <Loader2 className="w-10 h-10 text-brand-indigo animate-spin" />
        <h3 className="text-base text-slate-400">Loading history data...</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-6 text-center border-rose-500/20 max-w-md mx-auto space-y-4">
        <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
        <p className="text-slate-300 text-sm">{error}</p>
        <button onClick={fetchHistory} className="btn-primary py-2 px-4 text-xs font-semibold">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
          Match History & Analytics
        </h1>
        <p className="text-slate-400 mt-2">
          Review historical candidates, visual analytics trends, and previously compiled roadmaps.
        </p>
      </div>

      {totalMatches === 0 ? (
        <div className="glass-card p-12 text-center border-dashed border-slate-700/50 bg-slate-900/10">
          <Calendar className="w-12 h-12 text-slate-700 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-400">No match records yet</h3>
          <p className="text-slate-600 text-xs mt-1">
            Run a match analysis on the main dashboard to log entries and generate charts.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          
          {/* Stats Bar */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="glass-card p-6 border-slate-800 space-y-2">
              <span className="text-[10px] tracking-wider uppercase text-slate-500 font-bold">TOTAL ASSESSMENTS</span>
              <p className="text-3xl font-extrabold text-white">{totalMatches}</p>
              <p className="text-xs text-slate-400">Successfully matching skills & profiles</p>
            </div>
            <div className="glass-card p-6 border-slate-800 space-y-2">
              <span className="text-[10px] tracking-wider uppercase text-slate-500 font-bold">AVERAGE MATCH SCORE</span>
              <p className="text-3xl font-extrabold text-brand-indigo">{avgScore}%</p>
              <p className="text-xs text-slate-400">Average alignment across matches</p>
            </div>
            <div className="glass-card p-6 border-slate-800 space-y-2">
              <span className="text-[10px] tracking-wider uppercase text-slate-500 font-bold">PEAK SCORE</span>
              <p className="text-3xl font-extrabold text-brand-teal">{highestScore}%</p>
              <p className="text-xs text-slate-400">Highest matching candidate profile</p>
            </div>
          </div>

          {/* Chart Section */}
          <div className="glass-card p-6 border-slate-800 space-y-4">
            <h3 className="text-lg font-bold text-white">Assessment Score Trend (Last 10 Runs)</h3>
            <div className="w-full h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={chartData}
                  margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="name" stroke="#6b7280" style={{ fontSize: '12px' }} />
                  <YAxis domain={[0, 100]} stroke="#6b7280" style={{ fontSize: '12px' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#111827', 
                      borderColor: '#374151',
                      borderRadius: '8px',
                      color: '#f3f4f6'
                    }} 
                  />
                  <Area 
                    type="monotone" 
                    dataKey="score" 
                    stroke="#6366f1" 
                    strokeWidth={2}
                    fillOpacity={1} 
                    fill="url(#colorScore)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Table list */}
          <div className="glass-card border-slate-800 overflow-hidden">
            <div className="p-6 border-b border-white/5">
              <h3 className="text-lg font-bold text-white">All Matching Records</h3>
            </div>
            
            <div className="overflow-x-auto w-full">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-900/60 border-b border-slate-850 text-slate-400 text-xs font-semibold uppercase">
                    <th className="px-6 py-4">Candidate</th>
                    <th className="px-6 py-4">Target Job Summary</th>
                    <th className="px-6 py-4 text-center">Match Score</th>
                    <th className="px-6 py-4">Assessment Date</th>
                    <th className="px-6 py-4 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-sm text-slate-300">
                  {historyList.map((item) => (
                    <tr key={item.match_id} className="hover:bg-white/5 transition-all">
                      <td className="px-6 py-4 font-semibold text-white">
                        {item.candidate_name}
                      </td>
                      <td className="px-6 py-4 max-w-xs truncate text-slate-400">
                        {item.job_description.split('\n')[0]}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className={`px-2.5 py-1 rounded text-xs font-semibold border ${
                          item.match_score >= 80 
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : item.match_score >= 60
                              ? 'bg-brand-indigo/10 text-brand-indigo border-brand-indigo/20'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                        }`}>
                          {item.match_score}%
                        </span>
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-400">
                        {new Date(item.timestamp).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <button
                          onClick={() => onViewRoadmap(item.match_id)}
                          className="inline-flex items-center gap-1.5 text-xs text-brand-indigo hover:text-brand-purple hover:underline"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          View Roadmap
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
