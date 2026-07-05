import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileText, CheckCircle, AlertCircle, Cpu, ArrowRight, Loader2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function Dashboard({ 
  onMatchSuccess, 
  candidate, 
  setCandidate, 
  matchResult, 
  setMatchResult,
  setViewRoadmapMatchId,
  setGlobalLoading = () => {},
  setLoadingMessage = () => {}
}) {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [activeStep, setActiveStep] = useState(1); // 1: Upload, 2: Match Result

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadStatus(`Selected: ${e.target.files[0].name}`);
    }
  };

  const handleUploadResume = async () => {
    if (!file) {
      alert("Please select a resume file first.");
      return;
    }
    
    setLoading(true);
    setGlobalLoading(true);
    setLoadingMessage("Parsing resume content with NLP...");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload-resume`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCandidate(response.data);
      setUploadStatus(`Successfully parsed: ${response.data.name}`);
      setActiveStep(2); // Go to job match inputs
    } catch (error) {
      console.error(error);
      alert("Error parsing resume. Please ensure the backend is running and the file is valid.");
    } finally {
      setLoading(false);
      setGlobalLoading(false);
    }
  };

  const handleRunMatching = async () => {
    if (!candidate || !candidate.id) {
      alert("Please upload and parse a resume first.");
      return;
    }
    if (!jd.trim()) {
      alert("Please paste a job description to match against.");
      return;
    }

    setLoading(true);
    setGlobalLoading(true);
    setLoadingMessage("Running semantic matching & gap analysis...");
    try {
      const response = await axios.post(`${API_BASE_URL}/match`, {
        candidate_id: candidate.id,
        job_description: jd
      });
      setMatchResult(response.data);
      onMatchSuccess(); // Triggers parent to refresh records if needed
    } catch (error) {
      console.error(error);
      alert("Error matching candidate. Please check backend logs.");
    } finally {
      setLoading(false);
      setGlobalLoading(false);
    }
  };

  const resetFlow = () => {
    setFile(null);
    setJd('');
    setCandidate(null);
    setMatchResult(null);
    setUploadStatus('');
    setActiveStep(1);
  };

  // Helper for radial gauge dash calculations
  const score = matchResult ? matchResult.match_score : 0;
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-extrabold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
          RAG-Powered Talent Matcher
        </h1>
        <p className="text-slate-400 mt-2">
          Upload resumes, parse skills using NLP, match candidates semantically, and build personalized roadmaps.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Input Section (Inputs & Controls) */}
        <div className="lg:col-span-6 space-y-6">
          
          {/* Step 1: Upload Resume */}
          <div className="glass-card p-6 relative overflow-hidden">
            <div className={`absolute top-0 left-0 w-2 h-full ${activeStep === 1 ? 'bg-brand-indigo' : 'bg-brand-teal'}`}></div>
            <div className="flex items-center justify-between mb-4 pl-2">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <span className="flex items-center justify-center w-7 h-7 rounded-full bg-slate-800 border border-slate-700 text-sm font-semibold">1</span>
                Upload Candidate Resume
              </h2>
              {candidate && (
                <span className="text-xs font-semibold px-2.5 py-1 rounded bg-brand-teal/20 text-brand-teal border border-brand-teal/30">
                  Parsed Successfully
                </span>
              )}
            </div>

            {activeStep === 1 || !candidate ? (
              <div className="space-y-4 pl-2">
                <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-700 hover:border-brand-indigo/60 rounded-xl p-8 cursor-pointer bg-slate-900/40 hover:bg-slate-900/60 transition-all group">
                  <Upload className="w-10 h-10 text-slate-500 group-hover:text-brand-indigo group-hover:scale-110 transition-all duration-300" />
                  <span className="mt-3 font-semibold text-sm text-slate-300">Click to upload resume</span>
                  <span className="text-xs text-slate-500 mt-1">PDF, DOCX, or TXT formats (Max 5MB)</span>
                  <input type="file" className="hidden" accept=".pdf,.docx,.doc,.txt" onChange={handleFileChange} />
                </label>
                
                {uploadStatus && (
                  <p className="text-xs text-brand-indigo font-medium flex items-center gap-1">
                    <FileText className="w-3.5 h-3.5" />
                    {uploadStatus}
                  </p>
                )}

                <button
                  onClick={handleUploadResume}
                  disabled={loading || !file}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Parsing Resume Content...
                    </>
                  ) : (
                    <>
                      Parse Resume with NLP
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="pl-2 space-y-3">
                <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 space-y-2">
                  <p className="text-sm font-semibold text-white">{candidate.name}</p>
                  <p className="text-xs text-slate-400">Email: {candidate.email || 'N/A'}</p>
                  <p className="text-xs text-slate-400">Phone: {candidate.phone || 'N/A'}</p>
                  <p className="text-xs text-slate-300 font-semibold mt-2">
                    Classification Category: <span className="text-brand-indigo">{candidate.category || 'Data Science & AI'}</span>
                  </p>
                </div>
                <button onClick={resetFlow} className="text-xs text-slate-400 hover:text-white underline">
                  Upload a different resume
                </button>
              </div>
            )}
          </div>

          {/* Step 2: Paste Job Description */}
          <div className={`glass-card p-6 relative overflow-hidden transition-all duration-300 ${!candidate ? 'opacity-50 pointer-events-none' : 'opacity-100'}`}>
            <div className="absolute top-0 left-0 w-2 h-full bg-brand-purple"></div>
            <h2 className="text-xl font-bold flex items-center gap-2 mb-4 pl-2">
              <span className="flex items-center justify-center w-7 h-7 rounded-full bg-slate-800 border border-slate-700 text-sm font-semibold">2</span>
              Paste Job Description
            </h2>

            <div className="space-y-4 pl-2">
              <textarea
                value={jd}
                onChange={(e) => setJd(e.target.value)}
                placeholder="Paste the target job description details here to compute skill gap and matching metrics..."
                className="w-full h-44 glass-input resize-none"
              ></textarea>

              <button
                onClick={handleRunMatching}
                disabled={loading || !jd.trim()}
                className="w-full btn-primary bg-gradient-to-r from-brand-purple to-brand-indigo flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Running Match Algorithms...
                  </>
                ) : (
                  <>
                    <Cpu className="w-5 h-5" />
                    Match & Identify Skill Gaps
                  </>
                )}
              </button>
            </div>
          </div>

        </div>

        {/* Right Output Section (Results & Action) */}
        <div className="lg:col-span-6">
          {matchResult ? (
            <div className="glass-card p-6 space-y-6 h-full flex flex-col justify-between animate-fadeIn border-brand-indigo/30 bg-slate-900/10">
              
              {/* Top Section: Score & Metrics */}
              <div className="space-y-6">
                <div className="flex items-center justify-between border-b border-white/5 pb-4">
                  <h3 className="text-lg font-bold text-slate-200">Matching Analytics</h3>
                  <button onClick={resetFlow} className="text-xs bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded border border-slate-700">
                    Reset
                  </button>
                </div>

                <div className="flex flex-col sm:flex-row items-center gap-6 justify-center bg-slate-900/40 p-6 rounded-2xl border border-slate-800">
                  {/* Gauge Chart SVG */}
                  <div className="relative flex items-center justify-center w-36 h-36">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="70" cy="70" r={radius} className="stroke-slate-800 fill-none" strokeWidth="10" />
                      <circle 
                        cx="70" 
                        cy="70" 
                        r={radius} 
                        className="stroke-brand-indigo fill-none transition-all duration-1000 ease-out" 
                        strokeWidth="10"
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute text-center">
                      <span className="text-3xl font-extrabold text-white">{score}%</span>
                      <p className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Match Score</p>
                    </div>
                  </div>

                  {/* Similarity Breakdown */}
                  <div className="flex-1 space-y-4 w-full">
                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1">
                        <span className="text-slate-400">Semantic Cosine Similarity</span>
                        <span className="text-brand-indigo">{matchResult.cosine_similarity}%</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div className="bg-brand-indigo h-full rounded-full" style={{ width: `${matchResult.cosine_similarity}%` }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs font-semibold mb-1">
                        <span className="text-slate-400">Keyword / Skill Overlap</span>
                        <span className="text-brand-purple">{matchResult.keyword_overlap}%</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div className="bg-brand-purple h-full rounded-full" style={{ width: `${matchResult.keyword_overlap}%` }}></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Skills Gap Analysis */}
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-bold text-slate-300 flex items-center gap-1.5 mb-2">
                      <CheckCircle className="w-4 h-4 text-emerald-500" />
                      Matched Skills ({matchResult.matched_skills.length})
                    </h4>
                    {matchResult.matched_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {matchResult.matched_skills.map((skill, index) => (
                          <span key={index} className="badge-skill bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                            {skill}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No direct matches found.</p>
                    )}
                  </div>

                  <div>
                    <h4 className="text-sm font-bold text-slate-300 flex items-center gap-1.5 mb-2">
                      <AlertCircle className="w-4 h-4 text-rose-500" />
                      Missing Skills (Skill Gap: {matchResult.missing_skills.length})
                    </h4>
                    {matchResult.missing_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {matchResult.missing_skills.map((skill, index) => (
                          <span key={index} className="badge-skill bg-rose-500/10 text-rose-400 border-rose-500/20">
                            {skill}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-emerald-400 bg-emerald-500/5 p-2 rounded-lg border border-emerald-500/15">
                        Perfect match! Candidate possesses all identified skills for this role.
                      </p>
                    )}
                  </div>
                </div>

              </div>

              {/* Bottom Section: Generate Roadmap Action */}
              <div className="pt-4 border-t border-white/5 mt-6">
                <button
                  onClick={() => setViewRoadmapMatchId(matchResult.match_id)}
                  className="w-full btn-primary bg-gradient-to-r from-emerald-500 to-brand-indigo hover:from-emerald-500/90 hover:to-brand-indigo/90 shadow-emerald-500/20 text-white flex items-center justify-center gap-2 p-4 text-base"
                >
                  Generate RAG-Powered Roadmap
                  <ArrowRight className="w-5 h-5" />
                </button>
                <p className="text-center text-[10px] text-slate-500 mt-2">
                  Uses ChromaDB semantic query over Career Knowledge Base resources + Groq LLaMA-3.1
                </p>
              </div>

            </div>
          ) : (
            <div className="glass-card p-6 h-full flex flex-col items-center justify-center border-dashed border-slate-700/50 bg-slate-900/10 min-h-[300px]">
              <Cpu className="w-16 h-16 text-slate-700 mb-4 animate-pulse" />
              <h3 className="text-lg font-semibold text-slate-400">Awaiting Profile Match</h3>
              <p className="text-slate-600 text-xs text-center max-w-xs mt-1">
                Parse a resume first, paste the target job description, and hit 'Match' to see real-time skill gaps.
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
