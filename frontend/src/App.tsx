import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { useAuthStore } from './stores/authStore';
import MainLayout from './components/Layout/MainLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Chat from './pages/Chat';
import KnowledgeBase from './pages/KnowledgeBase';
import Profile from './pages/Profile';

function ProtectedRoute({ children, requireAdmin = false }: { children: React.ReactNode; requireAdmin?: boolean }) {
  const { isAuthenticated, isAdmin } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/chat" replace />;
  }

  return <>{children}</>;
}

function App() {
  const { loadFromStorage, isAuthenticated } = useAuthStore();

  useEffect(() => {
    loadFromStorage();
  }, []);

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 8,
        },
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={isAuthenticated ? <Navigate to="/chat" replace /> : <Login />} />
          <Route path="/register" element={isAuthenticated ? <Navigate to="/chat" replace /> : <Register />} />
          <Route path="/chat/:conversationId?" element={<ProtectedRoute><MainLayout><Chat /></MainLayout></ProtectedRoute>} />
          <Route path="/knowledge" element={<ProtectedRoute requireAdmin><MainLayout><KnowledgeBase /></MainLayout></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><MainLayout><Profile /></MainLayout></ProtectedRoute>} />
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
