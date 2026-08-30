import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { checkBackendHealth } from '../services/api';

export function LandingPage() {
  const [health, setHealth] = useState<any>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'gemini' | 'claude' | 'openai' | 'rag'>('gemini');

  useEffect(() => {
    checkBackendHealth().then(setHealth);
  }, []);

  const toggleFaq = (index: number) => {
    setActiveFaq(activeFaq === index ? null : index);
  };

  return (
    <div className="min-h-screen text-white flex flex-col justify-between selection:bg-orange-500/30 selection:text-orange-200">
      {/* 1. Floating Glassmorphic Navbar */}
      <nav className="sticky top-4 z-50 max-w-6xl mx-auto w-[92%] px-6 py-3.5 rounded-2xl glass border border-white/10 flex items-center justify-between shadow-2xl transition-all">
        <Link to="/" className="flex items-center space-x-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-amber-500 via-orange-500 to-red-500 p-[1px] shadow-glow">
            <div className="w-full h-full bg-[#0A0A0B] rounded-[11px] flex items-center justify-center font-bold text-transparent bg-clip-text bg-gradient-to-tr from-orange-400 to-amber-300">
              ⚡
            </div>
          </div>
          <span className="font-extrabold text-xl tracking-tight text-white group-hover:text-orange-400 transition-colors">
            SwitchAI
          </span>
        </Link>

        <div className="hidden md:flex items-center space-x-8 text-xs font-medium text-text-secondary">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#architecture" className="hover:text-white transition-colors">Architecture</a>
          <a href="#passport" className="hover:text-white transition-colors">Context Passport</a>
          <a href="#providers" className="hover:text-white transition-colors">Providers</a>
          <a href="#faq" className="hover:text-white transition-colors">FAQ</a>
        </div>

        <div className="flex items-center space-x-3">
          <a
            href="https://github.com/Santhosh939s/Switch-AI-LatentForce"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex px-4 py-2 rounded-xl glass hover:bg-white/10 text-xs font-semibold text-white transition-colors border border-white/10"
          >
            GitHub
          </a>
          <Link
            to="/chat"
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-orange-600 via-orange-500 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-xs font-bold text-white shadow-glow transition-all"
          >
            Launch App
          </Link>
        </div>
      </nav>

      {/* 2. Hero Section */}
      <section className="pt-16 pb-20 px-6 max-w-5xl mx-auto text-center space-y-8">
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full glass border border-orange-500/30 text-xs font-semibold text-orange-300 animate-pulse">
          <span>✨ Powered by LatentForce • Multi-Provider RAG & Shared Memory</span>
        </div>

        <div className="space-y-4">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-tight">
            One Memory.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-amber-300 to-red-400">
              Infinite AI Models.
            </span>
          </h1>
          <p className="text-base md:text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed font-normal">
            Seamlessly orchestrate Google Gemini, Anthropic Claude, OpenAI GPT, and local RAG engines with zero context loss and zero token waste.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2">
          <Link
            to="/chat"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-orange-600 via-orange-500 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-sm font-bold text-white shadow-glow transition-all flex items-center justify-center space-x-2"
          >
            <span>Start Chatting Now</span>
            <span className="text-base">→</span>
          </Link>
          <Link
            to="/settings/providers"
            className="w-full sm:w-auto px-8 py-3.5 rounded-xl glass hover:bg-white/10 text-sm font-semibold text-white transition-colors border border-white/10"
          >
            Connect AI Providers
          </Link>
        </div>

        {/* 3. Interactive Live Model Switching Simulator Preview Card */}
        <div id="architecture" className="pt-10 max-w-4xl mx-auto">
          <div className="glass-card p-6 border border-white/10 shadow-2xl space-y-6 text-left">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-4 border-b border-white/10 gap-3">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-red-500/80"></span>
                <span className="w-3 h-3 rounded-full bg-yellow-500/80"></span>
                <span className="w-3 h-3 rounded-full bg-green-500/80"></span>
                <span className="text-xs font-mono text-text-muted ml-2">SwitchAI Unified Memory Architecture</span>
              </div>
              <div className="flex bg-black/40 p-1 rounded-xl border border-white/10 text-xs font-medium">
                <button
                  onClick={() => setActiveTab('gemini')}
                  className={`px-3 py-1 rounded-lg transition-all ${activeTab === 'gemini' ? 'bg-blue-500/20 text-blue-300 font-bold border border-blue-500/30' : 'text-text-muted'}`}
                >
                  Gemini
                </button>
                <button
                  onClick={() => setActiveTab('claude')}
                  className={`px-3 py-1 rounded-lg transition-all ${activeTab === 'claude' ? 'bg-orange-500/20 text-orange-300 font-bold border border-orange-500/30' : 'text-text-muted'}`}
                >
                  Claude
                </button>
                <button
                  onClick={() => setActiveTab('openai')}
                  className={`px-3 py-1 rounded-lg transition-all ${activeTab === 'openai' ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30' : 'text-text-muted'}`}
                >
                  GPT-4o
                </button>
                <button
                  onClick={() => setActiveTab('rag')}
                  className={`px-3 py-1 rounded-lg transition-all ${activeTab === 'rag' ? 'bg-purple-500/20 text-purple-300 font-bold border border-purple-500/30' : 'text-text-muted'}`}
                >
                  Offline RAG
                </button>
              </div>
            </div>

            {/* Simulated Live Chat State */}
            <div className="space-y-4 font-sans text-xs">
              <div className="flex justify-end">
                <div className="p-3 rounded-xl bg-orange-600/30 border border-orange-500/40 text-white max-w-lg">
                  I'm building a college food delivery platform using FastAPI, PostgreSQL, and React. Design the payment system.
                </div>
              </div>

              <div className="flex justify-start">
                <div className="p-4 rounded-xl glass-card border border-white/10 text-text-primary max-w-xl space-y-2">
                  <div className="flex items-center justify-between text-[11px] text-text-muted border-b border-white/5 pb-2">
                    <span className="font-semibold text-white">Assistant</span>
                    {activeTab === 'gemini' && <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 font-semibold text-[10px]">Google Gemini 3.6</span>}
                    {activeTab === 'claude' && <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-500/30 font-semibold text-[10px]">Claude 3.5 Sonnet</span>}
                    {activeTab === 'openai' && <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold text-[10px]">OpenAI GPT-4o</span>}
                    {activeTab === 'rag' && <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 font-semibold text-[10px]">SwitchAI RAG Engine</span>}
                  </div>

                  <p className="leading-relaxed">
                    {activeTab === 'gemini' && "Here is the long-context payment architecture. I recommend using an Asynchronous Webhook Processor with idempotent transaction keys to decouple webhooks from core APIs."}
                    {activeTab === 'claude' && "Challenging the payment architecture: Ensure you implement the Transactional Outbox Pattern in PostgreSQL before broadcasting events to avoid message loss during network partitions."}
                    {activeTab === 'openai' && "Here is the structured OpenAPI 3.0 REST specification for `/api/v1/payments/checkout` with Pydantic request validation and async Webhook handlers."}
                    {activeTab === 'rag' && "🤖 [SwitchAI RAG Knowledge Engine] Retained 3 shared memories (Goal: Food delivery app; Tech Stack: FastAPI, PostgreSQL, React). Cloud token cost: 0 tokens."}
                  </p>
                </div>
              </div>
            </div>

            {/* Context Passport Transfer Badge */}
            <div className="p-3.5 rounded-xl bg-orange-500/10 border border-orange-500/30 text-xs text-orange-200 flex flex-col sm:flex-row items-center justify-between gap-2">
              <div className="flex items-center space-x-2 font-mono">
                <span className="text-amber-400">⚡</span>
                <span>Context Passport Active: 3 Memories + 1 Goal + File Context Preserved</span>
              </div>
              <span className="text-[11px] font-bold text-green-400 bg-green-500/10 px-2 py-0.5 rounded border border-green-500/20">
                0 Context Loss ✓
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Provider Matrix Showcase */}
      <section id="providers" className="py-16 px-6 max-w-6xl mx-auto w-full space-y-10">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-extrabold tracking-tight text-white">Supported AI Ecosystem</h2>
          <p className="text-sm text-text-secondary max-w-lg mx-auto">
            Connect your official API keys or run self-hosted local models without vendor lock-in.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-card p-6 border border-white/10 space-y-3 hover:border-blue-500/40 transition-colors">
            <div className="px-3 py-1 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs font-bold inline-block">
              Google Gemini
            </div>
            <h3 className="text-base font-bold text-white">Gemini 3.6 / 1.5 Flash</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              1M+ token long-context window for deep document analysis and multi-turn reasoning.
            </p>
          </div>

          <div className="glass-card p-6 border border-white/10 space-y-3 hover:border-orange-500/40 transition-colors">
            <div className="px-3 py-1 rounded-lg bg-orange-500/20 text-orange-400 border border-orange-500/30 text-xs font-bold inline-block">
              Anthropic Claude
            </div>
            <h3 className="text-base font-bold text-white">Claude 3.5 Sonnet</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              State-of-the-art coding, architecture critique, and nuanced instruction following.
            </p>
          </div>

          <div className="glass-card p-6 border border-white/10 space-y-3 hover:border-emerald-500/40 transition-colors">
            <div className="px-3 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold inline-block">
              OpenAI
            </div>
            <h3 className="text-base font-bold text-white">GPT-4o & o3-mini</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              High-speed general intelligence, structured JSON generation, and mathematical reasoning.
            </p>
          </div>

          <div className="glass-card p-6 border border-white/10 space-y-3 hover:border-orange-500/40 transition-colors">
            <div className="px-3 py-1 rounded-lg bg-orange-500/20 text-orange-300 border border-orange-500/30 text-xs font-bold inline-block">
              Local AI & RAG
            </div>
            <h3 className="text-base font-bold text-white">llama.cpp / Qwen2.5</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Self-hosted CPU inference and 28-domain offline RAG knowledge retrieval.
            </p>
          </div>
        </div>
      </section>

      {/* 5. Feature Highlights (Web Search, RAG, Circuit Breaker) */}
      <section id="features" className="py-16 px-6 max-w-6xl mx-auto w-full space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-extrabold tracking-tight text-white">Architectural Highlights</h2>
          <p className="text-sm text-text-secondary max-w-lg mx-auto">
            Engineered for reliability, zero key exposure, and token-efficient memory retention.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-card p-8 border border-white/10 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-2xl text-blue-400">
              🌐
            </div>
            <h3 className="text-lg font-bold text-white">Multi-Source Web Search</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Keyless DuckDuckGo live web search with Wikipedia REST API fallback. Web search facts are automatically saved into SQLite shared memory.
            </p>
          </div>

          <div className="glass-card p-8 border border-white/10 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-orange-500/20 border border-orange-500/30 flex items-center justify-center text-2xl text-orange-400">
              🧠
            </div>
            <h3 className="text-lg font-bold text-white">Offline RAG Knowledge Engine</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              28-domain grounded technical knowledge base and acronym expansion. Provides zero-token-cost local answers when cloud API quotas are exhausted.
            </p>
          </div>

          <div className="glass-card p-8 border border-white/10 space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-2xl text-amber-400">
              ⚡
            </div>
            <h3 className="text-lg font-bold text-white">Circuit Breaker & Fallback</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Automatic rate limit (429) detection and circuit breaker rerouting. Seamlessly shifts tasks to secondary healthy providers without losing thread state.
            </p>
          </div>
        </div>
      </section>

      {/* 6. Accordion FAQ Section */}
      <section id="faq" className="py-16 px-6 max-w-4xl mx-auto w-full space-y-8">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-extrabold tracking-tight text-white">Frequently Asked Questions</h2>
          <p className="text-sm text-text-secondary">Everything you need to know about SwitchAI architecture.</p>
        </div>

        <div className="space-y-4">
          {[
            {
              q: "How does SwitchAI preserve context across different AI models?",
              a: "SwitchAI owns the conversation state, memories, goals, and summaries in a local SQLite database. When you switch models, SwitchAI packages this context into a standardized ContextPackage and translates it into the target model's system prompt format."
            },
            {
              q: "Are my API keys secure?",
              a: "Yes. Your API keys are encrypted at rest using 32-byte Fernet symmetric encryption keys. They are stored only on the backend and are never sent to the browser or logged in plaintext."
            },
            {
              q: "What happens when an AI model hits a rate limit (HTTP 429)?",
              a: "SwitchAI's Circuit Breaker automatically detects rate limits and temporary service outages. It instantly reroutes your request to the next healthy connected provider in your fallback chain without resetting your conversation or losing context."
            },
            {
              q: "Can I run SwitchAI completely offline?",
              a: "Yes. SwitchAI includes a local provider adapter for llama.cpp and LM Studio (http://127.0.0.1:8080/v1) and an embedded 28-domain RAG Knowledge Engine."
            }
          ].map((faq, idx) => (
            <div key={idx} className="glass-card border border-white/10 overflow-hidden">
              <button
                onClick={() => toggleFaq(idx)}
                className="w-full px-6 py-4 text-left text-sm font-semibold text-white flex justify-between items-center hover:bg-white/5 transition-colors"
              >
                <span>{faq.q}</span>
                <span className="text-orange-400 font-mono text-lg">{activeFaq === idx ? '−' : '+'}</span>
              </button>
              {activeFaq === idx && (
                <div className="px-6 pb-5 text-xs text-text-secondary leading-relaxed border-t border-white/5 pt-3">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 7. Modern Footer */}
      <footer className="py-8 px-6 border-t border-white/10 max-w-6xl mx-auto w-full flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-text-muted">
        <div className="flex items-center space-x-3">
          <span className="font-extrabold text-white">SwitchAI</span>
          <span>•</span>
          <span>BuildSprint 2026</span>
        </div>

        <div className="flex items-center space-x-2">
          {health ? (
            <span className={`font-mono flex items-center space-x-1.5 ${health.status === 'healthy' ? 'text-green-400' : 'text-red-400'}`}>
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              <span>● All Systems Operational</span>
            </span>
          ) : (
            <span className="font-mono text-yellow-400">Checking system status...</span>
          )}
        </div>
      </footer>
    </div>
  );
}
