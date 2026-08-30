import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../services/api';
import { useAuth } from '../context/AuthContext';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await loginUser(email, password);
      await refreshUser();
      navigate('/chat');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex items-center justify-center p-6 selection:bg-purple-500/30 selection:text-purple-200">
      <div className="glass-card p-8 sm:p-10 max-w-md w-full space-y-6 border border-white/10 shadow-2xl relative overflow-hidden">
        {/* Glow ambient background element */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-purple-600/30 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-24 -left-24 w-48 h-48 bg-cyan-600/20 rounded-full blur-3xl pointer-events-none"></div>

        <div className="text-center space-y-3 relative z-10">
          <Link to="/" className="inline-flex items-center space-x-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 via-purple-500 to-cyan-400 p-[1px] shadow-glow">
              <div className="w-full h-full bg-[#0B0F17] rounded-[11px] flex items-center justify-center font-bold text-transparent bg-clip-text bg-gradient-to-tr from-cyan-400 to-violet-400 text-lg">
                ⚡
              </div>
            </div>
            <span className="font-extrabold text-2xl tracking-tight text-white group-hover:text-cyan-300 transition-colors">
              SwitchAI
            </span>
          </Link>
          <p className="text-xs text-text-secondary">Welcome back! Sign in to your SwitchAI account.</p>
        </div>

        {error && (
          <div className="p-3 text-xs bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl font-medium flex items-center space-x-2">
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 relative z-10">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-text-secondary">Email address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 focus:border-violet-500 focus:ring-1 focus:ring-violet-500/50 focus:outline-none text-xs text-white placeholder-text-muted transition-all"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-text-secondary">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl bg-black/40 border border-white/10 focus:border-violet-500 focus:ring-1 focus:ring-violet-500/50 focus:outline-none text-xs text-white placeholder-text-muted transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white text-xs font-bold transition-all shadow-glow disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {loading ? 'Signing in...' : 'Sign In to Workspace →'}
          </button>
        </form>

        <div className="text-center text-xs text-text-muted pt-2 relative z-10">
          Don't have an account?{' '}
          <Link to="/signup" className="text-cyan-400 hover:underline font-semibold">
            Create account
          </Link>
        </div>
      </div>
    </div>
  );
}
