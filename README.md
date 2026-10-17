# Sistema de Notificaciones - Casilla Electrónica MTC / GORE PUNO

Sistema corporativo de emisión, custodia y no repudio de notificaciones administrativas, integrado directamente con el **Servicio Web de Casillas Electrónicas del Ministerio de Transportes y Comunicaciones (MTC)**.

---

## 🏛️ Especificación Oficial MTC (Oficina de Desarrollo Tecnológico y Digital)

### Credenciales de Desarrollo (GORE PUNO)
* **Base URL:** `https://wscasilla.mtc.gob.pe/ms-notific/v2/servicios-publicos`
* **Entidad Emisora:** Gobierno Regional de Puno (`GORE - PUNO`)
* **clientId:** `e8c61edc-f33b-4b64-b241-a2bc85c73402`
* **clientSecret:** `wqetekyaQHPK3QwAksSKuNofH0Cp5kIzBwht8lC3VC6XdRTjTZysTEwJEfAGCyWi0FSGDUPXEAMl6dTBli9tBqrStLTmh8fj3b7whBaSUnHGvE6LYTIUuMgjjphqeiqJ`

---

## 🔌 Servicios Oficiales MTC Implementados

### 1. Token Externo
* **Método & Ruta:** `GET /notificaciones/token`
* **Parámetros:** `grantType=authorization_code`, `clientId`, `clientSecret`
* **Respuesta:** `{ "accessToken": "...", "expiresIn": 3600 }`
* **Gestión:** Manejo de caché automático y renovación proactiva ante expiración o código 401.

### 2. Verificar Estado de Casilla
* **Método & Ruta:** `GET /verificar-estado-casilla`
* **Cabecera:** `Authorization: Bearer <accessToken>`
* **Parámetros:**
  - `codTipoPersona`: `00001` (Persona Natural), `00002` (Jurídica), `00004` (Extranjera), `00005` (Natural con RUC).
  - `codTipoDocumento`: `00001` (RUC), `00002` (DNI), `00003` (CE), `00005` (Pasaporte), `00101` (Refugio), `00102` (PTP).
  - `nroDocumento`: Número de documento del administrado.
* **Respuesta:** `{ "success": true, "data": { "activo": true } }`

### 3. Notificaciones Externas (Depósito)
* **Método & Ruta:** `POST /notificaciones-externas`
* **Cabecera:** `Authorization: Bearer <accessToken>`, `Content-Type: application/json`
* **Cuerpo:**
  ```json
  {
    "codTipoPersona": "00001",
    "codTipoDocumento": "00002",
    "nroDocumento": "70123456",
    "asunto": "Notificación...",
    "mensaje": "<html>...</html>",
    "idCategoria": 5,
    "conSelloTiempo": true,
    "adjuntos": [
      {
        "url": "http://minio:9000/.../documento.pdf",
        "nombreArchivo": "documento.pdf"
      }
    ]
  }
  ```
* **Respuesta:** Retorna `idNotificacion`, `fechaNotificacion` y `constanciaDeposito` (UUID).

### 4. Constancias (Acuse de Depósito y Lectura)
* **Método & Ruta:** `GET /notificaciones/constancias/{idNotificacion}?tipo=base64`
* **Cabecera:** `Authorization: Bearer <accessToken>`
* **Respuesta:**
  ```json
  {
    "success": true,
    "data": {
      "constanciaDeposito": "base64...",
      "constanciaLectura": "base64... (presente cuando el administrado abre el mensaje)"
    }
  }
  ```

---

## 🛠️ Tecnologías y Arquitectura

* **Frontend:** Angular 22 (Standalone Components, Signals Reactivos, Tailwind CSS Nativo, Asistente Gemini AI).
* **Backend:** FastAPI (Python 3.12, SQLAlchemy 2.0 Async, Pydantic v2, HTTPX).
* **Worker en Background:** Bucle asíncrono periódico que sondea `GET /notificaciones/constancias/{idNotificacion}` y descarga la Constancia de Lectura oficial apenas el administrado abre la casilla.
* **Custodia Legal:** MinIO S3 (Almacenamiento de PDFs con cálculo y sellado de hash SHA-256).
* **Base de Datos:** PostgreSQL 16 con soporte `JSONB` y bitácora de auditoría inmutable.

---

## 🚀 Puesta en Marcha

### 1. Iniciar Infraestructura y Backend
```bash
docker compose up -d
```
* **Documentación Interactiva Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Consola de Custodia MinIO:** [http://localhost:9001](http://localhost:9001) (`minioadmin` / `minioadmin123`)

### 2. Iniciar Frontend Angular 22
```bash
cd frontend
npm install
npm start
```
* **Aplicación Web:** [http://localhost:4200](http://localhost:4200)
