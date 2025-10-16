Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
winget install Python.PythonInstallManager
timeout /t 5
py install 3.10
timeout /t 5
py -3.10 -m venv venv310
timeout /t 5
.\venv310\Scripts\activate
timeout /t 5
pip install mediapipe opencv-python pygame
