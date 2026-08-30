import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { checkBackendHealth } from '../services/api';

export function LandingPage() {
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    checkBackendHealth().then(setHealth);
  }, []);

  return (
    <div className="min-h-screen bg-neutral-bg1 flex flex-col items-center justify-center p-6 text-center">
      <div className="glass-card p-10 max-w-3xl w-full border border-border space-y-8">
        <div className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-brand-subtle text-brand-light border border-brand/30">
          BuildSprint 2026 • LatentForce
        </div>

        <div className="space-y-3">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white">
            One memory. Many AI models.
          </h1>
          <h2 className="text-xl md:text-2xl font-semibold text-brand-light">
            Switch models without restarting your thinking.
          </h2>
          <p className="text-sm md:text-base text-text-secondary max-w-xl mx-auto leading-relaxed">
            Keep one conversation, one memory and one workspace while using the AI model that fits the task.
          </p>
        </div>

        {/* Visual Shared Memory Architecture Diagram */}
        <div className="p-6 rounded-2xl bg-black/40 border border-border space-y-6">
          <div className="inline-block px-4 py-2 rounded-xl bg-brand/20 border border-brand/40 text-sm font-bold text-white shadow-glow">
            🧠 SHARED MEMORY
          </div>

          <div className="flex justify-center items-center space-x-8 text-xs font-mono text-text-muted">
            <div className="flex flex-col items-center space-y-2">
              <span className="text-blue-400 font-semibold">↙</span>
              <div className="px-3.5 py-2 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-300 font-bold">
                Gemini
              </div>
            </div>

            <div className="flex flex-col items-center space-y-2">
              <span className="text-orange-400 font-semibold">↓</span>
              <div className="px-3.5 py-2 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-300 font-bold">
                Claude
              </div>
            </div>

            <div className="flex flex-col items-center space-y-2">
              <span className="text-emerald-400 font-semibold">↘</span>
              <div className="px-3.5 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-bold">
                OpenAI
              </div>
            </div>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex justify-center space-x-4 pt-2">
          <Link
            to="/chat"
            className="px-6 py-3 rounded-xl bg-brand hover:bg-brand-hover text-white text-sm font-semibold transition-all shadow-glow"
          >
            Start chatting
          </Link>
          <Link
            to="/settings/providers"
            className="px-6 py-3 rounded-xl glass hover:bg-white/10 text-white text-sm font-semibold transition-colors"
          >
            Connect AI providers
          </Link>
        </div>

        {/* Backend Status Bar */}
        <div className="pt-4 text-xs text-text-muted flex justify-between items-center bg-black/30 p-3 rounded-lg border border-border-subtle">
          <span>Backend Status:</span>
          {health ? (
            <span className={`font-mono ${health.status === 'healthy' ? 'text-green-400' : 'text-red-400'}`}>
              ● {health.status === 'healthy' ? `Healthy (${health.service})` : `Offline (${health.message})`}
            </span>
          ) : (
            <span className="font-mono text-yellow-400">Checking...</span>
          )}
        </div>
      </div>
    </div>
  );
}
