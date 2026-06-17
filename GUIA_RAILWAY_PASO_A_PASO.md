# 📖 Guía Paso a Paso: Desplegar CreditApi en Railway

## 🎯 Objetivo Final
Tener tu aplicación Django corriendo en `https://tu-app.railway.app`

---

## ⚡ Requisitos Previos
- [ ] Cuenta en GitHub con el repositorio
- [ ] Cuenta en [Railway.app](https://railway.app) (gratis)
- [ ] Git instalado localmente

---

## 📋 PASO 1: Preparar el Repositorio Local

### 1.1 Actualizar el repositorio con los nuevos archivos
```bash
cd c:\Users\DELL\Documents\CreditApi\CreditApi\CreditMovilApp

# Verificar que estos archivos existen:
# - requirements.txt
# - Procfile
# - .env (local)
# - .env.example

# Agregar cambios a Git
git add .
git commit -m "feat: agregar configuración para producción en Railway"
git push origin main  # o la rama que uses
```

---

## 🚂 PASO 2: Conectar Railway con GitHub

### 2.1 Ir a Railway.app
1. Abre https://railway.app
2. Haz clic en **"Start a New Project"**

### 2.2 Conectar GitHub
1. Haz clic en **"Deploy from GitHub"**
2. Autoriza Railway a acceder a tu GitHub
3. Selecciona el repositorio: `CreditApi`
4. Selecciona la rama: `main` (o la rama que uses)

---

## 🗄️ PASO 3: Agregar Base de Datos PostgreSQL

### 3.1 Agregar PostgreSQL
1. En el dashboard de Railway, haz clic en **"Create"** o **"+"**
2. Busca **"PostgreSQL"**
3. Haz clic en **"Add"**

**Railway generará automáticamente** las variables de conexión (DATABASE_URL)

---

## 🔐 PASO 4: Configurar Variables de Entorno

### 4.1 Abrir configuración de variables
1. En Railway, ve al tab **"Variables"**
2. Haz clic en **"Add Variable"** o el icono de edición

### 4.2 Copiar y Pegar Variables
Usa el contenido de `ENV_VARIABLES_RAILWAY.md`:

Copia línea por línea y reemplaza:

```
DEBUG=False
SECRET_KEY=<Tu nueva clave segura>
ALLOWED_HOSTS=<tu-app-name>.railway.app
CORS_ALLOWED_ORIGINS=https://tu-dominio-frontend.com
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

### 4.3 Generar SECRET_KEY Segura

**Opción A: Localmente**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Opción B: En línea**
Usa: https://djecrety.ir/

---

## 🚀 PASO 5: Desplegar Automáticamente

### 5.1 Railway Despliega Automáticamente
1. Una vez agregadas las variables de entorno
2. Railway detectará cambios en tu repositorio
3. Iniciará automáticamente el deploy

**Espera a que termine** (verás un checkmark verde ✅)

### 5.2 Monitorear el Deploy
1. Ve al tab **"Deployments"**
2. Verás un log en tiempo real
3. Busca mensajes como:
   - `Running release command: python manage.py migrate`
   - `Deployment successful`

---

## 🧪 PASO 6: Verificar que Funciona

### 6.1 Encontrar tu URL
1. En Railway, ve al tab **"Domains"**
2. Copia la URL generada (ej: `https://creditapi-prod.railway.app`)

### 6.2 Probar la Aplicación
1. Abre en el navegador: `https://tu-url.railway.app/admin`
2. Deberías ver el login de Django admin
3. **Usuario**: `admin`
4. **Contraseña**: Depende de tu configuración (ver Paso 7)

---

## 👤 PASO 7: Crear Superusuario (Opcional)

### 7.1 Opción A: Desde Railway Shell
```bash
# En Railway, abre el terminal
python manage.py createsuperuser
# Sigue las instrucciones
```

### 7.2 Opción B: Script Automático
Ya existe un script `init_db.sh` que lo hace automáticamente

---

## 🌐 PASO 8: Configurar Dominio Personalizado (Opcional)

### 8.1 Si tienes un dominio
1. En Railway, ve a **"Domains"**
2. Haz clic en **"Add Custom Domain"**
3. Ingresa tu dominio (ej: `api.tudominio.com`)
4. Sigue las instrucciones de DNS

---

## ✅ Checklist de Verificación

Después de desplegar:

- [ ] Aplicación en línea en `https://tu-app.railway.app`
- [ ] Acceso a `/admin` funciona
- [ ] Base de datos migrada correctamente
- [ ] Variables de entorno configuradas
- [ ] SSL/HTTPS funcionando
- [ ] CORS permitiendo tu frontend

---

## 🐛 Solución de Problemas

### Problema: Deploy falla con "Module not found"
**Solución:**
```bash
# Verifica que requirements.txt esté en la raíz
git add requirements.txt
git commit -m "add requirements.txt"
git push
```

### Problema: "ALLOWED_HOSTS invalid"
**Solución:**
Verifica que `ALLOWED_HOSTS` coincida exactamente con tu URL de Railway

### Problema: Database connection failed
**Solución:**
1. Verifica que PostgreSQL esté creado en Railway
2. Verifica que `USE_POSTGRES=1`
3. Re-despliega

### Problema: Static files no se cargan
**Solución:**
El Procfile tiene:
```
release: python manage.py migrate
```
Que ejecuta `collectstatic` automáticamente

### Ver logs en tiempo real
En Railway → Deployments → Logs

---

## 📞 Información Adicional

- **Railway Docs**: https://docs.railway.app
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **PostgreSQL en Railway**: https://docs.railway.app/databases/postgresql

---

## 🎉 ¡Listo!

Tu aplicación está desplegada en Railway. 

**Próximos pasos:**
1. Configura tu dominio personalizado
2. Establece un CD/CI pipeline (optional)
3. Configura alertas de error
4. Monitorea el rendimiento

**¡Felicidades! 🚀**
