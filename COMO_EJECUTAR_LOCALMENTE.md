# ⚙️ Cómo Ejecutar el Proyecto Localmente

## 🏠 Configuración Local (Desarrollo)

### Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes)
- Git
- (Opcional) PostgreSQL para desarrollo

---

## 🚀 Pasos para Ejecutar Localmente

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/CreditApi.git
cd CreditApi/CreditMovilApp
```

### 2. Crear Entorno Virtual
```bash
# Windows
python -m venv env_stable

# macOS/Linux
python3 -m venv env_stable
```

### 3. Activar Entorno Virtual
```bash
# Windows
env_stable\Scripts\activate

# macOS/Linux
source env_stable/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Variables de Entorno (Si necesitas)
```bash
# El archivo .env ya está pre-configurado para desarrollo
# Si quieres verificar/cambiar:
cat .env

# Las variables importantes para desarrollo:
# DEBUG=True
# USE_POSTGRES=0  (usa SQLite por defecto)
```

### 6. Ejecutar Migraciones
```bash
python manage.py migrate
```

### 7. Crear Superusuario (Admin)
```bash
python manage.py createsuperuser
# Sigue las instrucciones en pantalla
```

### 8. Ejecutar el Servidor
```bash
python manage.py runserver
```

**Output esperado:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## 🌐 Acceder a la Aplicación

- **API**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
  - Usuario: `admin`
  - Contraseña: (la que creaste)

---

## 🧪 Ejecutar Pruebas

### Pruebas Unitarias
```bash
# Todas las pruebas
pytest

# Pruebas específicas
pytest validacion/tests/

# Con cobertura
pytest --cov=validacion
```

### Pruebas de API
```bash
pytest validacion/test/test_api.py
```

### Pruebas JavaScript (Jest)
```bash
# Primero instala dependencias npm
npm install

# Ejecuta pruebas
npm test
```

---

## 🔧 Comandos Django Útiles

### Crear Nueva App
```bash
python manage.py startapp nombre_app
```

### Crear Migraciones
```bash
python manage.py makemigrations
```

### Aplicar Migraciones
```bash
python manage.py migrate
```

### Ver Base de Datos (SQLite)
```bash
# El archivo se encuentra en:
# CreditMovilApp/db.sqlite3

# Puedes abrirlo con SQLite Browser
```

### Limpiar Cache
```bash
python manage.py clear_cache
```

### Recolectar Archivos Estáticos
```bash
python manage.py collectstatic
```

---

## 📊 Configuración PostgreSQL Local (Opcional)

Si quieres usar PostgreSQL en desarrollo:

### 1. Instalar PostgreSQL
- Windows: https://www.postgresql.org/download/windows/
- macOS: `brew install postgresql`
- Linux: `sudo apt-get install postgresql`

### 2. Crear Base de Datos
```bash
createdb crediticia_db
```

### 3. Actualizar .env
```env
USE_POSTGRES=1
POSTGRES_DB=crediticia_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_contraseña
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 4. Instalar Driver PostgreSQL
```bash
pip install psycopg2-binary
```

### 5. Ejecutar Migraciones
```bash
python manage.py migrate
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'django'"
**Solución:**
```bash
# Verifica que el entorno virtual esté activado
# y reinstala dependencias
pip install -r requirements.txt
```

### Error: "Database connection refused"
**Solución:**
```bash
# Si usas PostgreSQL, verifica que esté corriendo:
# Windows: Busca "Services" > PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### Error: "Port 8000 already in use"
**Solución:**
```bash
# Usar puerto diferente
python manage.py runserver 8001
```

### Error: "Static files not found"
**Solución:**
```bash
python manage.py collectstatic --noinput
```

### Limpiar Base de Datos (Cuidado)
```bash
# Eliminar todas las migraciones excepto __init__.py
# y la base de datos
rm db.sqlite3
python manage.py migrate
```

---

## 📋 Estructura de Carpetas del Proyecto

```
CreditMovilApp/
├── crediticia/           # Configuración principal Django
│   ├── settings.py       # Configuraciones (variables de entorno)
│   ├── urls.py          # URLs principales
│   ├── wsgi.py          # WSGI para producción
│   └── asgi.py          # ASGI para WebSockets
│
├── validacion/          # App principal
│   ├── models.py        # Modelos de datos
│   ├── views.py         # Vistas/Endpoints API
│   ├── serializers.py   # Serializadores DRF
│   ├── permissions.py   # Permisos personalizados
│   ├── tests.py         # Pruebas
│   ├── admin.py         # Configuración admin
│   └── migrations/      # Migraciones de base de datos
│
├── .env                 # Variables locales (desarrollo)
├── .env.example         # Plantilla variables
├── manage.py            # Comando principal Django
├── requirements.txt     # Dependencias Python
└── db.sqlite3          # Base de datos local (desarrollo)
```

---

## 🔌 Variables de Entorno para Desarrollo

```env
# Debug activado
DEBUG=True

# Base de datos local (SQLite)
USE_POSTGRES=0

# Configuración CORS flexible para desarrollo
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Seguridad desactivada para desarrollo
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Zona horaria
LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
```

---

## 🎯 Workflow Típico de Desarrollo

1. **Crear rama feature**
   ```bash
   git checkout -b feature/mi-feature
   ```

2. **Hacer cambios y pruebas**
   ```bash
   # Editar modelos/vistas/etc
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

3. **Ejecutar pruebas**
   ```bash
   pytest
   ```

4. **Commit y push**
   ```bash
   git add .
   git commit -m "feat: descripción cambios"
   git push origin feature/mi-feature
   ```

5. **Crear Pull Request** en GitHub

---

## 📱 Testear API con Postman/Insomnia

### 1. Login (Obtener token)
```
POST http://localhost:8000/api/token/
{
  "username": "admin",
  "password": "admin123"
}
```

### 2. Usar token en requests
```
Headers:
Authorization: Bearer <token_aqui>
```

---

## 🚦 Estados y Logs

### Ver logs en tiempo real
```bash
# Django muestra logs en la terminal donde ejecutaste runserver
# Busca mensajes tipo:
# [26/Jun/2024 10:30:45] "GET /api/validacion/ HTTP/1.1" 200 1234
```

### Habilitar logs detallados
En `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 💾 Backup y Exportar Datos

### Exportar datos
```bash
python manage.py dumpdata > datos_backup.json
```

### Importar datos
```bash
python manage.py loaddata datos_backup.json
```

---

## 🎉 ¡Listo para Desarrollar!

Tienes todo configurado para:
- ✅ Desarrollar localmente
- ✅ Ejecutar pruebas
- ✅ Desplegar en Railway
- ✅ Mantener variables de entorno seguras

**¿Necesitas más ayuda?** Revisa `RAILWAY_DEPLOYMENT.md` para producción.
