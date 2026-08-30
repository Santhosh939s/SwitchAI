import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getConversations,
  createConversation,
  getConversationMessages,
  sendMessage,
  deleteConversation,
  renameConversation,
  getContextPassport,
  previewRoute,
  getProviderStatuses,
  uploadFile,
} from '../services/api';

interface Conversation {
  id: string;
  title: string;
  active_provider?: string;
  active_model?: string;
  updated_at: string;
}

interface Message {
  id: string;
  sender_role: 'user' | 'assistant';
  content: string;
  provider?: string;
  model?: string;
  latency_ms?: number;
  token_estimate?: number;
  created_at: string;
}

interface ContextPassport {
  conversation_id: string;
  user_goal: string;
  facts: string[];
  decisions: string[];
  constraints: string[];
  open_questions: string[];
  summary: string;
  total_memories_transferred: number;
  total_messages_transferred: number;
  has_summary: boolean;
  active_provider: string;
}

interface ProviderStatus {
  provider: string;
  status: string;
  is_connected: boolean;
  default_model?: string;
  available_models: string[];
}

const ALL_PROVIDERS = [
  { id: 'auto', name: '✨ Auto (Smart Router)', badgeBg: 'bg-brand-subtle text-brand-light border-brand/30' },
  { id: 'gemini', name: 'Gemini (Google)', badgeBg: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  { id: 'openai', name: 'GPT (OpenAI)', badgeBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' },
  { id: 'anthropic', name: 'Claude (Anthropic)', badgeBg: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
  { id: 'deepseek', name: 'DeepSeek (DeepSeek AI)', badgeBg: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30' },
  { id: 'groq', name: 'Llama 3.3 (Groq LPU)', badgeBg: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  { id: 'mistral', name: 'Mistral (Mistral AI)', badgeBg: 'bg-amber-500/20 text-amber-400 border-amber-500/30' },
  { id: 'cohere', name: 'Command R+ (Cohere)', badgeBg: 'bg-teal-500/20 text-teal-400 border-teal-500/30' },
  { id: 'local', name: '💻 Local AI (Self-Hosted)', badgeBg: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' },
];

export function ChatPage() {
  const { user, logout } = useAuth();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [passport, setPassport] = useState<ContextPassport | null>(null);
  const [providerStatuses, setProviderStatuses] = useState<ProviderStatus[]>([]);
  const [connectedProviders, setConnectedProviders] = useState<string[]>([]);
  const [input, setInput] = useState('');
  const [selectedProvider, setSelectedProvider] = useState<string>('auto');
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [routingPriority, setRoutingPriority] = useState<string>('balanced');
  const [routePreview, setRoutePreview] = useState<{ rationale: string; task_category: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [editingTitleId, setEditingTitleId] = useState<string | null>(null);
  const [titleInput, setTitleInput] = useState('');
  const [deletingConvId, setDeletingConvId] = useState<string | null>(null);
  const [switchNotification, setSwitchNotification] = useState<{ text: string; sub: string } | null>(null);
  const [showPassportSidebar, setShowPassportSidebar] = useState(true);
  const [attachedFiles, setAttachedFiles] = useState<{ id: string; name: string }[]>([]);
  const [fileUploading, setFileUploadLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    let conv = activeConv;
    if (!conv) {
      try {
        const createdConv = await createConversation('New Conversation', selectedProvider);
        setConversations([createdConv, ...conversations]);
        setActiveConv(createdConv);
        conv = createdConv;
      } catch (err) {
        console.error('Failed to create conversation for file upload', err);
        return;
      }
    }

    if (!conv) return;

    setFileUploadLoading(true);
    try {
      const res = await uploadFile(conv.id, file);
      setAttachedFiles((prev) => [...prev, { id: res.id, name: res.filename }]);
      await loadPassport(conv.id);
    } catch (err: any) {
      console.error('File upload failed', err);
    } finally {
      setFileUploadLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const loadConversations = async (query?: string) => {
    try {
      const data = await getConversations(query);
      setConversations(data);
      if (data.length > 0 && !activeConv && !query) {
        setActiveConv(data[0]);
      }
    } catch (err) {
      console.error('Failed to load conversations', err);
    }
  };

  const loadProviderStatuses = async () => {
    try {
      const statuses: ProviderStatus[] = await getProviderStatuses();
      setProviderStatuses(statuses);
      const connected = statuses.filter((p) => p.is_connected).map((p) => p.provider.toLowerCase());
      setConnectedProviders(connected);
    } catch (err) {
      console.error('Failed to load provider statuses', err);
    }
  };

  const loadPassport = async (convId: string) => {
    try {
      const data = await getContextPassport(convId);
      setPassport(data);
    } catch (err) {
      console.error('Failed to load context passport', err);
    }
  };

  useEffect(() => {
    loadConversations(searchQuery);
    loadProviderStatuses();
  }, [searchQuery]);

  useEffect(() => {
    if (activeConv) {
      setMessagesLoading(true);
      if (activeConv.active_provider) {
        setSelectedProvider(activeConv.active_provider);
        const provStatus = providerStatuses.find((p) => p.provider === activeConv.active_provider);
        if (provStatus && provStatus.available_models.length > 0) {
          const isModelValid = activeConv.active_model && provStatus.available_models.includes(activeConv.active_model);
          setSelectedModel(isModelValid ? activeConv.active_model! : provStatus.available_models[0]);
        } else if (activeConv.active_model) {
          setSelectedModel(activeConv.active_model);
        }
      } else if (activeConv.active_model) {
        setSelectedModel(activeConv.active_model);
      }
      getConversationMessages(activeConv.id)
        .then(setMessages)
        .catch(console.error)
        .finally(() => setMessagesLoading(false));

      loadPassport(activeConv.id);
    } else {
      setMessages([]);
      setPassport(null);
    }
  }, [activeConv?.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (selectedProvider === 'auto' && input.trim().length > 10) {
      const timer = setTimeout(() => {
        previewRoute(input.trim(), routingPriority)
          .then((res) => setRoutePreview({ rationale: res.rationale, task_category: res.task_category }))
          .catch(() => setRoutePreview(null));
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setRoutePreview(null);
    }
  }, [input, selectedProvider, routingPriority]);

  const handleProviderChange = (newProvider: string) => {
    if (newProvider === selectedProvider) return;
    const provName = ALL_PROVIDERS.find((p) => p.id === newProvider)?.name || newProvider;
    setSelectedProvider(newProvider);
    
    // Auto-select the default model for the new provider
    const provStatus = providerStatuses.find((p) => p.provider === newProvider);
    if (provStatus && provStatus.available_models.length > 0) {
      const isDefaultValid = provStatus.default_model && provStatus.available_models.includes(provStatus.default_model);
      setSelectedModel(isDefaultValid ? provStatus.default_model! : provStatus.available_models[0]);
    } else {
      setSelectedModel('');
    }

    setSwitchNotification({
      text: `Switching to ${provName}...`,
      sub: `Context Passport ready. ${passport?.total_memories_transferred || 3} memories + summary transferred. ✓ Context transferred`,
    });

    setTimeout(() => {
      setSwitchNotification(null);
    }, 4000);
  };

  const handleNewConversation = async () => {
    try {
      const conv = await createConversation('New Conversation', selectedProvider);
      setConversations([conv, ...conversations]);
      setActiveConv(conv);
    } catch (err) {
      console.error('Failed to create conversation', err);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    let conv = activeConv;
    if (!conv) {
      try {
        const createdConv = await createConversation('New Conversation', selectedProvider);
        setConversations([createdConv, ...conversations]);
        setActiveConv(createdConv);
        conv = createdConv;
      } catch (err) {
        console.error('Failed to create conversation', err);
        return;
      }
    }

    if (!conv) return;

    const currentText = input.trim();
    setInput('');
    setRoutePreview(null);
    setLoading(true);

    const tempUserMsg: Message = {
      id: 'temp-' + Date.now(),
      sender_role: 'user',
      content: currentText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const assistantMsg = await sendMessage(conv.id, currentText, selectedProvider, selectedModel || undefined);
      setMessages((prev) => [...prev.filter((m) => !m.id.startsWith('temp-')), tempUserMsg, assistantMsg]);
      await loadConversations(searchQuery);
      await loadPassport(conv.id);
    } catch (err: any) {
      const errorMsg: Message = {
        id: 'err-' + Date.now(),
        sender_role: 'assistant',
        content: `[Error] ${err.message || 'Failed to generate response'}`,
        provider: selectedProvider,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const confirmDeleteConv = async () => {
    if (!deletingConvId) return;
    try {
      await deleteConversation(deletingConvId);
      const updated = conversations.filter((c) => c.id !== deletingConvId);
      setConversations(updated);
      if (activeConv?.id === deletingConvId) {
        setActiveConv(updated.length > 0 ? updated[0] : null);
      }
    } catch (err) {
      console.error('Failed to delete conversation', err);
    } finally {
      setDeletingConvId(null);
    }
  };

  const handleRenameConv = async (id: string, newTitle: string) => {
    if (!newTitle.trim()) return;
    try {
      await renameConversation(id, newTitle.trim());
      setConversations(conversations.map((c) => (c.id === id ? { ...c, title: newTitle.trim() } : c)));
      if (activeConv?.id === id) {
        setActiveConv({ ...activeConv, title: newTitle.trim() });
      }
    } catch (err) {
      console.error('Failed to rename conversation', err);
    } finally {
      setEditingTitleId(null);
    }
  };

  const getProviderBadge = (providerId?: string) => {
    const prov = ALL_PROVIDERS.find((p) => p.id === providerId) || { name: providerId || 'AI', badgeBg: 'bg-white/10 text-white border-white/20' };
    return (
      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${prov.badgeBg}`}>
        {prov.name}
      </span>
    );
  };

  // Filter dropdown to show Auto + ONLY connected providers
  const connectedSet = new Set(
    providerStatuses
      .filter((p) => p.is_connected && p.status !== 'NOT_CONNECTED')
      .map((p) => p.provider.toLowerCase())
  );

  const availableDropdownProviders = [
    { id: 'auto', name: '✨ Auto (Smart Router)', badgeBg: 'bg-brand-subtle text-brand-light border-brand/30' },
    ...ALL_PROVIDERS.filter((p) => p.id !== 'auto' && connectedSet.has(p.id.toLowerCase()))
  ];

  return (
    <div className="h-screen bg-neutral-bg1 flex text-white overflow-hidden">
      {/* Delete Confirmation Modal */}
      {deletingConvId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="glass-card p-6 max-w-sm w-full space-y-4 border border-border">
            <h3 className="text-base font-bold text-white">Delete Conversation?</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              This action cannot be undone. All messages and shared memory associated with this conversation will be permanently removed.
            </p>
            <div className="flex space-x-3 pt-2">
              <button
                onClick={confirmDeleteConv}
                className="flex-1 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 text-xs font-medium transition-colors"
              >
                Delete
              </button>
              <button
                onClick={() => setDeletingConvId(null)}
                className="flex-1 py-2 rounded-lg glass text-text-secondary hover:text-white text-xs font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Left Sidebar */}
      <aside className="w-64 bg-neutral-bg2/80 border-r border-border flex flex-col justify-between p-4">
        <div className="space-y-3 overflow-hidden flex flex-col flex-1">
          <div className="flex items-center justify-between pb-2 border-b border-border-subtle">
            <span className="font-bold text-lg text-white tracking-tight">SwitchAI</span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-brand-subtle text-brand-light border border-brand/30">
              v0.1
            </span>
          </div>

          <button
            onClick={handleNewConversation}
            className="w-full py-2.5 px-3 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-medium transition-colors flex items-center justify-center space-x-2"
          >
            <span>+ New Conversation</span>
          </button>

          {/* Conversation Search Input */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-1.5 rounded-lg bg-neutral-bg2 border border-border focus:border-brand text-xs text-white placeholder-text-muted outline-none"
            />
          </div>

          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
            <div className="text-[11px] font-semibold text-text-muted px-2 py-1 uppercase tracking-wider">
              Recent Chats
            </div>
            {conversations.length === 0 ? (
              <div className="text-xs text-text-muted px-2 py-4 text-center">
                {searchQuery ? 'No matching chats found' : 'No conversations yet'}
              </div>
            ) : (
              conversations.map((c) => {
                const isActive = activeConv?.id === c.id;
                const isEditing = editingTitleId === c.id;

                return (
                  <div
                    key={c.id}
                    onClick={() => setActiveConv(c)}
                    className={`group relative flex items-center justify-between p-2.5 rounded-lg text-xs cursor-pointer transition-colors ${
                      isActive ? 'bg-white/10 text-white font-medium border border-white/10' : 'text-text-secondary hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    {isEditing ? (
                      <input
                        type="text"
                        autoFocus
                        value={titleInput}
                        onChange={(e) => setTitleInput(e.target.value)}
                        onBlur={() => handleRenameConv(c.id, titleInput)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleRenameConv(c.id, titleInput);
                        }}
                        className="bg-neutral-bg1 border border-brand rounded px-1.5 py-0.5 text-xs text-white outline-none w-full"
                      />
                    ) : (
                      <span className="truncate flex-1 pr-2">{c.title}</span>
                    )}

                    <div className="hidden group-hover:flex items-center space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingTitleId(c.id);
                          setTitleInput(c.title);
                        }}
                        title="Rename"
                        className="text-text-muted hover:text-white text-[10px] p-0.5"
                      >
                        ✎
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeletingConvId(c.id);
                        }}
                        title="Delete"
                        className="text-text-muted hover:text-red-400 text-[10px] p-0.5"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        <div className="pt-3 border-t border-border-subtle space-y-2">
          <Link
            to="/usage"
            className="w-full py-2 px-3 rounded-lg bg-white/5 hover:bg-white/10 text-text-secondary hover:text-white text-xs font-medium border border-border flex items-center justify-between transition-colors"
          >
            <span>📊 Usage Telemetry</span>
            <span className="text-[10px] text-green-400">View</span>
          </Link>

          <Link
            to="/settings/memory"
            className="w-full py-2 px-3 rounded-lg bg-white/5 hover:bg-white/10 text-text-secondary hover:text-white text-xs font-medium border border-border flex items-center justify-between transition-colors"
          >
            <span>🧠 Shared Memory</span>
            <span className="text-[10px] text-purple-400">Inspect</span>
          </Link>

          <Link
            to="/settings/providers"
            className="w-full py-2 px-3 rounded-lg bg-white/5 hover:bg-white/10 text-text-secondary hover:text-white text-xs font-medium border border-border flex items-center justify-between transition-colors"
          >
            <span>⚙ AI Providers</span>
            <span className="text-[10px] text-brand-light">
              {connectedProviders.length > 0 ? `${connectedProviders.length} Connected` : 'Manage'}
            </span>
          </Link>

          <div className="flex items-center justify-between px-2 pt-2">
            <span className="text-xs text-text-muted truncate max-w-[120px]">{user?.email}</span>
            <button onClick={logout} className="text-xs text-red-400 hover:underline">
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* Main Chat Panel */}
      <main className="flex-1 flex flex-col h-full bg-neutral-bg1 relative">
        {switchNotification && (
          <div className="absolute top-16 left-1/2 -translate-x-1/2 z-50 glass-card px-5 py-3 rounded-xl border border-brand/40 shadow-glow flex flex-col items-center text-center space-y-1 animate-fade-in">
            <div className="text-xs font-bold text-white flex items-center space-x-2">
              <span className="text-amber-400 animate-spin">⚡</span>
              <span>{switchNotification.text}</span>
            </div>
            <div className="text-[11px] text-brand-light font-mono">{switchNotification.sub}</div>
          </div>
        )}

        {/* Top Header */}
        <header className="px-6 py-3.5 border-b border-border bg-neutral-bg2/40 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <h2 className="text-sm font-semibold text-white max-w-xs truncate">
              {activeConv ? activeConv.title : 'New Chat'}
            </h2>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowPassportSidebar(!showPassportSidebar)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors flex items-center space-x-1.5 ${
                showPassportSidebar
                  ? 'bg-purple-500/20 text-purple-300 border-purple-500/40'
                  : 'bg-white/5 text-text-secondary border-border hover:text-white'
              }`}
            >
              <span>Passport</span>
            </button>

            {selectedProvider === 'auto' && (
              <div className="flex items-center space-x-1.5">
                <span className="text-[11px] text-text-muted">Priority:</span>
                <select
                  value={routingPriority}
                  onChange={(e) => setRoutingPriority(e.target.value)}
                  className="px-2.5 py-1 rounded bg-neutral-bg2 border border-border text-[11px] text-brand-light font-medium focus:border-brand outline-none"
                >
                  <option value="balanced">Balanced</option>
                  <option value="quality">Quality</option>
                  <option value="speed">Speed</option>
                  <option value="cost">Cost</option>
                </select>
              </div>
            )}

            <div className="flex items-center space-x-2">
              <span className="text-xs text-text-secondary font-medium">Routing Mode:</span>
              <select
                value={selectedProvider}
                onChange={(e) => handleProviderChange(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-neutral-bg2 border border-border text-xs text-white font-medium focus:border-brand outline-none"
              >
                {availableDropdownProviders.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>

            {selectedProvider !== 'auto' && (
              <div className="flex items-center space-x-2">
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-neutral-bg2 border border-border text-xs text-brand-light font-medium focus:border-brand outline-none"
                >
                  {providerStatuses.find(p => p.provider === selectedProvider)?.available_models.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </header>

        {/* Message Feed */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {!activeConv && messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4">
              <div className="p-4 rounded-full bg-brand-subtle text-brand-light border border-brand/30 text-2xl">
                ⚡
              </div>
              <h3 className="text-xl font-bold text-white">One memory. Many AI models.</h3>
              <p className="text-xs text-text-muted leading-relaxed">
                Select your preferred provider at the top. You can switch models mid-conversation without losing your place.
              </p>
            </div>
          ) : messagesLoading ? (
            <div className="text-center text-xs text-text-muted py-10 animate-pulse">Loading conversation history...</div>
          ) : (
            messages.map((m) => {
              const isUser = m.sender_role === 'user';
              return (
                <div key={m.id} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-1.5`}>
                  <div className="flex items-center space-x-2 text-[11px] text-text-muted">
                    <span>{isUser ? 'You' : 'Assistant'}</span>
                    {!isUser && getProviderBadge(m.provider)}
                    {m.latency_ms && <span className="font-mono text-[10px] text-text-muted">({m.latency_ms.toFixed(0)}ms)</span>}
                  </div>

                  <div
                    className={`p-4 rounded-xl text-xs leading-relaxed max-w-2xl border ${
                      isUser
                        ? 'bg-brand/20 border-brand/30 text-white rounded-br-none'
                        : 'glass-card border-border text-text-primary rounded-bl-none'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  </div>
                </div>
              );
            })
          )}
          {loading && (
            <div className="flex flex-col items-start space-y-1.5">
              <div className="flex items-center space-x-2 text-[11px] text-text-muted">
                <span>Assistant</span>
                {getProviderBadge(selectedProvider)}
              </div>
              <div className="glass-card p-3 rounded-xl text-xs text-brand-light border border-border animate-pulse">
                Routing & Generating response...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <footer className="p-4 border-t border-border bg-neutral-bg2/40 space-y-2">
          {attachedFiles.length > 0 && (
            <div className="max-w-4xl mx-auto flex flex-wrap gap-2 pb-1">
              {attachedFiles.map((f) => (
                <div key={f.id} className="px-2.5 py-1 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[11px] font-mono flex items-center space-x-1">
                  <span>📎 {f.name}</span>
                  <button
                    type="button"
                    onClick={() => setAttachedFiles((prev) => prev.filter((item) => item.id !== f.id))}
                    className="ml-1 text-text-muted hover:text-white"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          {routePreview && (
            <div className="max-w-4xl mx-auto px-3 py-1.5 rounded-lg bg-brand-subtle border border-brand/30 text-[11px] text-brand-light flex items-center justify-between font-mono animate-fade-in">
              <span>🎯 Auto Router Rationale: {routePreview.rationale}</span>
              <span className="uppercase text-[9px] px-1.5 py-0.5 rounded bg-brand/20 font-bold">{routePreview.task_category}</span>
            </div>
          )}

          <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-center">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".txt,.md,.json,.csv"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={fileUploading}
              title="Attach File Context (.txt, .md, .json, .csv)"
              className="absolute left-2.5 z-10 p-1.5 rounded-lg text-text-muted hover:text-white hover:bg-white/10 transition-colors"
            >
              {fileUploading ? '⏳' : '📎'}
            </button>

            <textarea
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e);
                }
              }}
              placeholder={
                selectedProvider === 'auto'
                  ? 'Message in Auto Mode (Router classifies task & selects optimal model)...'
                  : `Message using ${ALL_PROVIDERS.find((p) => p.id === selectedProvider)?.name || selectedProvider}...`
              }
              className="w-full py-3 pl-10 pr-24 rounded-xl bg-neutral-bg2 border border-border focus:border-brand focus:outline-none text-xs text-white placeholder-text-muted resize-none transition-colors"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2 px-4 py-1.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-medium transition-colors disabled:opacity-40"
            >
              Send
            </button>
          </form>
        </footer>
      </main>

      {/* Right Sidebar — Context Passport Panel */}
      {showPassportSidebar && (
        <aside className="w-80 bg-neutral-bg2/80 border-l border-border flex flex-col p-4 overflow-y-auto space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-border-subtle">
            <div className="flex items-center space-x-2">
              <span className="text-base">Passport</span>
              <span className="font-bold text-sm text-white tracking-tight">Context Passport</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
              Provider Independent
            </span>
          </div>

          {passport ? (
            <div className="space-y-5 text-xs">
              <div className="space-y-1.5">
                <div className="font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Goal</div>
                <div className="p-2.5 rounded-lg bg-black/30 border border-border-subtle text-white font-medium">
                  {passport.user_goal}
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Facts</div>
                <div className="space-y-1">
                  {passport.facts.map((f, i) => (
                    <div key={i} className="p-2 rounded bg-white/5 border border-border-subtle text-text-secondary">
                      • {f}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Decisions</div>
                <div className="space-y-1">
                  {passport.decisions.map((d, i) => (
                    <div key={i} className="p-2 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
                      • {d}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Constraints</div>
                <div className="space-y-1">
                  {passport.constraints.map((c, i) => (
                    <div key={i} className="p-2 rounded bg-red-500/10 border border-red-500/20 text-red-300">
                      • {c}
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Open Questions</div>
                <div className="space-y-1">
                  {passport.open_questions.map((q, i) => (
                    <div key={i} className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300">
                      • {q}
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-brand/10 border border-brand/30 space-y-2">
                <div className="font-semibold text-brand-light text-[11px] uppercase tracking-wider flex justify-between items-center">
                  <span>Transfer Status</span>
                  <span className="text-green-400">Ready ✓</span>
                </div>
                <div className="text-[11px] text-text-secondary space-y-1 font-mono">
                  <div>• {passport.total_memories_transferred} memories</div>
                  <div>• {passport.total_messages_transferred} recent messages</div>
                  <div>• {passport.has_summary ? '1 summary' : '0 summaries'}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-xs text-text-muted text-center py-10">Select or start a conversation to view Context Passport</div>
          )}
        </aside>
      )}
    </div>
  );
}
