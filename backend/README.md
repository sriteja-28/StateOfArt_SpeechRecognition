Backend for speech-app
- run: 

python -m venv mlstateofartenv;
.\mlstateofartenv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


in power shell
----------------
python -m venv mlstateofartenv

.\mlstateofartenv\Scripts\Activate.ps1
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000

