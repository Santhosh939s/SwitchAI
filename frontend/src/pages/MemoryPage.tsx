import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  getConversations,
  getConversationMemories,
  createMemory,
  updateMemory,
  deleteMemory,
} from '../services/api';

interface MemoryItem {
  id: string;
  conversation_id: string;
  category: string;
  key: string;
  value: string;
  is_pinned: boolean;
  created_at: string;
}

interface Conversation {
  id: string;
  title: string;
}

const CATEGORIES = [
  { id: 'goal', name: 'Goals', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  { id: 'fact', name: 'Facts', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  { id: 'decision', name: 'Decisions', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
  { id: 'constraint', name: 'Constraints', color: 'bg-red-500/20 text-red-300 border-red-500/30' },
  { id: 'preference', name: 'Preferences', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
  { id: 'project_context', name: 'Project Context', color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' },
];

export function MemoryPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConvId, setSelectedConvId] = useState<string>('');
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  // New Memory Form
  const [newCategory, setNewCategory] = useState('fact');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [newPinned, setNewPinned] = useState(false);

  useEffect(() => {
    getConversations().then((data) => {
      setConversations(data);
      if (data.length > 0) {
        setSelectedConvId(data[0].id);
      } else {
        setLoading(false);
      }
    });
  }, []);

  const loadMemories = async (convId: string) => {
    if (!convId) return;
    setLoading(true);
    try {
      const data = await getConversationMemories(convId);
      setMemories(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedConvId) {
      loadMemories(selectedConvId);
    }
  }, [selectedConvId]);

  const handleAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim() || !selectedConvId) return;

    try {
      await createMemory(selectedConvId, newCategory, newKey.trim(), newValue.trim(), newPinned);
      setNewKey('');
      setNewValue('');
      setNewPinned(false);
      await loadMemories(selectedConvId);
    } catch (err) {
      console.error('Failed to create memory', err);
    }
  };

  const handleTogglePin = async (mem: MemoryItem) => {
    try {
      await updateMemory(mem.id, { is_pinned: !mem.is_pinned });
      await loadMemories(selectedConvId);
    } catch (err) {
      console.error('Failed to pin memory', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteMemory(id);
      await loadMemories(selectedConvId);
    } catch (err) {
      console.error('Failed to delete memory', err);
    }
  };

  const getCategoryBadge = (category: string) => {
    const cat = CATEGORIES.find((c) => c.id === category) || { name: category, color: 'bg-white/10 text-white' };
    return (
      <span className={`px-2.5 py-1 rounded text-[10px] font-semibold uppercase border ${cat.color}`}>
        {cat.name}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-neutral-bg1 text-white p-6 max-w-5xl mx-auto space-y-8">
      <div className="flex justify-between items-center pb-6 border-b border-border">
        <div>
          <Link to="/chat" className="text-sm font-medium text-text-muted hover:text-white transition-colors">
            ← Back to Chat
          </Link>
          <h1 className="text-3xl font-bold tracking-tight text-white mt-2">Shared Memory Inspector</h1>
          <p className="text-sm text-text-secondary mt-1">
            Provider-independent durable facts, goals, and architectural decisions attached across models.
          </p>
        </div>

        {conversations.length > 0 && (
          <div className="flex items-center space-x-3">
            <span className="text-xs text-text-muted">Conversation:</span>
            <select
              value={selectedConvId}
              onChange={(e) => setSelectedConvId(e.target.value)}
              className="px-3 py-1.5 rounded-lg bg-neutral-bg2 border border-border text-xs text-white focus:border-brand outline-none"
            >
              {conversations.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Add Memory Form */}
      {selectedConvId && (
        <form onSubmit={handleAddMemory} className="glass-card p-6 border border-border space-y-4">
          <h3 className="text-sm font-semibold text-white">Add Durable Shared Memory Item</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <select
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              className="px-3 py-2 rounded-lg bg-neutral-bg2 border border-border text-xs text-white focus:border-brand outline-none"
            >
              {CATEGORIES.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>

            <input
              type="text"
              placeholder="Key (e.g. Backend Framework)"
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
              className="px-3 py-2 rounded-lg bg-neutral-bg2 border border-border text-xs text-white focus:border-brand outline-none"
            />

            <input
              type="text"
              placeholder="Value (e.g. FastAPI with PostgreSQL)"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              className="px-3 py-2 rounded-lg bg-neutral-bg2 border border-border text-xs text-white focus:border-brand outline-none"
            />

            <div className="flex items-center space-x-3">
              <label className="flex items-center space-x-2 text-xs text-text-secondary cursor-pointer">
                <input
                  type="checkbox"
                  checked={newPinned}
                  onChange={(e) => setNewPinned(e.target.checked)}
                  className="rounded border-border text-brand focus:ring-brand"
                />
                <span>Pin High Priority</span>
              </label>

              <button
                type="submit"
                className="flex-1 py-2 px-3 rounded-lg bg-brand hover:bg-brand-hover text-white text-xs font-medium transition-colors"
              >
                + Add Memory
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Memory List */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider">
          Active Shared Memories ({memories.length})
        </h3>

        {loading ? (
          <div className="p-8 text-center text-xs text-text-muted animate-pulse">Loading memories...</div>
        ) : memories.length === 0 ? (
          <div className="glass-card p-8 text-center text-xs text-text-muted border border-border">
            No memories attached to this conversation yet. Send messages in chat or manually add memories above.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {memories.map((m) => (
              <div key={m.id} className="glass-card p-5 border border-border flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between items-start">
                    {getCategoryBadge(m.category)}
                    <button
                      onClick={() => handleTogglePin(m)}
                      title={m.is_pinned ? 'Unpin' : 'Pin Memory'}
                      className={`text-xs px-2 py-0.5 rounded border transition-colors ${
                        m.is_pinned
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                          : 'bg-white/5 text-text-muted border-border hover:text-white'
                      }`}
                    >
                      {m.is_pinned ? '★ Pinned' : '☆ Pin'}
                    </button>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-white">{m.key}</h4>
                    <p className="text-xs text-text-secondary mt-1 leading-relaxed bg-black/20 p-2.5 rounded border border-border-subtle font-mono">
                      {m.value}
                    </p>
                  </div>
                </div>

                <div className="flex justify-between items-center pt-2 border-t border-border-subtle text-[10px] text-text-muted">
                  <span>Created: {new Date(m.created_at).toLocaleDateString()}</span>
                  <button onClick={() => handleDelete(m.id)} className="text-red-400 hover:underline">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
