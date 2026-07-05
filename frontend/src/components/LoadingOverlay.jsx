import React from 'react';

export default function LoadingOverlay({ message = 'Processing request...' }) {
  return (
    <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-slate-950/75 backdrop-blur-md animate-fadeIn">
      <div className="flex flex-col items-center gap-6 p-8 rounded-2xl bg-slate-900/60 border border-white/5 shadow-2xl max-w-xs w-full text-center">
        {/* CSS Pen-Writing animation container */}
        <div className="relative w-20 h-20 flex items-center justify-center">
          <svg className="w-full h-full text-slate-100" viewBox="0 0 100 100">
            {/* Paper Sheet */}
            <rect 
              x="25" 
              y="15" 
              width="50" 
              height="68" 
              rx="4" 
              fill="none" 
              stroke="currentColor" 
              strokeWidth="3.5" 
              className="text-slate-700"
            />
            {/* Text lines */}
            <line 
              x1="32" 
              y1="32" 
              x2="68" 
              y2="32" 
              stroke="currentColor" 
              strokeWidth="3" 
              strokeLinecap="round" 
              className="text-slate-500 line-1" 
            />
            <line 
              x1="32" 
              y1="46" 
              x2="68" 
              y2="46" 
              stroke="currentColor" 
              strokeWidth="3" 
              strokeLinecap="round" 
              className="text-slate-500 line-2" 
            />
            <line 
              x1="32" 
              y1="60" 
              x2="68" 
              y2="60" 
              stroke="currentColor" 
              strokeWidth="3" 
              strokeLinecap="round" 
              className="text-slate-500 line-3" 
            />
            {/* Moving Pen */}
            <g className="pen-group">
              {/* Pen body */}
              <path 
                d="M 68,14 L 78,24 L 46,60 L 36,60 L 36,50 Z" 
                fill="url(#pen-grad)" 
              />
              {/* Pen tip */}
              <polygon 
                points="36,60 36,53 43,60" 
                fill="#14b8a6" 
              />
            </g>
            
            <defs>
              <linearGradient id="pen-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        <div className="space-y-1">
          <p className="text-sm font-semibold text-white tracking-wide">{message}</p>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest animate-pulse">Running AI Agent</p>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes write {
          0% {
            transform: translate(0, 0) rotate(0deg);
          }
          30% {
            transform: translate(-10px, 14px) rotate(-3deg);
          }
          35% {
            transform: translate(-30px, 14px) rotate(3deg);
          }
          65% {
            transform: translate(-10px, 28px) rotate(-3deg);
          }
          70% {
            transform: translate(-30px, 28px) rotate(3deg);
          }
          95% {
            transform: translate(0, 0) rotate(-3deg);
          }
          100% {
            transform: translate(0, 0) rotate(0deg);
          }
        }

        .pen-group {
          transform-origin: 36px 60px;
          animation: write 3s infinite ease-in-out;
        }

        @keyframes drawLine1 {
          0%, 10% { stroke-dashoffset: 36; }
          30%, 100% { stroke-dashoffset: 0; }
        }
        @keyframes drawLine2 {
          0%, 35% { stroke-dashoffset: 36; }
          65%, 100% { stroke-dashoffset: 0; }
        }
        @keyframes drawLine3 {
          0%, 70% { stroke-dashoffset: 36; }
          95%, 100% { stroke-dashoffset: 0; }
        }

        .line-1, .line-2, .line-3 {
          stroke-dasharray: 36;
          stroke-dashoffset: 36;
        }
        
        .line-1 { animation: drawLine1 3s infinite ease-in-out; }
        .line-2 { animation: drawLine2 3s infinite ease-in-out; }
        .line-3 { animation: drawLine3 3s infinite ease-in-out; }
      `}} />
    </div>
  );
}
