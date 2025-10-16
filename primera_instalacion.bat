Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
winget install Python.PythonInstallManager
py install 3.10
py -3.10 -m venv venv310
pip install mediapipe opencv-python pygame
