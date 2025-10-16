Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
timeout /t 1
winget install Python.PythonInstallManager
timeout /t 3
pymanager install 3.10
timeout /t 3
py -3.10 -m venv venv310
timeout /t 3
.\venv310\Scripts\activate
timeout /t 3
pip install mediapipe opencv-python pygame
