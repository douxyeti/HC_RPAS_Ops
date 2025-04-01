@echo off
:: Vérifie si le script est exécuté en tant qu'administrateur
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Exécution avec privilèges administrateur...
) else (
    echo Demande des privilèges administrateur...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: Change le répertoire courant vers celui du script
cd /d "%~dp0"

:: Installation du service
echo Installation du service de sauvegarde...
python install_service.py install

:: Démarrage du service
echo Démarrage du service...
python install_service.py start

echo.
echo Installation terminée. Appuyez sur une touche pour fermer.
pause >nul
