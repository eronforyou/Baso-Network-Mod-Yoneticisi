@echo off
setlocal enabledelayedexpansion

:: -------------------------
:: Versiyon ve GitHub linkleri
:: -------------------------
set "VERSION=1.0.0"
set "VERSION_URL=https://raw.githubusercontent.com/eronforyou/Baso-Network-Mod-Yoneticisi/main/version.txt"
set "SCRIPT_URL=https://raw.githubusercontent.com/eronforyou/Baso-Network-Mod-Yoneticisi/main/script.bat"
set "SCRIPT_NAME=%~nx0"
:: -------------------------

:: --- Güncelleme kontrolü ---
echo Mevcut surum: %VERSION%
echo Sunucudan en son surum kontrol ediliyor...

curl -s -o latest_version.txt %VERSION_URL%
if exist latest_version.txt (
    set /p LATEST=<latest_version.txt
    del /q latest_version.txt
    if not "%VERSION%"=="%LATEST%" (
        echo Yeni surum bulundu! [%LATEST%]
        echo Script indiriliyor...
        curl -s -o "%SCRIPT_NAME%.new" %SCRIPT_URL%
        if exist "%SCRIPT_NAME%.new" (
            move /y "%SCRIPT_NAME%.new" "%SCRIPT_NAME%" >nul
            echo Script guncellendi. Yeniden baslatiliyor...
            start "" "%SCRIPT_NAME%"
            exit
        ) else (
            echo [HATA] Script indirilemedi!
        )
    ) else (
        echo Script zaten guncel.
    )
) else (
    echo [HATA] Surum kontrol dosyasi indirilemedi!
)

:: -------------------------
:: Mod yoneticisi ayarlari
:: -------------------------
set "jsonfile=C:\xampp\htdocs\files"
set "moddir=C:\Users\enesb\AppData\Roaming\.basonw\mods"

:menu
cls
echo 1. Mod Ekle
echo 2. Mod Sil
echo 3. Modlari Listele
echo 4. Cikis
set /p choice=Seciminiz: 

if "%choice%"=="1" goto ekle
if "%choice%"=="2" goto sil
if "%choice%"=="3" goto listele
if "%choice%"=="4" exit
goto menu

:ekle
echo Lutfen eklenecek dosyayi secin...
for /f "usebackq delims=" %%I in (
    `powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms | Out-Null; $f = New-Object Windows.Forms.OpenFileDialog; $f.InitialDirectory = [Environment]::GetFolderPath('Desktop'); $f.Filter = 'Tüm Dosyalar (*.*)|*.*'; if($f.ShowDialog() -eq 'OK'){Write-Output $f.FileName}"`
) do (
    set "file=%%I"
)

if "%file%"=="" (
    echo Dosya secilmedi.
    pause
    goto menu
)

for %%A in ("%file%") do set "filename=%%~nxA"
set "target=%moddir%\%filename%"
mkdir "%moddir%" >nul 2>&1
copy /y "%file%" "%target%" >nul

for %%A in ("%target%") do set "filesize=%%~zA"

:: SHA1 her defasında sıfırlansın
set "sha1="
for /f "skip=1 tokens=1" %%A in ('certutil -hashfile "%target%" SHA1') do if not defined sha1 set "sha1=%%A"

set "tempfile=%temp%\files_temp.json"
set "inserted="

(for /f "usebackq delims=" %%L in ("%jsonfile%") do (
    set "line=%%L"
    setlocal enabledelayedexpansion

    :: JSON sonundan bir önceki yere ekle
    if "!line!"=="]" (
        if not defined inserted (
            echo ,>>"%tempfile%"
            echo {>>"%tempfile%"
            echo "name": "%filename%",>>"%tempfile%"
            echo "size": %filesize%,>>"%tempfile%"
            echo "sha1": "%sha1%",>>"%tempfile%"
            echo "download_link": "/download/mods/%filename%",>>"%tempfile%"
            echo "path": "mods/%filename%">>"%tempfile%"
            echo }>>"%tempfile%"
            set "inserted=1"
        )
        echo ]>>"%tempfile%"
    ) else (
        echo !line!>>"%tempfile%"
    )
    endlocal
))
move /y "%tempfile%" "%jsonfile%" >nul

echo Mod eklendi: %filename%
pause
goto menu

:sil
cls
echo Silinecek mod secin:
set /a count=0
for %%A in ("%moddir%\*") do (
    set /a count+=1
    set "mod[!count!]=%%~nxA"
    echo !count!. %%~nxA
)

if %count%==0 (
    echo Hic mod bulunamadi.
    pause
    goto menu
)

set /p modchoice=Numara girin: 
if "%modchoice%"=="" goto menu

set "modname=!mod[%modchoice%]!"
if "!modname!"=="" (
    echo Gecersiz secim.
    pause
    goto menu
)

del "%moddir%\!modname!" >nul 2>&1

set "tempfile=%temp%\files_temp.json"
set "prevline="
set "skipblock="

(for /f "usebackq delims=" %%L in ("%jsonfile%") do (
    set "line=%%L"

    if defined skipblock (
        echo %%L | findstr /c:"}" >nul
        if not errorlevel 1 set "skipblock="
    ) else (
        echo %%L | findstr /c:"\"!modname!\"" >nul
        if not errorlevel 1 (
            set "skipblock=1"
            :: Önceki satır "}," ise son blok olabilir, onu düzelt
            echo !prevline! | findstr /c:"}," >nul
            if not errorlevel 1 set "prevline=!prevline:},=}!"
        ) else (
            if defined prevline echo !prevline!>>"%tempfile%"
            set "prevline=!line!"
        )
    )
))
if defined prevline echo !prevline!>>"%tempfile%"

move /y "%tempfile%" "%jsonfile%" >nul

echo Mod silindi: !modname!
pause
goto menu

:listele
cls
echo Mods klasorundeki modlar:
echo.
set /a count=0
for %%A in ("%moddir%\*") do (
    set /a count+=1
    echo %%~nxA
    echo.
)
if %count%==0 echo Hic mod bulunamadi.
pause
goto menu
