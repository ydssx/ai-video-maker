# 测试说明

本目录以 **pytest** 为准。

## 运行

```bash
cd backend
python3 -m pytest ../tests/ -v
```

跳过需要 MySQL 的集成检查：

```bash
SKIP_MYSQL_TESTS=1 python3 -m pytest ../tests/ -v
```

## 当前用例

- `test_foundation.py` — 配置解析、数据库工厂、API 模型导入、健康检查
- 其余历史脚本型文件已移除（导入路径过期、非 pytest 结构）
