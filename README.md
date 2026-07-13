# HexOPS Manager — Gestor de Clientes & Compras (Flask + Arquitectura Hexagonal)

Plataforma web construida en **Python Flask** siguiendo los principios de **Arquitectura Hexagonal (Ports & Adapters)** y **Clean Code**, con persistencia en **SQLite** y preparada para despliegue en **Render Web Services (Free Tier)**.

---

## ✨ Características Principales

1. **Arquitectura Hexagonal & Clean Code**:
   - **Domain (`src/domain/`)**: Modelos puros (`User`, `Client`, `Purchase`) y excepciones de dominio sin dependencias externas.
   - **Ports (`src/ports/`)**: Interfaces abstractas entrantes (Casos de uso / Servicios) y salientes (Repositorios).
   - **Application (`src/application/services/`)**: Lógica de negocio encapsulada (`AuthService`, `ClientService`, `PurchaseService`).
   - **Adapters (`src/adapters/`)**: Adaptadores web (Blueprints Flask, controladores, decoradores de seguridad) y adaptadores de infraestructura (SQLite y PBKDF2/Werkzeug).

2. **Administrador de Cuentas de Seguridad (User Account Manager)**:
   - Autenticación y control de acceso con sesiones seguras y hash PBKDF2.
   - Roles de operador y administrador (`@login_required`, `@admin_required`).
   - Usuario Administrador por defecto:
     - **Usuario**: `admin`
     - **Contraseña**: `admin123`

3. **Gestión de Clientes & Sincronización con `Consulta.html`**:
   - Registro y administración de clientes con los campos de `/Volumes/COS_202606/Consulta.html`:
     - `Nombre`
     - `Cédula`
     - `Proceso de Desempeño`
     - `Valor a Descontar`
   - Importación y sincronización automática o manual desde `Consulta.html`.

4. **Registro de Compras (Transacciones / Consumos)**:
   - Capacidad para agregar registros de compras (`concepto`, `monto`, `fecha_compra`, `notas`) asociados a cualquier cliente registrado.
   - Cálculo automático de resumen financiero (`Valor base a descontar`, `Total compras`, `Saldo neto`).

5. **UI/UX Premium (Glassmorphism & Vanilla CSS)**:
   - Diseño moderno en modo oscuro con tarjetas glassmorphism, gradientes esmeralda/cian y micro-animaciones en CSS puro (`static/css/index.css`).
   - Búsqueda y filtrado en tiempo real en tablas de clientes y compras.

6. **Generador de Informes Excel (`.xlsx`) y Envío Directo por GMAIL**:
   - Generación de informes por rango de fechas (típico: **20 del mes anterior al 19 del mes actual**) con nombre formateado en español (ej. `Mayo 20 hasta Junio 19 2026.xlsx`).
   - Estructura de columnas y estilo idénticos al archivo de referencia (`Nombre`, `Cedula`, `Porceso de Desempeno`, `Valor a Descontar`).
   - Módulo de envío directo por correo electrónico desde cuentas **GMAIL** con cuerpo, asunto y estructura idéntica al archivo de referencia `.eml`.

---

## 🏗️ Estructura del Proyecto

```text
restaurant-manager-ops/
├── app.py                      # Factory de la aplicación y CLI Flask
├── wsgi.py                     # Entry point para Gunicorn / Render
├── config.py                   # Configuración por entornos (Desarrollo/Producción)
├── requirements.txt            # Dependencias del proyecto
├── render.yaml                 # Blueprint para despliegue en Render Free Tier
├── seed_data.py                # Script de semilla e importación desde Consulta.html
├── src/
│   ├── domain/                 # Entidades y lógica pura de negocio
│   ├── ports/                  # Puertos de entrada y salida (Interfaces)
│   ├── application/            # Casos de uso e importador HTML
│   └── adapters/               # Controladores Web Flask y repositorios SQLite
├── static/
│   ├── css/index.css           # Sistema de diseño moderno Glassmorphism
│   └── js/app.js               # Lógica de modales y filtros interactivos
├── templates/                  # Vistas Jinja2 (Dashboard, Clientes, Compras, Seguridad)
└── tests/                      # Suite de pruebas automatizadas
```

---

## 🚀 Instalación y Ejecución Local con Entorno Virtual (`venv`)

Es una buena práctica ejecutar los proyectos de Python dentro de un **entorno virtual** aislado para evitar conflictos entre dependencias del sistema y del proyecto.

### Paso 1: Crear el Entorno Virtual (`venv`)
Abre tu terminal en la carpeta raíz del proyecto (`restaurant-manager-ops`) y ejecuta:

- **En macOS / Linux**:
  ```bash
  python3 -m venv venv
  ```
- **En Windows**:
  ```cmd
  python -m venv venv
  ```

### Paso 2: Activar el Entorno Virtual
Una vez creado, debes activarlo antes de instalar paquetes o ejecutar el proyecto:

- **En macOS / Linux (Zsh / Bash)**:
  ```bash
  source venv/bin/activate
  ```
- **En Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **En Windows (Command Prompt - CMD)**:
  ```cmd
  venv\Scripts\activate.bat
  ```

> [!TIP]
> Sabrás que el entorno virtual está activo porque tu terminal mostrará el prefijo **`(venv)`** al inicio de la línea de comandos.

### Paso 3: Instalar las Dependencias del Proyecto
Con el entorno virtual activo, actualiza `pip` e instala las librerías necesarias:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Inicializar Base de Datos e Importar `Consulta.html`
Ejecuta el script de inicialización para crear el usuario administrador por defecto e importar automáticamente los clientes desde `/Volumes/COS_202606/Consulta.html`:
```bash
python3 seed_data.py
```

### Paso 5: Iniciar el Servidor de Desarrollo
Ejecuta la aplicación web localmente:
```bash
python3 app.py
```
Abre tu navegador web en: **[http://localhost:5001](http://localhost:5001)**

> **Credenciales de Administrador por defecto:**
> - **Usuario**: `admin`
> - **Contraseña**: `admin123`

### Paso 6: Desactivar el Entorno Virtual (Al finalizar)
Cuando termines de trabajar en el proyecto, puedes salir del entorno virtual ejecutando simplemente:
```bash
deactivate
```

---

## ☁️ Despliegue en Render (Free Tier)

El proyecto incluye el archivo `render.yaml` preconfigurado:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT`
- Base de datos **SQLite** autogestionada en `instance/app.db`.

---

## 🧪 Pruebas Automatizadas

Para ejecutar la suite de pruebas unitarias:
```bash
python3 -m unittest tests/test_app.py
```
