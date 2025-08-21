import zhCN from '../locales/zh-CN.json';

const messages = {
  'zh-CN': zhCN
};

// 极简 t() 实现：后续可替换为 i18next 等
export function t(key, fallback) {
  const locale = 'zh-CN';
  return messages[locale]?.[key] || fallback || key;
}

export default t;

