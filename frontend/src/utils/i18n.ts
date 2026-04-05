import zhCN from '../locales/zh-CN.json';

const messages = {
  'zh-CN': zhCN
};

// 极简 t() 实现：后续可替换为 i18next 等
export function t(key: string, fallback?: string): string {
  const locale = 'zh-CN';
  const dict = messages[locale] as Record<string, string>;
  return dict[key] || fallback || key;
}

export default t;

