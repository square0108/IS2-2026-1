# IS2-2026-1
Proyecto semestral del curso Ingeniería de Software II

# Estructura del Proyecto
```text
IS2-2026-1/
│
├── app/                        # Paquete principal de la aplicación Flask
│   ├── auth/                   # Módulo de autenticación y seguridad
│   │   ├── routes.py           # Rutas y lógica para el inicio de sesión
│   │   └── login_required.py   # Decorador para protección de rutas por rol
│   │
│   ├── static/                 # Archivos estáticos globales del frontend
│   │   ├── css/                # Hojas de estilo adicionales a Bootstrap
│   │   ├── js/                 # Scripts interactivos (ej. registro_incidentes.js)
│   │   └── images/             # Recursos de imagen (ej. wip.png)
│   │
│   ├── templates/              # Vistas HTML con Jinja2 y Bootstrap 5
│   │   ├── auth/               # Vistas de autenticación (signin.html)
│   │   ├── components/         # Componentes reutilizables (navbar, buscador, etc.)
│   │   └── *.html              # Vistas principales (dashboard, detalles, expedientes)
│   │
│   ├── users/                  # Módulos separados por tipo de usuario
│   │   ├── reportador/         # Rutas específicas del Profesor/Inspector
│   │   └── manager/            # Rutas específicas del Encargado de Convivencia
│   │
│   ├── students/               # Módulo para el manejo general de estudiantes
│   │
│   ├── __init__.py             # Inicialización de app Flask y SQLAlchemy
│   ├── db_model.py             # Definición de los modelos ORM (Usuario, Estudiante, Caso, etc.)
│   └── queries.py              # Lógica de abstracción de consultas a la BD
│
├── instance/                   # Carpeta autogenerada por Flask
│   └── flaskr.sqlite           # Base de datos local SQLite
│
├── scripts/                    # Scripts de utilidad
│   └── seed_db.py              # Script para poblar la base de datos con datos de prueba
│
├── tests/                      # Suite de pruebas automatizadas (pytest)
│   ├── conftest.py             # Configuración global y fixtures (BD en memoria, clientes)
│   └── test_*.py               # Pruebas unitarias y de integración por módulo
│
├── .gitignore                  
├── README.md                   
├── requirements.txt            # Lista de dependencias del proyecto
└── run.py                      # Script principal para arrancar el servidor local

```

# Ejecución de aplicación Flask

#### 1. Crear entorno virtual

```bash
python -m venv venv

```

#### 2. Activar entorno virtual

En línea de comandos de Windows:

```cmd
venv\Scripts\activate

```

En Bash (Linux/Mac):

```bash
source venv/bin/activate

```

#### 3. Instalar dependencias

Asegúrate de tener el entorno activado antes de instalar:

```bash
pip install -r requirements.txt

```

#### 4. Población de base de datos para desarrollo

En caso de ser necesario (o si hay cambios en el esquema), elimina el archivo `instance/flaskr.sqlite` y ejecuta el script de población con datos de prueba:

```bash
python scripts/seed_db.py

```

#### 5. Iniciar aplicación de Flask

```bash
flask run --debug

```

*La aplicación estará disponible por defecto en http://127.0.0.1:5000*

#### 6. Salida del entorno virtual

Windows:

```cmd
venv\Scripts\deactivate

```

Bash:

```bash
deactivate

```

#### 7. Ejecución de pruebas unitarias

El proyecto utiliza **`pytest`** como entorno de pruebas. La suite está configurada para crear una base de datos en memoria (`:memory:`), por lo que ejecutar las pruebas es completamente seguro y **no modificará ni borrará** los datos de tu aplicación en desarrollo (`flaskr.sqlite`).

Ejecutar toda la suite de pruebas:

```bash
pytest tests/

```

Ejecutar un archivo de pruebas específico:

```bash
pytest tests/test_manager.py

```