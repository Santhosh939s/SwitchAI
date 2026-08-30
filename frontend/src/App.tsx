import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { ChatPage } from './pages/ChatPage';
import { ProvidersPage } from './pages/ProvidersPage';
import { MemoryPage } from './pages/MemoryPage';
import { UsagePage } from './pages/UsagePage';
import { ProtectedLayout } from './components/layout/ProtectedLayout';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route element={<ProtectedLayout />}>
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/settings/providers" element={<ProvidersPage />} />
            <Route path="/settings/memory" element={<MemoryPage />} />
            <Route path="/usage" element={<UsagePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
