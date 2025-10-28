@echo off
echo Setting up RAG Chat Assistant...
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating uploads directory...
if not exist "uploads" mkdir uploads

echo.
echo Setup complete!
echo.
echo IMPORTANT: Before running the application:
echo 1. Get your Anthropic API key from https://console.anthropic.com/
echo 2. Create a .env file with: ANTHROPIC_API_KEY=your_api_key_here
echo 3. Run: python app.py
echo 4. Open http://localhost:5000 in your browser
echo.
pause
