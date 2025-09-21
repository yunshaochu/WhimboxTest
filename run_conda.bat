@echo off
setlocal EnableExtensions
pushd "%~dp0"

REM =====================================================
REM  run.bat  —— 使用当前目录下的 Conda 环境运行脚本
REM  环境目录：%CD%\conda_env  （可改 ENV_DIR）
REM  入口脚本：whimbox.py      （可改 ENTRY）
REM  说明：报错不退出，最后统一 pause
REM =====================================================

REM ---- 可按需修改的参数 ----
set "ENV_DIR=conda_env"
set "ENTRY=whimbox.py"

REM ---- 控制台编码（可注释） ----
chcp 65001 >nul

set "ENV_PREFIX=%CD%\%ENV_DIR%"
set "CONDA_EXE="

echo(
echo ============================================
echo  [运行] %ENTRY%  （Conda 环境内）
echo  环境路径：%ENV_PREFIX%
echo ============================================
echo(

REM ---- 查找 conda.exe（避免用 conda.bat 触发递归）----
for /f "delims=" %%I in ('where conda.exe 2^>nul') do (
  if not defined CONDA_EXE set "CONDA_EXE=%%~fI"
)

if not defined CONDA_EXE (
  echo [错误] 未找到 conda.exe
  echo   解决：确保 Miniconda/Anaconda 已安装且 conda.exe 在 PATH 中
  echo   示例：%%USERPROFILE%%\miniconda3\condabin\conda.exe
  goto :END
)

REM ---- 检查环境是否存在 ----
if not exist "%ENV_PREFIX%\python.exe" (
  echo [错误] 未发现环境：%ENV_PREFIX%
  echo   请先运行 setup_env_conda.bat 创建环境。
  goto :END
)

REM ---- 检查入口脚本是否存在 ----
if not exist "%ENTRY%" (
  echo [错误] 未找到入口脚本：%ENTRY%
  echo   请确认脚本文件名或修改本批处理中的 ENTRY 变量。
  goto :END
)

REM ---- 运行（把命令行参数 %* 透传给 Python 脚本）----
echo --------------------------------------------
echo  使用：%CONDA_EXE%
echo  命令：conda run -p "%ENV_PREFIX%" python "%ENTRY%" %*
echo --------------------------------------------
"%CONDA_EXE%" run -p "%ENV_PREFIX%" python "%ENTRY%" %*
set "EXITCODE=%ERRORLEVEL%"

echo(
if %EXITCODE% NEQ 0 (
  echo [错误] %ENTRY% 退出码：%EXITCODE%
) else (
  echo [完成] %ENTRY% 执行成功（退出码 0）
)

:END
echo(
echo ============================================
echo  脚本执行结束，按任意键关闭窗口...
echo ============================================
echo(
pause

popd
endlocal
