import os
import json
import logging
from hdbcli import dbapi


def load_env_from_dotenv():
    path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if "=" in s:
                    k, v = s.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if not os.getenv(k):
                        os.environ[k] = v
    except Exception:
        pass


def get_hana_credentials():
    if not (
        os.getenv("HANA_HOST") and os.getenv("HANA_USER") and os.getenv("HANA_PASSWORD")
    ):
        vcap = os.getenv("VCAP_SERVICES")
        if vcap:
            try:
                data = json.loads(vcap)
                creds = None
                for _, services in data.items():
                    for s in services:
                        c = s.get("credentials", {})
                        if (
                            c.get("host")
                            and (c.get("user") or c.get("username"))
                            and c.get("password")
                        ):
                            creds = c
                            break
                    if creds:
                        break
                if creds:
                    os.environ.setdefault("HANA_HOST", str(creds.get("host")))
                    port_val = creds.get("port") or creds.get("port_tls")
                    if port_val is not None:
                        os.environ.setdefault("HANA_PORT", str(port_val))
                    os.environ.setdefault(
                        "HANA_USER", str(creds.get("user") or creds.get("username"))
                    )
                    os.environ.setdefault("HANA_PASSWORD", str(creds.get("password")))
                    if creds.get("schema"):
                        os.environ.setdefault("HANA_SCHEMA", str(creds.get("schema")))
            except Exception:
                pass
    return {
        "host": os.getenv("HANA_HOST"),
        "port": int(os.getenv("HANA_PORT")) if os.getenv("HANA_PORT") else None,
        "user": os.getenv("HANA_USER"),
        "password": os.getenv("HANA_PASSWORD"),
        "schema": os.getenv("HANA_SCHEMA"),
    }


def get_hana_connection():
    c = get_hana_credentials()
    missing = []
    for key in ["host", "user", "password", "schema"]:
        if not c.get(key):
            missing.append(key)
    if missing:
        raise ValueError(
            "Faltan variables de entorno para HANA: "
            + ", ".join(
                [
                    {
                        "host": "HANA_HOST",
                        "user": "HANA_USER",
                        "password": "HANA_PASSWORD",
                        "schema": "HANA_SCHEMA",
                    }[m]
                    for m in missing
                ]
            )
        )
    conn = dbapi.connect(
        address=c.get("host"),
        port=c.get("port") or 443,
        user=c.get("user"),
        password=c.get("password"),
        encrypt=True,
        sslValidateCertificate=False,
    )
    schema = c.get("schema")
    if schema:
        cur = conn.cursor()
        cur.execute(f'SET SCHEMA "{schema}"')
        cur.close()
    return conn


def insert_gas_data(data):
    """
    Inserts data into GLOBALHITSS_EE_TEMPLPGASINVOICE.
    data: list of tuples/lists corresponding to columns:
    SITEID, COSTCENTER, NAME, LITERSLOADED, PRICE, DATE, AMOUNT
    """
    conn = get_hana_connection()
    try:
        cursor = conn.cursor()
        schema = os.getenv("HANA_SCHEMA")
        
        # Truncate table before insertion for data consistency
        logging.info("Iniciando truncado de tabla GLOBALHITSS_EE_TEMPLPGASINVOICE...")
        truncate_sql = f'TRUNCATE TABLE "{schema}"."GLOBALHITSS_EE_TEMPLPGASINVOICE"'
        cursor.execute(truncate_sql)
        logging.info("Tabla truncada correctamente.")
        
        sql = f'INSERT INTO "{schema}"."GLOBALHITSS_EE_TEMPLPGASINVOICE" (SITEID, COSTCENTER, NAME, LITERSLOADED, PRICE, "DATE", AMOUNT) VALUES (?, ?, ?, ?, ?, ?, ?)'
        cursor.executemany(sql, data)
        conn.commit()
        cursor.close()
    finally:
        conn.close()
