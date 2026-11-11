@echo off
setlocal
echo ========================================================
echo   Starting Scam Call Guard (Gnani AI)
echo ========================================================

if "%GNANI_API_KEY%"=="" (
    if exist .env (
        echo Loading GNANI_API_KEY from .env file...
        for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
            if "%%A"=="GNANI_API_KEY" set GNANI_API_KEY=%%B
        )
    )
)

if "%GNANI_API_KEY%"=="" (
    echo [WARNING] GNANI_API_KEY is not set!
    echo Set it via: set GNANI_API_KEY=your_key_here
    echo Or place it in .env or .streamlit/secrets.toml
    echo.
)

echo Starting Streamlit app...
python -m streamlit run app.py
pause

