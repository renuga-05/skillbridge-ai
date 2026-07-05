import React, { useState } from 'react';
import { Cpu, Mail, Lock, User, CheckCircle, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';

export default function Login({ onLoginSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields.');
      return;
    }

    if (isSignUp) {
      if (!name.trim()) {
        setError('Please enter your name.');
        return;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match.');
        return;
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters.');
        return;
      }

      setLoading(true);
      setTimeout(() => {
        // Retrieve existing users from local storage
        const users = JSON.parse(localStorage.getItem('skillbridge_users') || '[]');
        if (users.find(u => u.email.toLowerCase() === email.toLowerCase())) {
          setError('An account with this email already exists.');
          setLoading(false);
          return;
        }

        // Add new user record
        const newUser = { name, email, password };
        users.push(newUser);
        localStorage.setItem('skillbridge_users', JSON.stringify(users));

        setSuccess('Account created successfully! Switching to Login...');
        setLoading(false);
        setTimeout(() => {
          setIsSignUp(false);
          setPassword('');
          setConfirmPassword('');
          setSuccess('');
        }, 1500);
      }, 1000);
    } else {
      setLoading(true);
      setTimeout(() => {
        const users = JSON.parse(localStorage.getItem('skillbridge_users') || '[]');
        
        // Add a default guest user for easy testing if it doesn't exist
        const defaultUser = { name: 'Guest Developer', email: 'guest@example.com', password: 'password123' };
        if (!users.find(u => u.email === defaultUser.email)) {
          users.push(defaultUser);
          localStorage.setItem('skillbridge_users', JSON.stringify(users));
        }

        const user = users.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);
        if (!user) {
          setError('Invalid email or password. Use guest@example.com / password123 to log in.');
          setLoading(false);
          return;
        }

        localStorage.setItem('skillbridge_active_user', JSON.stringify(user));
        setSuccess('Success! Logging in...');
        setLoading(false);
        setTimeout(() => {
          onLoginSuccess(user);
        }, 800);
      }, 1000);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-dark-900 text-slate-100 relative overflow-hidden px-4">
      {/* Decorative Gradients */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-radial from-brand-indigo/15 to-transparent blur-3xl pointer-events-none -z-10"></div>
      
      <div className="flex-1 flex flex-col items-center justify-center py-12">
        {/* App Logo & Branding */}
        <div className="flex flex-col items-center gap-3 mb-8 text-center animate-fadeIn">
          <div className="bg-gradient-to-tr from-brand-indigo to-brand-purple p-3.5 rounded-2xl text-white shadow-xl shadow-brand-indigo/25">
            <Cpu className="w-8 h-8 animate-pulse-slow" />
          </div>
          <div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent tracking-tight font-display">
              SkillBridge <span className="text-brand-indigo">AI</span>
            </h1>
            <p className="text-xs text-slate-500 uppercase tracking-widest font-bold mt-0.5">
              RAG-Powered Career matching agent
            </p>
          </div>
        </div>

        {/* Login Box */}
        <div className="w-full max-w-md glass-card p-8 border-slate-800 shadow-2xl relative overflow-hidden animate-slideUp">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-brand-indigo via-brand-purple to-brand-teal"></div>
          
          <h2 className="text-2xl font-bold text-white text-center mb-6">
            {isSignUp ? 'Create New Account' : 'Sign In to Your Account'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Status alerts */}
            {error && (
              <div className="flex items-start gap-2.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3.5 rounded-xl text-xs animate-shake">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}
            
            {success && (
              <div className="flex items-start gap-2.5 bg-brand-teal/10 border border-brand-teal/20 text-brand-teal p-3.5 rounded-xl text-xs">
                <CheckCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{success}</span>
              </div>
            )}

            {isSignUp && (
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Jane Doe"
                    className="w-full pl-10 glass-input text-sm"
                    required
                  />
                </div>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full pl-10 glass-input text-sm"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-400">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 glass-input text-sm"
                  required
                />
              </div>
            </div>

            {isSignUp && (
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-400">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-500" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 glass-input text-sm"
                    required
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary bg-gradient-to-r from-brand-indigo to-brand-purple flex items-center justify-center gap-2 mt-6 py-3.5 text-sm"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Please Wait...
                </>
              ) : (
                <>
                  {isSignUp ? 'Create Account' : 'Sign In'}
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Button */}
          <div className="mt-6 text-center text-xs text-slate-400">
            {isSignUp ? (
              <p>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignUp(false);
                    setError('');
                  }}
                  className="text-brand-indigo hover:text-brand-purple font-semibold hover:underline bg-transparent border-none p-0 cursor-pointer"
                >
                  Sign In
                </button>
              </p>
            ) : (
              <p>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setIsSignUp(true);
                    setError('');
                  }}
                  className="text-brand-indigo hover:text-brand-purple font-semibold hover:underline bg-transparent border-none p-0 cursor-pointer"
                >
                  Create New Account
                </button>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-6 text-center text-xs text-slate-500 border-t border-white/5 w-full">
        <span>SkillBridge AI © 2026 - Renuga D Final Year Student</span>
      </footer>
    </div>
  );
}
