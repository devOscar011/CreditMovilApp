# Variables de Entorno para Railway - Formato Copiar y Pegar

## 🔑 VARIABLES LISTAS PARA RAILWAY

Copia estas variables tal cual (reemplaza los valores marcados con `<>`):

```
DEBUG=False
SECRET_KEY=<GENERAR_UNA_NUEVA_CLAVE_MUY_LARGA_Y_ALEATORIA>
ALLOWED_HOSTS=<tu-app>.railway.app,<tu-app>.up.railway.app
CORS_ALLOWED_ORIGINS=https://<tu-dominio-frontend>.com
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
USE_POSTGRES=1
```

---

## 📝 Valores a Reemplazar

### 1. **SECRET_KEY** (CRÍTICO)
Copia el resultado de ejecutar:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
Ejemplo: `django-insecure-9x^!7&mq@8w$#j*k^p%vx&@9$!5^@#j*k&@`

### 2. **ALLOWED_HOSTS**
Reemplaza `<tu-app>` con el nombre de tu app en Railway.
Ejemplo: `creditapi-prod.railway.app`

### 3. **CORS_ALLOWED_ORIGINS**
Reemplaza `<tu-dominio-frontend>` con tu dominio real.
Ejemplos:
- `https://tudominio.com`
- `https://app.tudominio.com`
- Para múltiples: `https://tudominio.com,https://app.tudominio.com`

---

## 🗄️ Base de Datos

**Railway configura esto automáticamente**, pero si necesitas valores específicos:

```
POSTGRES_DB=crediticia_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<GENERAR_CONTRASEÑA_SEGURA>
```

**Mejor opción**: Dejar que Railway gestione `DATABASE_URL` automáticamente.

---

## 📧 Email (Opcional)

### Opción 1: Gmail
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=<contraseña-app-gmail>
DEFAULT_FROM_EMAIL=noreply@creditapi.com
```

### Opción 2: Console (Desarrollo)
```
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## ✅ Checklist Final

Antes de desplegar en Railway:

- [ ] Generar nuevo `SECRET_KEY`
- [ ] Configurar `ALLOWED_HOSTS` con tu dominio
- [ ] Configurar `CORS_ALLOWED_ORIGINS` con frontend
- [ ] Crear base de datos PostgreSQL en Railway
- [ ] Agregar todas las variables de entorno
- [ ] Verificar que `Procfile` existe
- [ ] Verificar que `requirements.txt` existe
- [ ] Conectar repositorio a Railway
- [ ] Esperar a que termine el deploy
- [ ] Probar en `https://tu-app.railway.app/admin`

---

## 🚀 Comando Rápido para Copiar

Para una configuración mínima de desarrollo:

```env
DEBUG=False
SECRET_KEY=<GENERAR_UNA_NUEVA>
ALLOWED_HOSTS=localhost,127.0.0.1,tu-app.railway.app
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://tu-app.railway.app
USE_POSTGRES=1
LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
```

---

## 🔗 Links Útiles

- **Railway**: https://railway.app
- **Generador SECRET_KEY**: https://djecrety.ir/
- **Django Settings**: https://docs.djangoproject.com/en/4.2/ref/settings/
- **CORS Headers**: https://github.com/adamchainz/django-cors-headers

**¡Listo para desplegar! 🎉**
