import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  getProviderStatuses,
  connectProvider,
  testProviderConnection,
  disconnectProvider,
} from '../services/api';

interface ProviderStatus {
  provider: string;
  status: 'HEALTHY' | 'UNHEALTHY' | 'CREDENTIALS_SAVED' | 'NOT_CONNECTED' | 'RUNNING' | 'NOT_RUNNING';
  is_connected: boolean;
  is_healthy: boolean;
  default_model?: string;
  available_models: string[];
  updated_at?: string;
}

const PROVIDER_METADATA: Record<string, { title: string; desc: string; iconBg: string }> = {
  local: {
    title: 'Local AI (Offline Model)',
    desc: 'Self-hosted quantized model (Qwen2.5 / Llama) running on local CPU server via llama.cpp or LM Studio.',
    iconBg: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  },
  anthropic: {
    title: 'Anthropic Claude',
    desc: 'Claude 3.5 Sonnet, Opus & Haiku models for deep analysis and reasoning.',
    iconBg: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  },
  gemini: {
    title: 'Google Gemini',
    desc: 'Gemini 3.5 Flash & Pro models for long-context workloads.',
    iconBg: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  },
  openai: {
    title: 'OpenAI GPT',
    desc: 'GPT-4o, GPT-4o mini, and o1 models for general intelligence & coding.',
    iconBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  },
  deepseek: {
    title: 'DeepSeek AI',
    desc: 'DeepSeek-V3, DeepSeek-Coder & DeepSeek-R1 models for open reasoning & coding.',
    iconBg: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  },
  groq: {
    title: 'Groq LPU',
    desc: 'Ultra-fast LPU inference for Llama 3.3 70B & Mixtral models at 500+ tokens/sec.',
    iconBg: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  },
  mistral: {
    title: 'Mistral AI',
    desc: 'Mistral Large & Codestral state-of-the-art European open AI models.',
    iconBg: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  },
  cohere: {
    title: 'Cohere Command',
    desc: 'Command R+ models optimized for enterprise RAG and structured output.',
    iconBg: 'bg-teal-500/20 text-teal-400 border-teal-500/30',
  },
};

