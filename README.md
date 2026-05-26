# IS2-2026-1
Proyecto semestral del curso Ingeniería de Software II

# Estructura
```text
IS2-2026-1/
│
├── app/                        # Paquete principal de la aplicación Flask
│   ├── auth/                   # Módulo de autenticación (Inicio de sesión)
│   │   └── routes.py           # Rutas y lógica para el inicio de sesión
│   │
│   ├── static/                 # Archivos estáticos globales del frontend
│   │   ├── css/                # CSS extra (adicionales a Bootstrap, opcional)
│   │   └── js/                 # Scripts interactivos de JavaScript (opcional)
│   │
│   ├── templates/              # Vistas HTML con Jinja2 y Bootstrap 5
│   │   ├── base.html           # Estructura base global (aquí se importa Bootstrap)
│   │   └── signin.html         # Pantalla de login (Hereda de base.html)
│   │
│   ├── users                   # Contendrá rutas para cada tipo de usuario (Reportador, Coordinador, etc.)
│   │   └── reportador/         
│   │
│   ├── __init__.py             # Inicialización de app Flask y SQLAlchemy
│   └── db_model.py             # Definición de las clases/tablas (Estudiante, Caso, Patrón)
│
├── database/                   # Respaldos SQL (o quizás mover models.py acá)
├── .gitignore                  
├── README.md                   
├── requirements.txt            # Lista de dependencias
└── run.py                      # Script principal para arrancar el servidor local
```
# Ejecución de aplicación Flask

#### 1. **CREAR ENTORNO VIRTUAL**
```
python -m venv <nombre de carpeta, e.j. '.venv'>
```
#### 2. Activar entorno virtual
En command line de Windows:
```
.venv\Scripts\activate
```
Bash:
```
source venv/bin/activate
```
#### 3. Instalar dependencias (revisar que pip esté actualizado)
```
pip install -r requirements.txt
```
#### 4. Población de base de datos para testing
En caso de ser necesario, ejecutar el script de población con datos dummy.
```
python scripts/seed_db.py
```
#### 5. Iniciar aplicación de Flask
```
flask run --debug
```
#### 6. Salida del entorno virtual
Windows:
```
.venv\Scripts\deactivate
```
Bash:
```
deactivate
```
