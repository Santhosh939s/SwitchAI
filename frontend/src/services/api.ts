const API_BASE = '/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('switchai_token');
}

export function setAuthToken(token: string): void {
  localStorage.setItem('switchai_token', token);
}

export function removeAuthToken(): void {
  localStorage.removeItem('switchai_token');
}

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(endpoint, {
    ...options,
    headers,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || `Request failed with status ${res.status}`);
  }

  return data;
}

export async function checkBackendHealth() {
  try {
    const res = await fetch('/health');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err: any) {
    return { status: 'error', message: err.message };
  }
}

export async function registerUser(email: string, password: string) {
  const data = await apiRequest(`${API_BASE}/auth/register`, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

export async function loginUser(email: string, password: string) {
  const data = await apiRequest(`${API_BASE}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (data.access_token) {
    setAuthToken(data.access_token);
  }
  return data;
}

export async function logoutUser() {
  try {
    await apiRequest(`${API_BASE}/auth/logout`, { method: 'POST' });
  } finally {
    removeAuthToken();
  }
}

export async function getCurrentUser() {
  return await apiRequest(`${API_BASE}/auth/me`, { method: 'GET' });
}

// Provider APIs
export async function getProviderStatuses() {
  return await apiRequest(`${API_BASE}/providers`, { method: 'GET' });
}

export async function connectProvider(provider: string, apiKey: string, defaultModel?: string) {
  return await apiRequest(`${API_BASE}/providers/${provider}/connect`, {
    method: 'POST',
    body: JSON.stringify({ api_key: apiKey, default_model: defaultModel }),
  });
}

export async function testProviderConnection(provider: string) {
  return await apiRequest(`${API_BASE}/providers/${provider}/test`, {
    method: 'POST',
  });
}

export async function disconnectProvider(provider: string) {
  return await apiRequest(`${API_BASE}/providers/${provider}`, {
    method: 'DELETE',
  });
}

// Conversation APIs
export async function getConversations(searchQuery?: string) {
  const url = searchQuery ? `${API_BASE}/conversations?q=${encodeURIComponent(searchQuery)}` : `${API_BASE}/conversations`;
  return await apiRequest(url, { method: 'GET' });
}

export async function createConversation(title?: string, activeProvider?: string) {
  return await apiRequest(`${API_BASE}/conversations`, {
    method: 'POST',
    body: JSON.stringify({ title, active_provider: activeProvider }),
  });
}

export async function getConversationMessages(conversationId: string) {
  return await apiRequest(`${API_BASE}/conversations/${conversationId}/messages`, { method: 'GET' });
}

export async function sendMessage(conversationId: string, content: string, provider?: string, model?: string, webSearchEnabled?: boolean) {
  return await apiRequest(`${API_BASE}/conversations/${conversationId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content, provider, model, web_search_enabled: webSearchEnabled }),
  });
}

export async function renameConversation(conversationId: string, title: string) {
  return await apiRequest(`${API_BASE}/conversations/${conversationId}`, {
    method: 'PATCH',
    body: JSON.stringify({ title }),
  });
}

export async function deleteConversation(conversationId: string) {
  return await apiRequest(`${API_BASE}/conversations/${conversationId}`, {
    method: 'DELETE',
  });
}

export async function getContextPassport(conversationId: string) {
  return await apiRequest(`${API_BASE}/conversations/${conversationId}/passport`, { method: 'GET' });
}

// Memory APIs
export async function getConversationMemories(conversationId: string) {
  return await apiRequest(`${API_BASE}/conversations/${conversationId}/memory`, { method: 'GET' });
}

export async function createMemory(conversationId: string, category: string, key: string, value: string, isPinned = false) {
  return await apiRequest(`${API_BASE}/conversations/${conversationId}/memory`, {
    method: 'POST',
    body: JSON.stringify({ category, key, value, is_pinned: isPinned }),
  });
}

export async function updateMemory(memoryId: string, data: { category?: string; key?: string; value?: string; is_pinned?: boolean }) {
  return await apiRequest(`${API_BASE}/memory/${memoryId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function deleteMemory(memoryId: string) {
  return await apiRequest(`${API_BASE}/memory/${memoryId}`, {
    method: 'DELETE',
  });
}

// Router APIs
export async function previewRoute(message: string, priority = 'balanced') {
  return await apiRequest(`${API_BASE}/router/preview`, {
    method: 'POST',
    body: JSON.stringify({ message, priority }),
  });
}

// Usage APIs
export async function getUsageMetrics() {
  return await apiRequest(`${API_BASE}/usage`, { method: 'GET' });
}

// File Upload API
export async function uploadFile(conversationId: string, file: File) {
  const token = getAuthToken();
  const formData = new FormData();
  formData.append('conversation_id', conversationId);
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/files/upload`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || `File upload failed with status ${res.status}`);
  }

  return data;
}
