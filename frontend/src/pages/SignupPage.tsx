import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../services/api';
import { useAuth } from '../context/AuthContext';

export function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setLoading(true);

    try {
      await registerUser(email, password);
      await refreshUser();
      navigate('/chat');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-bg1 flex items-center justify-center p-6">
      <div className="glass-card p-8 max-w-md w-full space-y-6 border border-border">
        <div className="text-center space-y-2">
          <Link to="/" className="inline-block text-2xl font-bold text-white tracking-tight">
            SwitchAI
          </Link>
          <p className="text-sm text-text-secondary">Create your SwitchAI account</p>
        </div>

        {error && (
          <div className="p-3 text-xs bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Email address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-3.5 py-2.5 rounded-lg bg-neutral-bg2 border border-border focus:border-brand focus:outline-none text-sm text-white placeholder-text-muted transition-colors"
            />
          </div>

          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              className="w-full px-3.5 py-2.5 rounded-lg bg-neutral-bg2 border border-border focus:border-brand focus:outline-none text-sm text-white placeholder-text-muted transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-medium transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <div className="text-center text-xs text-text-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-brand-light hover:underline font-medium">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
