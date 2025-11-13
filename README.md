# TP-Expo
Jueguito para la expo de la Indu 4  
## ¿Cómo usar?
*(Ejecutar estos comandos uno por uno, esperando a que acabe el primero para ejecutar el siguiente)*
### Al abrir el proyecto
Una vez configurado (ver abajo), siempre ejecutar este comando al abrir una terminal antes de intentar abir el juego
(asegurate que la carperta que se señala en terminal es la misma que la del trabajo):\
``.\venv310\Scripts\activate``\
Para abrir el juego:\
``python game.py``\  
### Configurar todo por primera vez
Instalar Python (tendras que hacerlo con este método) y crear el entorno virtual:\
``Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser``\
``winget install Python.PythonInstallManager``\

Espera un rato, puede que tarde en terminar de instalarse aunque parezca que ya ha acabado. Después ejecuta:\
``pymanager install 3.10``\

Asegurate que la carperta que se señala en terminal es la misma que la del trabajo:\
``py -3.10 -m venv venv310``\
``.\venv310\Scripts\activate``\
``pip install mediapipe opencv-python``\
``pip install pygame``