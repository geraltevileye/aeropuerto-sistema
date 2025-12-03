import os
from datetime import timedelta

class Config:
    # Configuración de seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-aeropuerto-2024'
    
    # Configuración de base de datos desde variables de entorno
    # Usa valores por defecto para desarrollo local
    DB_HOST = os.environ.get('DB_HOST', 'aeropuerto-db.clg4k8ygi0xf.us-east-2.rds.amazonaws.com')
    DB_NAME = os.environ.get('DB_NAME', 'aeropuerto_db')
    DB_USER = os.environ.get('DB_USER', 'admin_aeropuerto')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Remsempai141')
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Configuración de usuarios
    ROLES = {
        'admin': 'Administrador',
        'responsable': 'Responsable',
        'consulta': 'Usuario Consulta'
    }
    
    # Configuración para Flask
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    TESTING = False