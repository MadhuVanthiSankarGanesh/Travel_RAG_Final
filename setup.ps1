# Create Python virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Green
python -m venv api/venv
. api/venv/Scripts/Activate

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install -r api/requirements.txt

# Create client directory and install Node dependencies
Write-Host "Setting up React client..." -ForegroundColor Green
Set-Location client
npm install

# Return to root directory
Set-Location ..

Write-Host "Setup complete!" -ForegroundColor Green
Write-Host @"

To start the application:

1. Start Ollama with Mistral:
   ollama run mistral

2. Start the backend server:
   cd api
   uvicorn app.main:app --reload

3. Start the frontend (in a new terminal):
   cd client
   npm start

The application will be available at http://localhost:3000
"@ -ForegroundColor Cyan 