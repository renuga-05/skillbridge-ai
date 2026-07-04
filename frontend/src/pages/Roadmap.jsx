import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Calendar, CheckSquare, BookOpen, ChevronRight, BarChart2, Award, ArrowLeft, Loader2, RefreshCw } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function Roadmap({ matchId, onBack }) {
  const [roadmapData, setRoadmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Tasks completion state: key is `weekIndex_taskIndex`, value is boolean
  const [completedTasks, setCompletedTasks] = useState({});

  useEffect(() => {
    if (matchId) {
      fetchRoadmap();
    }
  }, [matchId]);

  const fetchRoadmap = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_BASE_URL}/roadmap`, {
        match_id: matchId
      });
      setRoadmapData(response.data);
      
      // Initialize completed tasks states
      const initialStates = {};
      if (response.data.roadmap) {
        response.data.roadmap.forEach((week, wIdx) => {
          if (week.tasks) {
            week.tasks.forEach((_, tIdx) => {
              initialStates[`${wIdx}_${tIdx}`] = false;
            });
          }
        });
      }
      setCompletedTasks(initialStates);
    } catch (err) {
      console.error(err);
      setError('Failed to generate upskilling roadmap. Please make sure the backend is running and the Groq API key is valid.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = (weekIdx, taskIdx) => {
    const key = `${weekIdx}_${taskIdx}`;
    setCompletedTasks(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  // Calculations for progress bar
  const totalTasks = Object.keys(completedTasks).length;
  const completedCount = Object.values(completedTasks).filter(Boolean).length;
  const progressPercent = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4 animate-fadeIn">
        <Loader2 className="w-16 h-16 text-brand-indigo animate-spin" />
        <h3 className="text-xl font-bold text-slate-200">Retrieving Skill Resources...</h3>
        <p className="text-slate-400 text-sm max-w-xs text-center">
          Querying local vector database (ChromaDB) for missing skill resources and compiling custom roadmap using LLaMA-3.1.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card p-8 border-rose-500/30 text-center max-w-lg mx-auto space-y-4 animate-fadeIn">
        <Award className="w-12 h-12 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-white">Roadmap Generation Failed</h3>
        <p className="text-slate-400 text-sm">{error}</p>
        <div className="flex justify-center gap-4">
          <button onClick={onBack} className="btn-secondary flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" /> Go Back
          </button>
          <button onClick={fetchRoadmap} className="btn-primary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  if (!roadmapData) return null;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Navigation Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <button onClick={onBack} className="btn-secondary flex items-center gap-2 py-2 px-4 text-xs font-semibold">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </button>
        {roadmapData.mode === "demo_fallback" && (
          <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-3 py-1 rounded-full font-medium">
            ⚠️ Running in Offline Demo Mode (No Groq Key Configured)
          </span>
        )}
      </div>

      {/* Profile summary card */}
      <div className="glass-card p-6 bg-gradient-to-r from-brand-indigo/10 via-brand-purple/5 to-slate-900/40 relative overflow-hidden border-brand-indigo/20">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-indigo/5 rounded-full blur-3xl -z-10"></div>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
          <div className="space-y-2">
            <span className="text-[10px] uppercase tracking-wider bg-brand-indigo/20 text-brand-indigo border border-brand-indigo/30 px-2.5 py-1 rounded font-bold">
              UPSKILLING SCHEDULER
            </span>
            <h2 className="text-3xl font-extrabold text-white">
              {roadmapData.candidate_name}'s Roadmap
            </h2>
            <p className="text-slate-400">
              Personalized target role preparation path for: <span className="text-brand-purple font-semibold">{roadmapData.target_role}</span>
            </p>
            <div className="flex flex-wrap gap-2 pt-2">
              {roadmapData.missing_skills && roadmapData.missing_skills.map((skill, index) => (
                <span key={index} className="text-xs bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded">
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Progress gauge */}
          <div className="w-full md:w-64 bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-2">
            <div className="flex justify-between text-xs font-semibold">
              <span className="text-slate-400">Upskilling Roadmap Progress</span>
              <span className="text-brand-teal">{progressPercent}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
              <div 
                className="bg-brand-teal h-full rounded-full transition-all duration-500" 
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>
            <p className="text-[10px] text-slate-500 text-right">
              {completedCount} of {totalTasks} tasks completed
            </p>
          </div>
        </div>
      </div>

      {/* Main 4-Week Timeline */}
      <div className="relative pl-6 sm:pl-10 space-y-12">
        {/* Vertical Line */}
        <div className="absolute left-3.5 sm:left-5 top-4 bottom-4 w-0.5 bg-slate-800"></div>

        {roadmapData.roadmap && roadmapData.roadmap.map((week, wIdx) => {
          // Calculate tasks count for this week
          const weekTasks = week.tasks || [];
          const weekCompleted = weekTasks.filter((_, tIdx) => completedTasks[`${wIdx}_${tIdx}`]).length;
          const isWeekFinished = weekTasks.length > 0 && weekCompleted === weekTasks.length;

          return (
            <div key={wIdx} className="relative group animate-fadeIn" style={{ animationDelay: `${wIdx * 100}ms` }}>
              
              {/* Timeline Bullet Node */}
              <div className={`absolute -left-[30px] sm:-left-[46px] top-1.5 w-7 h-7 rounded-full border-4 flex items-center justify-center transition-all duration-300 ${
                isWeekFinished 
                  ? 'bg-brand-teal border-brand-teal text-slate-900' 
                  : weekCompleted > 0
                    ? 'bg-brand-indigo border-brand-indigo text-white'
                    : 'bg-dark-900 border-slate-700 text-slate-400'
              }`}>
                {isWeekFinished ? (
                  <CheckSquare className="w-3.5 h-3.5" />
                ) : (
                  <span className="text-[10px] font-bold">{week.week}</span>
                )}
              </div>

              {/* Week Card */}
              <div className={`glass-card p-6 space-y-6 transition-all duration-300 ${
                isWeekFinished ? 'border-brand-teal/20 bg-brand-teal/5' : 'border-slate-800 hover:border-slate-700'
              }`}>
                
                {/* Week Header */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-white/5 pb-4">
                  <div>
                    <span className="text-xs font-semibold text-brand-indigo uppercase tracking-wider">Week {week.week}</span>
                    <h3 className="text-xl font-bold text-white mt-1">{week.theme}</h3>
                  </div>
                  <span className="text-xs bg-slate-900/60 border border-slate-800 px-2.5 py-1 rounded text-slate-400 font-semibold self-start sm:self-center">
                    {weekCompleted}/{weekTasks.length} Tasks
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                  
                  {/* Left Column: Topics to Study */}
                  <div className="md:col-span-5 space-y-3">
                    <h4 className="text-sm font-bold text-slate-300 flex items-center gap-1.5">
                      <BookOpen className="w-4 h-4 text-brand-indigo" />
                      Core Learning Topics
                    </h4>
                    <ul className="space-y-2">
                      {week.topics && week.topics.map((topic, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-slate-400">
                          <ChevronRight className="w-4 h-4 text-brand-indigo shrink-0 mt-0.5" />
                          <span>{topic}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Middle Column: Tasks to Build / Practice */}
                  <div className="md:col-span-7 space-y-3">
                    <h4 className="text-sm font-bold text-slate-300 flex items-center gap-1.5">
                      <CheckSquare className="w-4 h-4 text-brand-purple" />
                      Hands-on Checkpoints
                    </h4>
                    <div className="space-y-2 bg-slate-900/40 p-4 rounded-xl border border-slate-800/80">
                      {weekTasks.map((task, tIdx) => {
                        const isDone = completedTasks[`${wIdx}_${tIdx}`];
                        return (
                          <label 
                            key={tIdx} 
                            className={`flex items-start gap-3 p-2 rounded-lg cursor-pointer transition-all duration-150 ${
                              isDone ? 'bg-slate-900/70 opacity-60' : 'hover:bg-slate-800/50'
                            }`}
                          >
                            <input 
                              type="checkbox" 
                              checked={!!isDone}
                              onChange={() => handleToggleTask(wIdx, tIdx)}
                              className="mt-1 rounded border-slate-700 text-brand-indigo focus:ring-brand-indigo bg-slate-800 w-4 h-4 shrink-0"
                            />
                            <span className={`text-sm text-slate-300 ${isDone ? 'line-through text-slate-500' : ''}`}>
                              {task}
                            </span>
                          </label>
                        );
                      })}
                    </div>
                  </div>

                </div>

                {/* Bottom Section: RAG study Resources */}
                {week.resources && week.resources.length > 0 && (
                  <div className="bg-slate-900/30 p-4 rounded-xl border border-slate-800/50 space-y-2 mt-4">
                    <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-brand-teal" />
                      Reference Materials (Retrieved via RAG)
                    </h5>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {week.resources.map((res, rIdx) => {
                        // Check if resource string looks like a markdown URL
                        const urlMatch = res.match(/(https?:\/\/[^\s]+)/);
                        const displayRes = res.replace(/(https?:\/\/[^\s]+)/, "").replace(" - ", "").strip ? res.replace(/(https?:\/\/[^\s]+)/, "").replace(" - ", "").trim() : res;
                        
                        return (
                          <div key={rIdx} className="text-xs text-slate-400 flex items-start gap-1.5 bg-slate-900/50 p-2.5 rounded border border-slate-800">
                            <span className="text-brand-teal shrink-0">📖</span>
                            {urlMatch ? (
                              <a 
                                href={urlMatch[0]} 
                                target="_blank" 
                                rel="noreferrer" 
                                className="text-brand-teal hover:underline font-medium break-all"
                              >
                                {res}
                              </a>
                            ) : (
                              <span>{res}</span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
