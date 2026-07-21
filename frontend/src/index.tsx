import React from "react";
import ReactDOM from "react-dom/client";
import { ConfigProvider, theme } from "antd";
import App from "./App";
import { AuthProvider } from "./contexts/AuthContext";
import "./styles/global.css";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(
  <React.StrictMode>
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: "#c8f54b",
          colorBgBase: "#071422",
          colorTextBase: "#e8f0e6",
          fontFamily: '"Manrope", "PingFang SC", sans-serif',
          borderRadius: 10,
        },
      }}
    >
      <AuthProvider>
        <App />
      </AuthProvider>
    </ConfigProvider>
  </React.StrictMode>
);
