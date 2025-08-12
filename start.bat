@echo off
echo === AI 短视频制作平台启动器 ===
echo.

REM 检查 Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Node.js 未安装，请先安装 Node.js
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python 未安装，请先安装 Python
    pause
    exit /b 1
)

echo ✓ 环境检查通过

REM 创建环境变量文件（如果不存在）
if not exist "backend\.env" (
    echo 创建环境变量文件...
    echo OPENAI_API_KEY=your_openai_api_key_here > backend\.env
    echo UNSPLASH_ACCESS_KEY=your_unsplash_key_here >> backend\.env
    echo ✓ 环境变量文件已创建
)

REM 安装前端依赖（如果需要）
if not exist "frontend\node_modules" (
    echo 安装前端依赖...
    cd frontend
    npm install
    if %errorlevel% neq 0 (
        echo ✗ 前端依赖安装失败
        pause
        exit /b 1
    )
    cd ..
    echo ✓ 前端依赖安装完成
)

echo.
echo 启动服务...

REM 启动后端服务
echo 启动后端服务...
start "AI Video Maker Backend" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端服务
echo 启动前端服务...
start "AI Video Maker Frontend" cmd /k "cd frontend && npm start"

echo.
echo 🎉 服务启动完成！
echo 前端地址: http://localhost:3000
echo 后端 API: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 关闭此窗口不会停止服务
echo 要停止服务，请关闭对应的命令行窗口
echo.
pause