export function ProvidersPage() {
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [activeInputProvider, setActiveInputProvider] = useState<string | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<{ provider: string; type: 'success' | 'error'; text: string } | null>(null);

  const fetchProviders = async () => {
    try {
      const data = await getProviderStatuses();
      setProviders(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const handleConnect = async (provider: string) => {
    if (provider !== 'local' && !apiKeyInput.trim()) return;
    setActionLoading(provider);
    setFeedbackMessage(null);

    try {
      await connectProvider(provider, apiKeyInput.trim() || 'local_native');
      setFeedbackMessage({
        provider,
        type: 'success',
        text: `Successfully saved ${PROVIDER_METADATA[provider]?.title || provider}.`,
      });
      setApiKeyInput('');
      setActiveInputProvider(null);
      await fetchProviders();
    } catch (err: any) {
      setFeedbackMessage({
        provider,
        type: 'error',
        text: err.message || 'Failed to save provider.',
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleTest = async (provider: string) => {
    setActionLoading(provider);
    setFeedbackMessage(null);

    try {
      const res = await testProviderConnection(provider);
      if (res.is_successful) {
        setFeedbackMessage({
          provider,
          type: 'success',
          text: `Test successful! Status: HEALTHY (${res.latency_ms?.toFixed(1) || 10}ms)`,
        });
      } else {
        setFeedbackMessage({
          provider,
          type: 'error',
          text: `Test failed: ${res.message}`,
        });
      }
      await fetchProviders();
    } catch (err: any) {
      setFeedbackMessage({
        provider,
        type: 'error',
        text: err.message || 'Test failed.',
      });
    } finally {
      setActionLoading(null);
    }
  };

  const handleDisconnect = async (provider: string) => {
    setActionLoading(provider);
    setFeedbackMessage(null);

    try {
      await disconnectProvider(provider);
      setFeedbackMessage({
        provider,
        type: 'success',
        text: `Disconnected ${PROVIDER_METADATA[provider]?.title || provider}.`,
      });
      await fetchProviders();
    } catch (err: any) {
      setFeedbackMessage({
        provider,
        type: 'error',
        text: err.message || 'Failed to disconnect.',
      });
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusBadge = (status: ProviderStatus['status'], isHealthy: boolean, isLocal: boolean) => {
    if (isLocal) {
      if (isHealthy || status === 'HEALTHY' || status === 'RUNNING') {
        return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">● Local Server Running</span>;
      }
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">✕ Local Server Offline</span>;
    }

    if (status === 'HEALTHY' || isHealthy) {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20">● HEALTHY</span>;
    }
    if (status === 'CREDENTIALS_SAVED') {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">🔑 Key Saved (Untested)</span>;
    }
    if (status === 'UNHEALTHY') {
      return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">▲ UNHEALTHY</span>;
    }
    return <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-neutral-bg4 text-text-muted border border-border">NOT_CONNECTED</span>;
  };

  const filteredProviders = providers.filter((p) => {
    const meta = PROVIDER_METADATA[p.provider] || { title: p.provider, desc: '' };
    const q = searchQuery.toLowerCase().trim();
    return p.provider.toLowerCase().includes(q) || meta.title.toLowerCase().includes(q) || meta.desc.toLowerCase().includes(q);
  });

  return (
    <div className="min-h-screen bg-neutral-bg1 text-white p-6 max-w-5xl mx-auto space-y-8">
      {/* Header Navigation & Search */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-6 border-b border-border gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <Link to="/chat" className="text-sm font-medium text-text-muted hover:text-white transition-colors">
              ← Back to Chat
            </Link>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white mt-2">AI Provider Connections</h1>
          <p className="text-sm text-text-secondary mt-1">
            Connect official cloud provider keys or self-host a local OpenAI-compatible inference server.
          </p>
        </div>

        {/* Search Bar for Connections */}
        <div className="relative w-full md:w-72">
          <input
            type="text"
            placeholder="🔍 Search providers (Local AI, DeepSeek, Claude...)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3.5 py-2 rounded-xl bg-neutral-bg2 border border-border focus:border-brand text-xs text-white placeholder-text-muted outline-none transition-colors"
          />
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-text-muted animate-pulse">Loading provider statuses...</div>
      ) : filteredProviders.length === 0 ? (
        <div className="glass-card p-12 text-center text-xs text-text-muted border border-border">
          No AI providers match "{searchQuery}"
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {filteredProviders.map((p) => {
            const meta = PROVIDER_METADATA[p.provider] || { title: p.provider, desc: '', iconBg: 'bg-white/10' };
            const isInputActive = activeInputProvider === p.provider;
            const isProcessing = actionLoading === p.provider;
            const msg = feedbackMessage?.provider === p.provider ? feedbackMessage : null;
            const isLocal = p.provider === 'local';

            return (
              <div key={p.provider} className="glass-card p-6 border border-border flex flex-col justify-between space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className={`px-3 py-1.5 rounded-lg text-xs font-bold border ${meta.iconBg}`}>
                      {meta.title}
                    </span>
                    {getStatusBadge(p.status, p.is_healthy, isLocal)}
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold text-white">{meta.title}</h3>
                    <p className="text-xs text-text-secondary mt-1 leading-relaxed">{meta.desc}</p>
                  </div>

                  {p.available_models.length > 0 && (
                    <div className="text-xs text-text-muted space-y-1 bg-black/20 p-3 rounded-lg border border-border-subtle">
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-text-secondary">Discovered Models:</span>
                        <span className="font-mono text-brand-light">{p.available_models.length}</span>
                      </div>
                      <div className="font-mono text-brand-light truncate">{p.default_model || p.available_models[0]}</div>
                    </div>
                  )}

                  {msg && (
                    <div className={`p-2.5 rounded-lg text-xs border ${msg.type === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
                      {msg.text}
                    </div>
                  )}
                </div>

                <div className="space-y-3 pt-4 border-t border-border-subtle">
                  {isLocal ? (
                    <button
                      onClick={() => handleTest('local')}
                      disabled={isProcessing}
                      className="w-full py-2 px-3 rounded-lg bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition-colors disabled:opacity-50"
                    >
                      {isProcessing ? 'Checking Server...' : 'Test Local Server Health'}
                    </button>
                  ) : p.is_connected ? (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleTest(p.provider)}
                        disabled={isProcessing}
                        className="flex-1 py-2 px-3 rounded-lg bg-white/5 hover:bg-white/10 text-white text-xs font-medium border border-border transition-colors disabled:opacity-50"
                      >
                        {isProcessing ? 'Testing...' : 'Test Connection'}
                      </button>
                      <button
                        onClick={() => handleDisconnect(p.provider)}
                        disabled={isProcessing}
                        className="py-2 px-3 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 text-xs font-medium border border-red-500/20 transition-colors disabled:opacity-50"
                      >
                        Disconnect
                      </button>
                    </div>
                  ) : (
                    <div>
                      {isInputActive ? (
                        <div className="space-y-2">
                          <input
                            type="password"
                            placeholder={`Enter ${meta.title} API key`}
                            value={apiKeyInput}
                            onChange={(e) => setApiKeyInput(e.target.value)}
                            className="w-full px-3 py-2 rounded-lg bg-neutral-bg2 border border-border focus:border-brand text-xs text-white placeholder-text-muted focus:outline-none"
                          />
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleConnect(p.provider)}
                              disabled={isProcessing || !apiKeyInput.trim()}
                              className="flex-1 py-1.5 px-3 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-medium transition-colors disabled:opacity-50"
                            >
                              {isProcessing ? 'Connecting...' : 'Save & Connect'}
                            </button>
                            <button
                              onClick={() => {
                                setActiveInputProvider(null);
                                setApiKeyInput('');
                              }}
                              className="py-1.5 px-3 rounded-lg glass text-text-muted hover:text-white text-xs"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            setActiveInputProvider(p.provider);
                            setApiKeyInput('');
                          }}
                          className="w-full py-2 px-3 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-medium transition-colors"
                        >
                          Connect API Key
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
