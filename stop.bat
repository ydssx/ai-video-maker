@echo off
echo === 停止 AI 短视频制作平台服务 ===
echo.

REM 停止 Node.js 进程（前端）
echo 停止前端服务...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 前端服务已停止
) else (
    echo ⚠ 没有找到运行中的前端服务
)

REM 停止 Python uvicorn 进程（后端）
echo 停止后端服务...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo table /nh ^| findstr uvicorn') do (
    taskkill /f /pid %%i >nul 2>&1
)

REM 也尝试停止所有 Python 进程（谨慎使用）
REM taskkill /f /im python.exe >nul 2>&1

echo ✓ 后端服务已停止

echo.
echo 🛑 所有服务已停止
echo.
pause