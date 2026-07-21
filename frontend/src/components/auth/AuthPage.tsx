import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

type Mode = "login" | "register";

export default function AuthPage({ mode }: { mode: Mode }) {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") {
        await login(username.trim(), password);
      } else {
        await register(username.trim(), password, email.trim() || undefined);
      }
      navigate("/");
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "操作失败，请重试");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-stage">
      <div className="auth-frame panel">
        <div className="brand-mark">
          短<span>镜</span>
        </div>
        <h1>{mode === "login" ? "回到工作台" : "开启你的第一支片"}</h1>
        <p>
          {mode === "login"
            ? "用一条主题，生成可渲染的短视频脚本。"
            : "注册后即可写脚本、渲染导出，全程在同一条流水线完成。"}
        </p>
        <form className="field-grid" onSubmit={onSubmit}>
          <div className="field">
            <label htmlFor="username">用户名</label>
            <input
              id="username"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
            />
          </div>
          {mode === "register" && (
            <div className="field">
              <label htmlFor="email">邮箱（可选）</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          )}
          <div className="field">
            <label htmlFor="password">密码</label>
            <input
              id="password"
              type="password"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>
          {error && <div className="error-text">{error}</div>}
          <div className="actions">
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? "处理中…" : mode === "login" ? "登录" : "注册并进入"}
            </button>
          </div>
        </form>
        <div className="auth-switch">
          {mode === "login" ? (
            <>
              还没有账号？ <Link to="/register">去注册</Link>
            </>
          ) : (
            <>
              已有账号？ <Link to="/login">去登录</Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
