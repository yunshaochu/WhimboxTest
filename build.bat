chcp 65001
@echo off
REM 统一构建脚本 - 将所有构建产物放到 output 目录

echo 清理旧的构建文件...
if exist output rmdir /s /q output
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info

echo.
echo 开始构建...
python -m build --wheel

echo.
echo 整理构建产物到 output 目录...
mkdir output 2>nul

REM 移动 dist 目录
if exist dist (
    move dist output\dist
    echo [√] dist 已移动到 output\dist
)

REM 移动 build 目录
if exist build (
    move build output\build
    echo [√] build 已移动到 output\build
)

REM 移动 egg-info 目录
for /d %%i in (*.egg-info) do (
    move "%%i" "output\%%i"
    echo [√] %%i 已移动到 output\%%i
)

echo.
echo ==========================================
echo 构建完成！
echo ==========================================
echo.
echo 构建产物位置:
if exist output\dist\*.whl (
    echo   wheel: output\dist\*.whl
)
if exist output\dist\*.tar.gz (
    echo   源码包: output\dist\*.tar.gz
)
echo.
pause
