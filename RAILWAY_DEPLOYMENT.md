# Variables de Entorno para Railway - CreditApi

## 📋 Guía de Configuración en Railway

### 1. Variables Requeridas Básicas

```
DEBUG=False
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria-aqui
ALLOWED_HOSTS=tu-dominio.railway.app,www.tu-dominio.railway.app
```

### 2. Base de Datos PostgreSQL

Railway proporcionará automáticamente una URL de base de datos. Si lo deseas, puedes usar:

```
USE_POSTGRES=1
POSTGRES_DB=crediticia_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu-contraseña-segura
POSTGRES_HOST=tu-railway-db-host.railway.internal
POSTGRES_PORT=5432
```

**O mejor aún, Railway proporciona**: `DATABASE_URL` (úsala si está disponible)

### 3. CORS Configuration

```
CORS_ALLOWED_ORIGINS=https://tu-frontend-domain.com,https://www.tu-frontend-domain.com
```

### 4. JWT Configuration

```
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
```

### 5. Security Settings

```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_SECURITY_POLICY=True
```

### 6. Email Configuration (Opcional)

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-app-gmail
DEFAULT_FROM_EMAIL=noreply@creditapi.com
```

### 7. Localización

```
LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
```

---

## 🚀 Pasos para Desplegar en Railway

### Paso 1: Conectar Repositorio
1. Ve a [railway.app](https://railway.app)
2. Crea un nuevo proyecto
3. Conecta tu repositorio de GitHub

### Paso 2: Agregar Base de Datos PostgreSQL
1. En Railway, haz clic en "+ Create"
2. Selecciona "PostgreSQL"
3. Railway generará automáticamente `DATABASE_URL`

### Paso 3: Configurar Variables de Entorno
En el panel de Railway, ve a "Variables" y agrega:

#### Copiar y Pegar (Reemplazar valores):
```
DEBUG=False
SECRET_KEY=generate-secure-key-here-make-it-long-random
ALLOWED_HOSTS=your-app-name.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Paso 4: Configurar Build & Deploy
Railway detectará automáticamente:
- **Procfile** - Define el comando web y release
- **requirements.txt** - Instala las dependencias

### Paso 5: Ejecutar Migraciones
1. En Railway, ve a "Deployments"
2. Railway ejecutará automáticamente el comando `release` en Procfile:
   ```
   release: python manage.py migrate
   ```

### Paso 6: Verificar Despliegue
- Ve a la URL proporcionada por Railway
- Accede a `/admin` para verificar que todo funciona

---

## 🔐 Cómo Generar un SECRET_KEY Seguro

### Opción 1: Desde Python
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Opción 2: Desde Terminal
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Opción 3: Sitio en línea
Usar https://djecrety.ir/ (generador de claves Django)

---

## 🛠️ Solución de Problemas

### Error: "Module not found"
- Verifica que `requirements.txt` esté en la raíz del proyecto
- Railway ejecutará `pip install -r requirements.txt` automáticamente

### Error: "Database connection refused"
- Verifica que `USE_POSTGRES=1` esté configurado
- Asegúrate de que PostgreSQL está habilitado en Railway

### Error: "CORS policy"
- Verifica que `CORS_ALLOWED_ORIGINS` incluya tu dominio frontend
- No incluyas `http://` en producción, solo `https://`

### Error: "Static files not found"
- La migración `collectstatic` se ejecuta en el comando `release`
- Verifica el Procfile

---

## 📚 Archivos Creados/Modificados

- ✅ `settings.py` - Configurado para usar variables de entorno
- ✅ `.env` - Template con valores por defecto (desarrollo)
- ✅ `.env.example` - Plantilla para referencia
- ✅ `requirements.txt` - Todas las dependencias necesarias
- ✅ `Procfile` - Configuración para Railway
- ✅ `init_db.sh` - Script de inicialización (opcional)

---

## 📞 Variables de Entorno Railway (Completa)

Usa esta tabla como checklist:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `DEBUG` | `False` | Desactiva debug en producción |
| `SECRET_KEY` | `<generated>` | Clave segura (genera una nueva) |
| `ALLOWED_HOSTS` | `app.railway.app` | Dominio de tu app |
| `USE_POSTGRES` | `1` | Usa PostgreSQL |
| `POSTGRES_DB` | `crediticia_db` | Nombre de la BD |
| `POSTGRES_USER` | `postgres` | Usuario de BD |
| `POSTGRES_PASSWORD` | `<secure>` | Contraseña de BD |
| `POSTGRES_HOST` | Auto (Railway) | Host de la BD |
| `POSTGRES_PORT` | `5432` | Puerto de la BD |
| `CORS_ALLOWED_ORIGINS` | `https://tu-dominio.com` | Orígenes CORS permitidos |
| `SECURE_SSL_REDIRECT` | `True` | Redirige HTTP a HTTPS |
| `SESSION_COOKIE_SECURE` | `True` | Cookies solo HTTPS |
| `CSRF_COOKIE_SECURE` | `True` | CSRF solo HTTPS |
| `LANGUAGE_CODE` | `es-es` | Idioma |
| `TIME_ZONE` | `America/Bogota` | Zona horaria |

---

**¡Tu app está lista para desplegarse en Railway! 🚀**
