# Instalación de Python
``https://www.python.org/downloads/``

## Instalar virtualenv
``pip install virtualenv``

## Crear entorno virtual
``virtualenv -p python3 env``

## Activar entorno virtual
``.\env\Scripts\activate``

## Instalar dependencias
``pip install -r requirements.txt``

## Ejecutar el proyecto
1. Asegúrate de que el entorno virtual esté activado.
2. Ejecuta el script principal del proyecto:
   ```
   python main.py
   ```

## Estructura del proyecto
```
c:\dev\py\
│
├── README.md          # Documentación del proyecto
├── requirements.txt   # Dependencias del proyecto
├── env\               # Entorno virtual
├── main.py            # Archivo principal del proyecto
└── tests\             # Carpeta con pruebas unitarias
```