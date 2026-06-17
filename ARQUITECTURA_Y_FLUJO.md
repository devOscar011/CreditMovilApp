# 🏗️ Arquitectura y Flujo de la Configuración

## 📊 Diagrama General del Proyecto

```
┌─────────────────────────────────────────────────────────┐
│                    CREDITAPI PROJECT                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐         ┌──────────────────┐    │
│  │  DESARROLLO      │         │   PRODUCCIÓN     │    │
│  │  (Local)         │         │   (Railway)      │    │
│  ├──────────────────┤         ├──────────────────┤    │
│  │ DEBUG=True       │    →    │ DEBUG=False      │    │
│  │ SQLite DB        │         │ PostgreSQL DB    │    │
│  │ CORS: *          │         │ CORS: Domain     │    │
│  │ SSL: No          │         │ SSL: Yes (HTTPS) │    │
│  └──────────────────┘         └──────────────────┘    │
│                                                         │
│  Archivo: .env              Archivo: Variables Railway │
│  ↓                          ↓                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │     crediticia/settings.py (USA VAR ENV)        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Configuración

```
1. INICIO
   ↓
2. settings.py carga dotenv si existe
   ↓
3. Lee variables de entorno:
   • SECRET_KEY
   • DEBUG
   • ALLOWED_HOSTS
   • DATABASE (PostgreSQL o SQLite)
   • CORS
   ↓
4. Aplica configuración según ambiente:
   • Si DEBUG=True → Desarrollo (SQLite, sin SSL)
   • Si DEBUG=False → Producción (PostgreSQL, SSL)
   ↓
5. Inicia aplicación con settings cargados
```

---

## 📁 Flujo de Archivos de Configuración

```
┌─────────────────────────────────────────┐
│ Tu Repositorio en GitHub                │
└─────────────────────────────────────────┘
            ↓
            │ git push
            ↓
┌─────────────────────────────────────────┐
│ Railroad.app detecta cambios            │
├─────────────────────────────────────────┤
│ 1. Lee Procfile                         │
│ 2. Lee requirements.txt                 │
│ 3. Instala dependencias: pip install    │
│ 4. Carga variables de entorno           │
│ 5. Ejecuta: release command             │
│    → python manage.py migrate           │
│    → python manage.py collectstatic     │
│ 6. Inicia web server: gunicorn          │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ App Corriendo en:                       │
│ https://tu-app.railway.app              │
└─────────────────────────────────────────┘
```

---

## 🗂️ Estructura de Variables de Entorno

```
Variables de Entorno
├── Django Core
│   ├── DEBUG (True/False)
│   ├── SECRET_KEY (string largo)
│   └── ALLOWED_HOSTS (dominios)
│
├── Database
│   ├── USE_POSTGRES (1/0)
│   ├── POSTGRES_DB
│   ├── POSTGRES_USER
│   ├── POSTGRES_PASSWORD
│   └── POSTGRES_HOST
│
├── Security
│   ├── SECURE_SSL_REDIRECT
│   ├── SESSION_COOKIE_SECURE
│   └── CSRF_COOKIE_SECURE
│
├── CORS
│   └── CORS_ALLOWED_ORIGINS
│
├── JWT
│   ├── ACCESS_TOKEN_LIFETIME
│   └── REFRESH_TOKEN_LIFETIME
│
└── Localización
    ├── LANGUAGE_CODE
    └── TIME_ZONE
```

---

## 🔐 Capas de Seguridad en Producción

```
Usuario (HTTPS)
    ↓ (SSL/TLS Encryption)
    ↓
Load Balancer
    ↓ (SECURE_SSL_REDIRECT = True)
    ↓
Django App (gunicorn)
    ├─ CSRF Protection (CSRF_COOKIE_SECURE)
    ├─ XSS Prevention (XFrameOptions)
    ├─ CORS Whitelist (CORS_ALLOWED_ORIGINS)
    ├─ JWT Tokens (Token BlackListing)
    └─ Secure Cookies (SESSION_COOKIE_SECURE)
    ↓
PostgreSQL Database
    └─ Password Protected
```

---

## 📈 Ciclo de Vida de una Solicitud en Producción

```
1. User Request (HTTPS)
   ↓
