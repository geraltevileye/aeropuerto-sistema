from database import Database
from werkzeug.security import generate_password_hash, check_password_hash
import logging

db = Database()

class Usuario:
    def __init__(self, id, username, email, rol, nombre_completo):
        self.id = id
        self.username = username
        self.email = email
        self.rol = rol
        self.nombre_completo = nombre_completo
    
    @staticmethod
    def autenticar(username, password):
        """Autentica un usuario"""
        try:
            query = "SELECT id, username, email, rol, nombre_completo, password_hash FROM usuarios WHERE username = %s"
            result = db.execute_query(query, (username,))
            
            if result and len(result) > 0:
                usuario_data = result[0]
                # Verificar contraseña (en producción usar bcrypt)
                if usuario_data['password_hash'] == password:  # Simplificado para ejemplo
                    return Usuario(
                        usuario_data['id'],
                        usuario_data['username'],
                        usuario_data['email'],
                        usuario_data['rol'],
                        usuario_data['nombre_completo']
                    )
        except Exception as e:
            logging.error(f"Error en autenticación: {e}")
        return None
    
    @staticmethod
    def obtener_por_id(user_id):
        """Obtiene un usuario por su ID"""
        try:
            query = "SELECT id, username, email, rol, nombre_completo FROM usuarios WHERE id = %s"
            result = db.execute_query(query, (user_id,))
            
            if result and len(result) > 0:
                usuario_data = result[0]
                return Usuario(
                    usuario_data['id'],
                    usuario_data['username'],
                    usuario_data['email'],
                    usuario_data['rol'],
                    usuario_data['nombre_completo']
                )
        except Exception as e:
            logging.error(f"Error obteniendo usuario: {e}")
        return None

class Aeropuerto:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los aeropuertos"""
        return db.execute_query("SELECT * FROM aeropuertos ORDER BY nombre")
    
    @staticmethod
    def crear(nombre, codigo_iata, ciudad, pais):
        """Crea un nuevo aeropuerto"""
        query = """
        INSERT INTO aeropuertos (nombre, codigo_iata, ciudad, pais)
        VALUES (%s, %s, %s, %s)
        """
        return db.execute_query(query, (nombre, codigo_iata, ciudad, pais), commit=True)
    
    @staticmethod
    def actualizar(aeropuerto_id, nombre, codigo_iata, ciudad, pais):
        """Actualiza un aeropuerto"""
        query = """
        UPDATE aeropuertos 
        SET nombre = %s, codigo_iata = %s, ciudad = %s, pais = %s
        WHERE id = %s
        """
        return db.execute_query(query, (nombre, codigo_iata, ciudad, pais, aeropuerto_id), commit=True)
    
    @staticmethod
    def eliminar(aeropuerto_id):
        """Elimina un aeropuerto"""
        query = "DELETE FROM aeropuertos WHERE id = %s"
        return db.execute_query(query, (aeropuerto_id,), commit=True)

class Vuelo:
    @staticmethod
    def obtener_todos():
        """Obtiene todos los vuelos con información relacionada"""
        query = """
        SELECT v.*, 
               a1.nombre as aeropuerto_origen_nombre,
               a2.nombre as aeropuerto_destino_nombre,
               al.nombre as aerolinea_nombre
        FROM vuelos v
        LEFT JOIN aeropuertos a1 ON v.aeropuerto_origen_id = a1.id
        LEFT JOIN aeropuertos a2 ON v.aeropuerto_destino_id = a2.id
        LEFT JOIN aerolineas al ON v.aerolinea_id = al.id
        ORDER BY v.fecha_salida DESC
        """
        return db.execute_query(query)
    
    @staticmethod
    def crear(numero_vuelo, aerolinea_id, aeropuerto_origen_id, 
              aeropuerto_destino_id, fecha_salida, fecha_llegada, 
              estado, capacidad):
        """Crea un nuevo vuelo"""
        query = """
        INSERT INTO vuelos (numero_vuelo, aerolinea_id, aeropuerto_origen_id, 
                          aeropuerto_destino_id, fecha_salida, fecha_llegada, 
                          estado, capacidad)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return db.execute_query(query, (
            numero_vuelo, aerolinea_id, aeropuerto_origen_id,
            aeropuerto_destino_id, fecha_salida, fecha_llegada,
            estado, capacidad
        ), commit=True)

class Reservacion:
    @staticmethod
    def obtener_todos():
        """Obtiene todas las reservaciones"""
        query = """
        SELECT r.*, 
               p.nombre as pasajero_nombre,
               p.apellido as pasajero_apellido,
               v.numero_vuelo,
               v.fecha_salida
        FROM reservaciones r
        LEFT JOIN pasajeros p ON r.pasajero_id = p.id
        LEFT JOIN vuelos v ON r.vuelo_id = v.id
        ORDER BY r.fecha_reserva DESC
        """
        return db.execute_query(query)