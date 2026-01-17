# Constantes del sistema de análisis de bombas

# Cargar datos de accesorios desde JSON externo
import json
import os

try:
    with open("data_tablas/accesorios_data.json", "r", encoding="utf-8") as f:
        ACCESORIOS_DATA = json.load(f)
except FileNotFoundError:
    # Datos por defecto si no se encuentra el archivo
    ACCESORIOS_DATA = {
        "valvulas": [
            {"singularidad": "Válvula de Compuerta", "tipo": "Completamente Abierta", "k": 0.17, "lc_d": 9, "lc_d_medio": 9, "descripcion": "Válvula de Compuerta Completamente Abierta Lc/D=9"},
        ],
        "accesorios": [
            {"singularidad": "Codo Estándar (r/D = 1)-90", "tipo": "90°", "k": 0.9, "lc_d": 45, "lc_d_medio": 45, "descripcion": "Codo Estándar (r/D = 1)-90 90° Lc/D=45"},
        ],
        "medidores": [
            {"singularidad": "Medidor de Caudal1", "tipo": "Pistón", "k": 7, "lc_d": 350, "lc_d_medio": 350, "descripcion": "Medidor de Caudal1 Pistón Lc/D=350"},
        ]
    }
except Exception as e:
    print(f"Error cargando accesorios_data.json: {e}")
    ACCESORIOS_DATA = {"valvulas": [], "accesorios": [], "medidores": []}

# Cargar coeficientes de Hazen-Williams desde JSON externo
try:
    with open("data_tablas/hazen_williams_data.json", "r", encoding="utf-8") as f:
        hazen_data = json.load(f)
        # Crear diccionario de material -> coeficiente C
        HAZEN_WILLIAMS_C = {item["material"]: item["coeficiente_c"] for item in hazen_data.get("materiales", [])}
except FileNotFoundError:
    # Datos por defecto si no se encuentra el archivo
    HAZEN_WILLIAMS_C = {
        "PVC": 150,
        "HDPE (Polietileno)": 150,
        "Acero comercial": 140,
        "Hierro Dúctil": 140,
        "Hierro Fundido": 130,
        "HIERRO": 130,
    }
except Exception as e:
    print(f"Error cargando hazen_williams_data.json: {e}")
    HAZEN_WILLIAMS_C = {"PVC": 150, "HDPE (Polietileno)": 150, "Acero comercial": 140}

# Cargar datos de motores estándar desde JSON externo
try:
    with open("data_tablas/motores_estandar_data.json", "r", encoding="utf-8") as f:
        motores_data = json.load(f)
        MOTORES_ESTANDAR = motores_data.get("motores_estandar", [])
except FileNotFoundError:
    MOTORES_ESTANDAR = []
except Exception as e:
    print(f"Error cargando motores_estandar_data.json: {e}")
    MOTORES_ESTANDAR = []

# Cargar datos de tuberías desde JSON externo
try:
    with open("data_tablas/tuberias_data.json", "r", encoding="utf-8") as f:
        tuberias_data = json.load(f)
        TUBERIAS_DATA = tuberias_data.get("tuberias", [])
except FileNotFoundError:
    TUBERIAS_DATA = []
except Exception as e:
    print(f"Error cargando tuberias_data.json: {e}")
    TUBERIAS_DATA = []

# Cargar datos de tuberías PEAD desde JSON externo
try:
    with open("data_tablas/pead_data.json", "r", encoding="utf-8") as f:
        pead_data = json.load(f)
        PEAD_DATA = pead_data.get("pead_tuberias", [])
except FileNotFoundError:
    PEAD_DATA = []
except Exception as e:
    print(f"Error cargando pead_data.json: {e}")
    PEAD_DATA = []

# Cargar datos de tuberías de hierro dúctil desde JSON externo
try:
    with open("data_tablas/hierro_ductil_data.json", "r", encoding="utf-8") as f:
        hierro_ductil_data = json.load(f)
        HIERRO_DUCTIL_DATA = hierro_ductil_data.get("hierro_ductil", {})
except FileNotFoundError:
    HIERRO_DUCTIL_DATA = {}
except Exception as e:
    print(f"Error cargando hierro_ductil_data.json: {e}")
    HIERRO_DUCTIL_DATA = {}

# Cargar datos de tuberías de hierro fundido desde JSON externo
try:
    with open("data_tablas/hierro_fundido_data.json", "r", encoding="utf-8") as f:
        hierro_fundido_data = json.load(f)
        HIERRO_FUNDIDO_DATA = hierro_fundido_data.get("hierro_fundido", {})
except FileNotFoundError:
    HIERRO_FUNDIDO_DATA = {}
except Exception as e:
    print(f"Error cargando hierro_fundido_data.json: {e}")
    HIERRO_FUNDIDO_DATA = {}

# Cargar datos de tuberías PVC desde JSON externo
try:
    with open("data_tablas/pvc_data.json", "r", encoding="utf-8") as f:
        pvc_data = json.load(f)
        PVC_DATA = pvc_data.get("pvc_tuberias", {})
except FileNotFoundError:
    PVC_DATA = {}
except Exception as e:
    print(f"Error cargando pvc_data.json: {e}")
    PVC_DATA = {}

# Configuraciones de la aplicación
APP_CONFIG = {
    "TITLE": "Sistema de Análisis de Bombas",
    "VERSION": "2.0.0",
    "AUTHOR": "Asistente AI - Cursor",
    "DEFAULT_UNITS": {
        "FLOW": "L/s",
        "HEAD": "m",
        "POWER": "HP",
        "EFFICIENCY": "%",
        "NPSH": "m"
    }
}

# Configuraciones de gráficos
CHART_CONFIG = {
    "COLORS": {
        "PUMP_CURVE": "blue",
        "SYSTEM_CURVE": "red",
        "EFFICIENCY": "green",
        "POWER": "orange",
        "NPSH": "purple",
        "OPERATING_POINT": "orange",
        "BEP": "darkgreen",
        "NOMINAL_POINT": "purple"
    },
    "SYMBOLS": {
        "OPERATING_POINT": "star",
        "BEP": "diamond",
        "NOMINAL_POINT": "circle"
    }
}
