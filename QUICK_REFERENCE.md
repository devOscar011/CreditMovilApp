# 📌 QUICK REFERENCE - Comandos Rápidos

## ⚡ Para Ejecutar Localmente (3 pasos)

```bash
# 1. Activar entorno virtual
env_stable\Scripts\activate  # Windows
source env_stable/bin/activate  # macOS/Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar servidor
python manage.py runserver
```

**URL**: http://localhost:8000

---

## 🚀 Para Desplegar en Railway (3 pasos)

```bash
# 1. Subir cambios a GitHub
git add .
git commit -m "agregar configuración producción"
git push

# 2. En Railway: Conectar repositorio
# https://railway.app → Deploy from GitHub

# 3. Agregar variables de entorno
# Ver: ENV_VARIABLES_RAILWAY.md
```

---

## 🔑 Variables de Entorno (Copiar/Pegar)

```env
DEBUG=False
SECRET_KEY=<GENERAR_NUEVA>
ALLOWED_HOSTS=<tu-app>.railway.app
CORS_ALLOWED_ORIGINS=https://tu-dominio.com
USE_POSTGRES=1
LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
```

---

## 🗄️ Comandos Django Básicos

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic

# Ejecutar pruebas
pytest

# Shell Django (para debug)
python manage.py shell
```

---

## 📚 Archivos de Documentación

| Archivo | Para |
|---------|------|
| `RESUMEN_CONFIGURACION.md` | Visión general |
| `COMO_EJECUTAR_LOCALMENTE.md` | Desarrollo local |
| `ENV_VARIABLES_RAILWAY.md` | Variables para Railway |
| `RAILWAY_DEPLOYMENT.md` | Despliegue completo |
| `GUIA_RAILWAY_PASO_A_PASO.md` | Pasos visuales |

---

## 🔧 Estructura Archivos Clave

```
CreditMovilApp/
├── crediticia/settings.py  ← Configuración (vars de entorno)
├── requirements.txt        ← Dependencias
├── Procfile               ← Configuración Railway
├── .env                   ← Variables locales
├── .env.example           ← Plantilla variables
└── manage.py              ← Comando principal Django
```

---

## ⚠️ Importante

- ❌ NO subir `.env` a GitHub
- ✅ Siempre generar nuevo `SECRET_KEY` para producción
- ✅ Cambiar `ALLOWED_HOSTS` a tu dominio real
- ✅ Usar `DEBUG=False` en producción

---

## 🔗 Links

- Railway: https://railway.app
- SECRET_KEY Generator: https://djecrety.ir/
- Django Docs: https://docs.djangoproject.com

---

## 💡 Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| "Module not found" | `pip install -r requirements.txt` |
| "Port in use" | `python manage.py runserver 8001` |
| "DB connection failed" | Verificar `USE_POSTGRES=1` en Railway |
| "CORS blocked" | Actualizar `CORS_ALLOWED_ORIGINS` |

---

**¿Más detalles?** Lee los archivos `.md` específicos.
