import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    filename='aeropuerto.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Database:
    def __init__(self):
        self.host = "aeropuerto-db.clg4k8ygi0xf.us-east-2.rds.amazonaws.com"
        self.database = "aeropuerto_db"
        self.user = "admin_aeropuerto"
        self.password = "Remsempai141"
        self.connection = None
        
    def connect(self):
        """Establece conexión con la base de datos AWS RDS"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=3306
            )
            if self.connection.is_connected():
                logging.info(f"Conexión establecida a {self.host}")
                return self.connection
        except Error as e:
            logging.error(f"Error de conexión: {e}")
            raise
    
    def disconnect(self):
        """Cierra la conexión a la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("Conexión cerrada")
    
    def execute_query(self, query, params=None, commit=False):
        """Ejecuta una consulta SQL"""
        connection = self.connect()
        cursor = None
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if commit:
                connection.commit()
                logging.info(f"Query ejecutada: {query}")
                result = True
            else:
                result = cursor.fetchall()
            
            return result
        except Error as e:
            logging.error(f"Error en query: {e}")
            if commit:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            self.disconnect()
    
    def log_operation(self, usuario_id, operacion, tabla, registro_id=None, detalles=""):
        """Registra una operación en el log"""
        query = """
        INSERT INTO log_operaciones (usuario_id, operacion, tabla_afectada, registro_id, detalles, fecha_hora)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """
        self.execute_query(query, (usuario_id, operacion, tabla, registro_id, detalles), commit=True)
        