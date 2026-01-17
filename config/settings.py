# Configuraciones de la aplicación

import os
from typing import Dict, Any

class AppSettings:
    """Configuraciones centralizadas de la aplicación"""
    
    # Configuración de la aplicación
    APP_TITLE = "Sistema de Análisis de Bombas"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Asistente AI - Cursor"
    
    # Control de visibilidad de funciones de desarrollador
    # Cambiar a False para la versión pública
    SHOW_DEVELOPER_SECTION = True
    
    # Configuración de Streamlit
    STREAMLIT_CONFIG = {
        "page_title": "Análisis de Bombas",
        "page_icon": "🔧",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
    
    # Configuración de archivos
    FILES_CONFIG = {
        "PROJECT_EXTENSION": ".json",
        "EXCEL_EXTENSION": ".xlsx",
        "BACKUP_SUFFIX": "_backup",
        "DEFAULT_PROJECT_NAME": "Proyecto_Bomba"
    }
    
    # Configuración de cálculos
    CALCULATION_CONFIG = {
        "DEFAULT_POLYNOMIAL_DEGREE": 2,
        "INTERSECTION_TOLERANCE": 1e-6,
        "MAX_ITERATIONS": 1000,
        "BEP_EFFICIENCY_RANGE": (0.65, 1.15)  # 65-115% del BEP
    }
    
    # Configuración de gráficos
    CHART_CONFIG = {
        "DEFAULT_WIDTH": 800,
        "DEFAULT_HEIGHT": 600,
        "GRID_COLOR": "lightgray",
        "GRID_WIDTH": 1,
        "LEGEND_POSITION": "bottom"
    }
    
    # Configuración de exportación
    EXPORT_CONFIG = {
        "EXCEL_SHEET_NAMES": {
            "PUMP_CURVE": "Curva_Bomba_H-Q",
            "EFFICIENCY": "Curva_Rendimiento",
            "POWER": "Curva_Potencia",
            "NPSH": "Curva_NPSH",
            "SYSTEM_CURVE": "H-Q_sistema"
        },
        "INCLUDE_EQUATIONS": True,
        "INCLUDE_COEFFICIENTS": True
    }
    
    # Configuración de IA (futuro)
    AI_CONFIG = {
        "ENABLED": False,
        "DEFAULT_MODEL": "gpt-3.5-turbo",
        "MAX_TOKENS": 1000,
        "TEMPERATURE": 0.7
    }
    
    # Configuración de RAG (futuro)
    RAG_CONFIG = {
        "ENABLED": False,
        "VECTOR_STORE_PATH": "vector_store",
        "CHUNK_SIZE": 1000,
        "CHUNK_OVERLAP": 200
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Retorna toda la configuración como diccionario"""
        return {
            "app": {
                "title": cls.APP_TITLE,
                "version": cls.APP_VERSION,
                "author": cls.APP_AUTHOR
            },
            "streamlit": cls.STREAMLIT_CONFIG,
            "files": cls.FILES_CONFIG,
            "calculations": cls.CALCULATION_CONFIG,
            "charts": cls.CHART_CONFIG,
            "export": cls.EXPORT_CONFIG,
            "ai": cls.AI_CONFIG,
            "rag": cls.RAG_CONFIG
        }
    
    @classmethod
    def update_config(cls, section: str, key: str, value: Any) -> None:
        """Actualiza una configuración específica"""
        if hasattr(cls, f"{section.upper()}_CONFIG"):
            config = getattr(cls, f"{section.upper()}_CONFIG")
            config[key] = value
        else:
            raise ValueError(f"Sección de configuración '{section}' no encontrada")
    
    @classmethod
    def get_config_value(cls, section: str, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración específico"""
        if hasattr(cls, f"{section.upper()}_CONFIG"):
            config = getattr(cls, f"{section.upper()}_CONFIG")
            return config.get(key, default)
        return default
