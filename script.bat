@echo off
setlocal enabledelayedexpansion

:: -------------------------
:: Ayarlar
:: -------------------------
set "VERSION=1.0.0"
set "REPO_RAW=https://raw.githubusercontent.com/KULLANICI_ADI/REPO_ADI/main"
set "VERSION_URL=%REPO_RAW%/version.txt"
set "SCRIPT_URL=%REPO_RAW%/script.bat"
set "SCRIPT_NAME=script.bat"
:: -------------------------

echo Mevcut surum: %VERSION%
echo Sunucudan en son surum kontrol ediliyor...

:: GitHub'dan version.txt indir
curl -s -o latest_version.txt %VERSION_URL%
if not exist latest_version.txt (
    echo [HATA] Surum kontrol dosyasi indirilemedi!
    goto :continue
)

set /p LATEST=<latest_version.txt
del /q latest_version.txt

echo En son surum: %LATEST%

:: Versiyon karsilastirma
if "%VERSION%"=="%LATEST%" (
    echo Bu script zaten guncel.
    goto :continue
) else (
    echo Yeni surum bulundu! [%LATEST%]
    echo Script indiriliyor...
    curl -s -o "%SCRIPT_NAME%.new" %SCRIPT_URL%
    if exist "%SCRIPT_NAME%.new" (
        echo Guncelleme tamamlandi.
        move /y "%SCRIPT_NAME%.new" "%SCRIPT_NAME%" >nul
        echo Script yeniden baslatiliyor...
        start "" "%SCRIPT_NAME%"
        exit
    ) else (
        echo [HATA] Script indirilemedi!
    )
)

:continue
echo Devam ediliyor...
:: Buraya esas batch kodlarini yazabilirsin

pause
