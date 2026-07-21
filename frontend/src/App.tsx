import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { BrowserRouter } from "react-router-dom";
import AuthPage from "./components/auth/AuthPage";
import Studio from "./components/studio/Studio";
import { useAuth } from "./contexts/AuthContext";

function Private({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="auth-stage">
        <div className="muted">载入中…</div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function Shell() {
  const { user, logout } = useAuth();
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">
            短<span>镜</span>
          </div>
          <div className="brand-sub">AI 短视频工作台</div>
        </div>
        <div className="actions" style={{ marginTop: 0 }}>
          <span className="muted">{user?.username}</span>
          <button className="btn btn-ghost" type="button" onClick={logout}>
            退出
          </button>
        </div>
      </header>
      <main className="shell-main">
        <Studio />
      </main>
      <footer className="footer">
        <span>短镜 AVM · v2</span>
        <span className="muted">主题 → 脚本 → 渲染，一条线做完</span>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<AuthPage mode="login" />} />
        <Route path="/register" element={<AuthPage mode="register" />} />
        <Route
          path="/*"
          element={
            <Private>
              <Shell />
            </Private>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
