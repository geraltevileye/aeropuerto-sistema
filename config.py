# config.py - Configuración de la base de datos
import os

class Config:
    # Datos de tu base de datos en Render
    DB_HOST = "dpg-d4qoq70gjchc73bg6qug-a.virginia-postgres.render.com"
    DB_PORT = "5432"
    DB_NAME = "sistema_3szc"
    DB_USER = "yova"
    DB_PASSWORD = "wtL5fI3nEyhrYPqmP4TKVqS2h0IVT6qP"
    
    # URL de conexión
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Configuración de seguridad
    SECRET_KEY = 'clave_super_secreta_para_el_proyecto_123'