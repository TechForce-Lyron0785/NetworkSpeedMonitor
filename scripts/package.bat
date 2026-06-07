@echo off
echo Creating speedmon.zip release package...

set RELEASE_DIR=release\speedmon
if exist release rmdir /s /q release
mkdir %RELEASE_DIR%

:: Copy EXE
copy dist\speedmon.exe %RELEASE_DIR%\speedmon.exe

:: Copy scripts (nssm already included in EXE as data, but also include separately for installer)
copy scripts\nssm.exe %RELEASE_DIR%\
copy scripts\install.bat %RELEASE_DIR%\
copy scripts\uninstall.bat %RELEASE_DIR%\

:: Copy documentation
copy README.md %RELEASE_DIR%\
copy docs\deploy.md %RELEASE_DIR%\deploy.txt
copy docs\known-issues.md %RELEASE_DIR%\known-issues.txt

:: Create zip
powershell Compress-Archive -Path %RELEASE_DIR%\* -DestinationPath release\speedmon.zip -Force

echo Package created at release\speedmon.zip
pause