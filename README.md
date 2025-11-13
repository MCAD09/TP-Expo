# TP-Expo
Jueguito para la expo de la Indu 4.
## ¿Cómo usar?
*(Ejecutar estos comandos **UNO POR UNO**, esperando a que acabe el primero para ejecutar el siguiente)*
### Al abrir el proyecto
Una vez configurado ([ver abajo](https://github.com/MCAD09/TP-Expo/edit/main/README.md#configurar-todo-por-primera-vez)), recordar siempre ejecutar este comando al abrir una terminal e intentar ejecutar el juego
(asegurate que la carperta que se señala en la terminal es la misma que la del proyecto):
```
.\venv310\Scripts\activate
```
Para abrir el juego:
```
python game.py
```


### Configurar todo por primera vez
Instalar Python (tendras que hacerlo con este método) y crear el entorno virtual:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
```
winget install Python.PythonInstallManager
```

Espera un rato, puede que tarde en terminar de instalarse aunque parezca que ya ha acabado. Después ejecuta:
```
pymanager install 3.10
```

Clona el proyecto:
```
git clone https://github.com/MCAD09/TP-Expo.git
```
Ingresa a la carpeta que lo contiene y ejecuta lo siguinte:
```
py -3.10 -m venv venv310
``` 
```
.\venv310\Scripts\activate
``` 
```
pip install mediapipe opencv-python
``` 
```
pip install pygame-ce #Si, se debe instalar por separado
```

(Este proyecto requiere de Python 3.10, lo cual se puede hacer facilmente desde Pymanager)
