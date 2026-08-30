import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getUsageMetrics } from '../services/api';

interface ProviderMetrics {
  provider: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  rate_limit_events: number;
  fallback_count: number;
  avg_latency_ms: number;
  total_estimated_tokens: number;
}

interface UsageDashboard {
  tracked_by: string;
  total_requests: number;
  total_fallbacks: number;
  avg_system_latency_ms: number;
  providers: ProviderMetrics[];
}

const PROVIDER_TITLES: Record<string, string> = {
  anthropic: 'Anthropic Claude',
  gemini: 'Google Gemini',
  openai: 'OpenAI GPT',
};

export function UsagePage() {
  const [data, setData] = useState<UsageDashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUsageMetrics()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-neutral-bg1 text-white p-6 max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center pb-6 border-b border-border">
        <div>
          <Link to="/chat" className="text-sm font-medium text-text-muted hover:text-white transition-colors">
            ← Back to Chat
          </Link>
          <h1 className="text-3xl font-bold tracking-tight text-white mt-2">Usage & Telemetry Dashboard</h1>
          <p className="text-sm text-text-secondary mt-1 flex items-center space-x-2">
            <span>Provider request distribution, fallbacks, latency, and token estimates.</span>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-brand-subtle text-brand-light border border-brand/30">
              Tracked by SwitchAI
            </span>
          </p>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-text-muted animate-pulse">Loading telemetry metrics...</div>
      ) : data ? (
        <div className="space-y-8">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="glass-card p-5 border border-border space-y-1">
              <div className="text-xs font-semibold text-text-muted uppercase">Total Requests</div>
              <div className="text-2xl font-bold text-white font-mono">{data.total_requests}</div>
              <div className="text-[10px] text-text-muted">Tracked by SwitchAI</div>
            </div>

            <div className="glass-card p-5 border border-border space-y-1">
              <div className="text-xs font-semibold text-text-muted uppercase">Fallback Events</div>
              <div className="text-2xl font-bold text-amber-400 font-mono">{data.total_fallbacks}</div>
              <div className="text-[10px] text-amber-400/80">Resilient Auto Fallbacks</div>
            </div>

            <div className="glass-card p-5 border border-border space-y-1">
              <div className="text-xs font-semibold text-text-muted uppercase">Avg Latency</div>
              <div className="text-2xl font-bold text-green-400 font-mono">{data.avg_system_latency_ms} ms</div>
              <div className="text-[10px] text-text-muted font-mono">Response time</div>
            </div>

            <div className="glass-card p-5 border border-border space-y-1">
              <div className="text-xs font-semibold text-text-muted uppercase">Telemetry Mode</div>
              <div className="text-base font-bold text-brand-light">Active</div>
              <div className="text-[10px] text-text-muted">Internal Measurements</div>
            </div>
          </div>

          {/* Provider Performance Cards */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
              Provider Telemetry breakdown
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {data.providers.map((p) => (
                <div key={p.provider} className="glass-card p-6 border border-border space-y-5">
                  <div className="flex justify-between items-center pb-3 border-b border-border-subtle">
                    <span className="font-semibold text-white">{PROVIDER_TITLES[p.provider] || p.provider}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-black/30 text-text-muted border border-border-subtle">
                      Tracked by SwitchAI
                    </span>
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="text-text-secondary">Requests</span>
                      <span className="font-mono text-white font-semibold">{p.total_requests}</span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-text-secondary">Successful</span>
                      <span className="font-mono text-green-400">{p.successful_requests}</span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-text-secondary">Failures</span>
                      <span className="font-mono text-red-400">{p.failed_requests}</span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-text-secondary">Rate Limits (429)</span>
                      <span className="font-mono text-amber-400">{p.rate_limit_events}</span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-text-secondary">Fallbacks Handled</span>
                      <span className="font-mono text-brand-light">{p.fallback_count}</span>
                    </div>

                    <div className="flex justify-between items-center pt-2 border-t border-border-subtle">
                      <span className="text-text-secondary">Avg Latency</span>
                      <span className="font-mono text-white">{p.avg_latency_ms} ms</span>
                    </div>

                    <div className="flex justify-between items-center">
                      <span className="text-text-secondary">Est. Tokens</span>
                      <span className="font-mono text-white">{p.total_estimated_tokens}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-xs text-text-muted py-10">Failed to load telemetry metrics</div>
      )}
    </div>
  );
}
