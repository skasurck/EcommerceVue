# Mktska Digital — EcommerceVue

Tienda de tecnología y cómputo en México. SPA full-stack construida con **Vue 3 + Vite** en el frontend y **Django 5 + Django REST Framework** en el backend.

---

## Tecnologías principales

| Capa | Stack |
|------|-------|
| Frontend | Vue 3, Vite 7, Pinia, Vue Router 4, Tailwind CSS 3, Axios |
| Backend | Django 5.2, Django REST Framework, SimpleJWT, Celery, Redis |
| Base de datos | PostgreSQL (producción) / SQLite (desarrollo) |
| Pagos | Mercado Pago Checkout Pro |
| IA | Anthropic Claude (clasificación de productos y reseñas) |
| Tests | Vitest + @vue/test-utils (frontend) / Django TestCase (backend) |

---

## Requisitos previos

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (o SQLite para desarrollo)
- Redis 7+ (para Celery y caché)

---

## Configuración inicial

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd EcommerceVue
```

### 2. Backend (Django)

```bash
# Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus valores (ver sección Variables de entorno)

cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 3. Frontend (Vue)

```bash
cd frontend
npm install
npm run dev
```

### 4. Celery (tareas asincrónicas — emails, cancelación de pedidos)

```bash
# Desde la raíz del proyecto, con el entorno virtual activado
cd backend
celery -A tienda worker -l info
```

---

## Variables de entorno del backend (`backend/.env`)

```env
# Django
SECRET_KEY=<clave-secreta-larga>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (PostgreSQL)
DB_NAME=mitienda_db
DB_USER=mitienda
DB_PASSWORD=<password>
DB_HOST=localhost
DB_PORT=5432

# Mercado Pago
MP_ACCESS_TOKEN=<token-produccion>
MP_ACCESS_TOKEN_TEST=<token-test>
MP_TEST_MODE=true
MP_WEBHOOK_SECRET=<secreto-webhook>

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<correo>
EMAIL_HOST_PASSWORD=<app-password>
DEFAULT_FROM_EMAIL=Mktska Digital <noreply@mktska.com>

# URLs
FRONTEND_BASE_URL=http://localhost:5173

# Carrito (opcionales)
CART_RESERVATION_MAX_HOURS=3
CART_RESERVATION_REFRESH_MINUTES=40
```

## Variables de entorno del frontend (`frontend/.env`)

```env
VITE_API_BASE=http://localhost:8000
```

---

## Estructura del proyecto

```
EcommerceVue/
├── backend/               # API REST Django
│   ├── tienda/            # Configuración del proyecto (settings, urls, celery)
│   ├── usuarios/          # Autenticación JWT, 2FA TOTP, gestión de usuarios
│   ├── productos/         # Catálogo, categorías, marcas, reseñas, búsqueda IA
│   ├── carrito/           # Carrito con reserva de stock
│   ├── pedidos/           # Pedidos, direcciones, métodos de envío
│   ├── pagos/             # Integración Mercado Pago + transferencia bancaria
│   ├── promotions/        # Cupones de descuento y ofertas diarias
│   └── suppliers/         # Integración proveedores (Supermex)
│
└── frontend/              # SPA Vue 3
    ├── src/
    │   ├── views/         # 30+ páginas (tienda + panel admin)
    │   ├── components/    # Componentes reutilizables (Navbar, ProductCard, etc.)
    │   ├── stores/        # Estado global con Pinia (auth, carrito, checkout…)
    │   ├── services/      # Axios + interceptores JWT
    │   ├── router/        # Rutas con guards de autenticación y roles
    │   └── tests/         # Tests unitarios con Vitest
    └── public/
```

---

## Comandos útiles

### Backend

```bash
# Correr tests
python manage.py test

# Crear migración
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Resetear categorías (importar árbol)
python manage.py shell < scripts/reset_categorias.py

# Procesar imágenes a WebP
python manage.py proceso_imagenes

# Cancelar pedidos abandonados manualmente
python manage.py cancelar_pedidos_abandonados
```

### Frontend

```bash
npm run dev          # Servidor de desarrollo (http://localhost:5173)
npm run build        # Build de producción → dist/
npm run test         # Tests en modo watch
npm run test:run     # Tests una sola vez
npm run test:coverage # Cobertura de tests
npm run lint         # ESLint + auto-fix
npm run format       # Prettier
```

---

## Flujo de autenticación

1. `POST /api/auth/login/` → devuelve `token` (access) + `refresh` + `user`
2. Administradores con 2FA activo reciben `{ requires_2fa: true, challenge }` → continúan en `POST /api/auth/login/2fa/`
3. El access token dura **3 horas**; el refresh dura **1 día**
4. El interceptor de Axios renueva el token automáticamente 60 segundos antes de que expire

---

## Flujo de pago (Mercado Pago)

1. El usuario confirma el pedido → se crea con estado `iniciado`
2. El backend llama a la API de MP y obtiene una `preference_id`
3. El usuario es redirigido al checkout de MP
4. MP llama al webhook `/api/pagos/webhooks/mercadopago/` cuando se confirma el pago
5. El backend actualiza el estado del pedido a `pagado` y envía el email de confirmación

---

## Panel de administración

Ruta: `/admin`  
Requiere rol `admin` o `super_admin`.

| Sección | URL |
|---------|-----|
| Dashboard | `/admin` |
| Productos | `/admin/productos` |
| Pedidos | `/admin/pedidos` |
| Usuarios | `/admin/usuarios` |
| Cupones | `/admin/cupones` |
| Reseñas | `/admin/resenas` |
| Editor del Home | `/admin/home-editor` |
| Banners | `/admin/promo-banners` |
| Configuración | `/admin/configuracion` |
| Clasificación IA | `/admin/ai/clasificar-productos` |
| Importar proveedor | `/admin/suppliers/supermex` |

Panel de Django (solo superusuario): `/mktska-panel-x7k2/admin/`

---

## Convenciones de commits

```
feat: nueva funcionalidad
fix: corrección de bug
refactor: cambio de código sin nueva funcionalidad ni bug fix
docs: documentación
test: tests
chore: tareas de mantenimiento (deps, config)
```
