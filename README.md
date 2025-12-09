# Carga de Archivo Facturación Gas (SNBRNS)

Este proyecto es una aplicación web desarrollada en Python con Flask para la carga, validación y envío de datos de facturación de Gas LP a una base de datos SAP HANA.

## Funcionalidades Principales

*   **Carga de Archivo Excel:** Interfaz amigable para subir archivos `.xlsx`.
*   **Validación y Previsualización:** Muestra los datos cargados en una tabla con formato idéntico al Excel original (respetando decimales y fechas).
*   **Envío a SAP HANA:**
    *   Conexión segura mediante `hdbcli`.
    *   Limpieza automática de la tabla destino (`TRUNCATE`) antes de cada carga para garantizar consistencia.
    *   Inserción masiva de datos (`INSERT`).
    *   Soporte híbrido para credenciales: Lee desde archivo `.env` (Local) o `VCAP_SERVICES` (SAP BTP Cloud Foundry).
*   **Feedback al Usuario:** Alertas visuales con SweetAlert2 y logs detallados en consola.

## Requisitos Previos

*   Python 3.11 o superior.
*   Acceso a una instancia de SAP HANA.
*   Archivo `.env` configurado (para ejecución local).

## Instalación y Configuración Local

1.  **Clonar el repositorio o descargar el código.**

2.  **Crear y activar un entorno virtual:**
    ```bash
    # En Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo llamado `.env` en la raíz del proyecto con tus credenciales de HANA:
    ```env
    HANA_HOST=tu_host_de_hana (ej. zeus.hana.prod.eu-central-1.whitney.dbaas.ondemand.com)
    HANA_PORT=443
    HANA_USER=tu_usuario
    HANA_PASSWORD=tu_contraseña
    HANA_SCHEMA=tu_esquema (ej. 4A87446945C9455A8EAAFEC276742578)
    ```

## Ejecución

Para iniciar la aplicación en tu máquina local:

```bash
python app.py
```

Accede a la aplicación en tu navegador en: `http://localhost:5000`

## Estructura del Archivo Excel
El archivo a cargar debe ser un `.xlsx` y se espera que las primeras 7 columnas contengan los siguientes datos (comenzando desde la fila 2):
1.  **SITEID** (Texto)
2.  **COSTCENTER** (Texto)
3.  **NAME** (Texto)
4.  **LITERSLOADED** (Numérico - 3 decimales)
5.  **PRICE** (Numérico - 4 decimales)
6.  **DATE** (Fecha - DD/MM/YYYY)
7.  **AMOUNT** (Numérico - 2 decimales)

## Despliegue en SAP BTP
El proyecto ya incluye la configuración necesaria para Cloud Foundry:
*   `manifest.yml`: Configuración de la aplicación y memoria.
*   `Procfile`: Comando de arranque con Gunicorn.
*   `runtime.txt`: Versión de Python especificada.

Simplemente ejecuta `cf push` estando logueado en tu espacio de trabajo.
