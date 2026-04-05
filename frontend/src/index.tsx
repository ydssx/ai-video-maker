import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';
import 'antd/dist/reset.css';
import './globalStyles.css';

const theme = {
  token: {
    colorPrimary: '#4f46e5',
    colorInfo: '#0ea5e9',
    borderRadius: 10,
    wireframe: false,
    fontFamily:
      "'DM Sans', 'Noto Sans SC', system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
  },
  components: {
    Button: { borderRadius: 10, controlHeight: 40 },
    Card: { borderRadiusLG: 16 },
    Input: { borderRadius: 10 },
    Select: { borderRadius: 10 },
    Menu: { itemBorderRadius: 10 },
    Segmented: { borderRadius: 10 },
  },
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <ConfigProvider locale={zhCN} theme={theme}>
        <App />
      </ConfigProvider>
    </ErrorBoundary>
  </React.StrictMode>
);