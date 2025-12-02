# Install Python dependencies
Write-Host "Installing Python dependencies..."
cd backend
.\mlstateofartenv\Scripts\Activate.ps1
pip install -r requirements.txt

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..."
cd ..\frontend
npm install

# Start servers
Write-Host "Starting servers..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\mlstateofartenv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"