2. Railway Load Balancer
   ↓
3. Gunicorn Web Server
   ↓
4. Django App
   a. settings.py carga config desde vars env
   b. Middleware CORS valida origen
   c. Middleware CSRF valida token
   d. JWT Authentication valida token
   e. View procesa request
   f. Database query (PostgreSQL)
   g. Response serializada a JSON
   ↓
5. Response (JSON encriptado HTTPS)
   ↓
6. Browser del usuario
```

---

## 🚦 Estados del Despliegue

```
┌─ Desarrollo (Local) ──┐
│ • DEBUG=True          │
│ • SQLite Database     │
│ • CORS: * (todos)     │
│ • No SSL              │
│ • Hot Reload          │
└───────────────────────┘
         ↓ (git push)
         ↓
┌─ Staging/Testing ─────┐
│ • DEBUG=False         │
│ • PostgreSQL          │
│ • CORS: Específicos   │
│ • SSL: Sí             │
│ • Monitoreo           │
└───────────────────────┘
         ↓ (verify tests)
         ↓
┌─ Producción (Railway) ┐
│ • DEBUG=False         │
│ • PostgreSQL          │
│ • CORS: Exacto        │
│ • SSL/HTTPS: Sí       │
│ • Backup DB           │
│ • Auto-scaling        │
└───────────────────────┘
```

---

## 📊 Comparación: Desarrollo vs Producción

| Aspecto | Desarrollo | Producción |
|---------|-----------|-----------|
| **DEBUG** | True | False |
| **Base de Datos** | SQLite (archivo) | PostgreSQL (servidor) |
| **CORS** | Todos los orígenes | Solo dominios permitidos |
| **SSL/HTTPS** | No requerido | Requerido |
| **Static Files** | Django sirve | S3/CDN (en Railway) |
| **Logs** | Consola | Archivo/Sentry |
| **Cache** | En memoria | Redis/Memcached |
| **Email** | Console | SMTP real |
| **Backup DB** | Manual | Automático |

---

## 🔄 Actualización de Variables en Producción

```
1. Usuario cambia variable en Railway UI
   ↓
2. Railway detecta cambio
   ↓
3. Railway reinicia automáticamente la app
   ↓
4. Nuevo Procfile ejecuta release command
   ↓
5. App carga nuevas variables de entorno
   ↓
6. App inicia con nueva configuración
```

---

## 🎯 Checklist Visual del Despliegue

```
Local Development
  ✅ Clone repo
  ✅ Create virtual env
  ✅ pip install -r requirements.txt
  ✅ python manage.py migrate
  ✅ python manage.py runserver
  ✅ Test en http://localhost:8000
  
        ↓
        
GitHub Repository
  ✅ git add .
  ✅ git commit
  ✅ git push origin main
  
        ↓
        
Railway Setup
  ✅ Connect GitHub repo
  ✅ Add PostgreSQL
  ✅ Set environment variables
  ✅ Procfile file exists
  ✅ requirements.txt exists
  
        ↓
        
Automated Deploy
  ✅ Build (npm/pip)
  ✅ Release (migrate)
  ✅ Web (gunicorn)
  
        ↓
        
Production Live
  ✅ App running on railway.app
  ✅ SSL/HTTPS active
  ✅ PostgreSQL connected
  ✅ Static files served
  ✅ Admin panel accessible
```

---

## 🔌 Conexión de Base de Datos

```
┌─────────────────┐
│  Django App     │
│   settings.py   │
└────────┬────────┘
         │
    USE_POSTGRES=1
         │
         ↓
┌──────────────────────────────────┐
│ POSTGRES Connection String       │
├──────────────────────────────────┤
│ Engine: postgresql               │
│ Name: crediticia_db              │
│ User: postgres                   │
│ Password: ****                   │
│ Host: railway-db.internal       │
│ Port: 5432                       │
└────────┬─────────────────────────┘
         │
         ↓
┌─────────────────────────┐
│  PostgreSQL Database    │
│  (Railway Managed)      │
│  Backup: Automático     │
│  SSL: Sí                │
└─────────────────────────┘
```

---

**¡Tu arquitectura está lista para producción! 🚀**
