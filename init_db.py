from database import Database
import logging

def crear_base_datos():
    """Crea la base de datos y las tablas si no existen"""
    db = Database()
    
    # Conexión sin base de datos específica para crear la DB
    try:
        connection = mysql.connector.connect(
            host=db.host,
            user=db.user,
            password=db.password,
            port=3306
        )
        
        cursor = connection.cursor()
        
        # Crear base de datos si no existe
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db.database}")
        cursor.execute(f"USE {db.database}")
        
        # Tabla de usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol ENUM('admin', 'responsable', 'consulta') NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
        """)
        
        # Tabla de aerolíneas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS aerolineas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo_iata VARCHAR(2) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            pais VARCHAR(50),
            fecha_fundacion DATE,
            activa BOOLEAN DEFAULT TRUE
        )
        """)
        
        # Tabla de aeropuertos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS aeropuertos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo_iata VARCHAR(3) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            ciudad VARCHAR(50) NOT NULL,
            pais VARCHAR(50) NOT NULL,
            capacidad_pasajeros INT,
            pistas INT DEFAULT 1
        )
        """)
        
        # Tabla de pasajeros
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pasajeros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pasaporte VARCHAR(20) UNIQUE NOT NULL,
            nombre VARCHAR(50) NOT NULL,
            apellido VARCHAR(50) NOT NULL,
            fecha_nacimiento DATE,
            nacionalidad VARCHAR(50),
            telefono VARCHAR(20),
            email VARCHAR(100),
            frecuente BOOLEAN DEFAULT FALSE
        )
        """)
        
        # Tabla de vuelos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vuelos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero_vuelo VARCHAR(10) NOT NULL,
            aerolinea_id INT NOT NULL,
            aeropuerto_origen_id INT NOT NULL,
            aeropuerto_destino_id INT NOT NULL,
            fecha_salida DATETIME NOT NULL,
            fecha_llegada DATETIME NOT NULL,
            estado ENUM('programado', 'embarcando', 'despegado', 'aterrizado', 'cancelado', 'demorado') DEFAULT 'programado',
            capacidad INT NOT NULL,
            asientos_disponibles INT,
            FOREIGN KEY (aerolinea_id) REFERENCES aerolineas(id),
            FOREIGN KEY (aeropuerto_origen_id) REFERENCES aeropuertos(id),
            FOREIGN KEY (aeropuerto_destino_id) REFERENCES aeropuertos(id)
        )
        """)
        
        # Tabla de reservaciones
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            codigo_reserva VARCHAR(20) UNIQUE NOT NULL,
            pasajero_id INT NOT NULL,
            vuelo_id INT NOT NULL,
            fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clase ENUM('economica', 'ejecutiva', 'primera') DEFAULT 'economica',
            asiento VARCHAR(5),
            estado ENUM('confirmada', 'pendiente', 'cancelada', 'check-in') DEFAULT 'confirmada',
            precio DECIMAL(10,2),
            FOREIGN KEY (pasajero_id) REFERENCES pasajeros(id),
            FOREIGN KEY (vuelo_id) REFERENCES vuelos(id)
        )
        """)
        
        # Tabla de log de operaciones
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_operaciones (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            operacion VARCHAR(50) NOT NULL,
            tabla_afectada VARCHAR(50),
            registro_id INT,
            detalles TEXT,
            fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
        """)
        
        # Crear usuarios iniciales
        usuarios_iniciales = [
            ("admin", "admin@aeropuerto.com", "admin123", "admin", "Administrador Principal"),
            ("responsable", "responsable@aeropuerto.com", "resp123", "responsable", "Responsable Operaciones"),
            ("consulta", "consulta@aeropuerto.com", "cons123", "consulta", "Usuario Consulta")
        ]
        
        for username, email, password, rol, nombre in usuarios_iniciales:
            cursor.execute("""
            INSERT IGNORE INTO usuarios (username, email, password_hash, rol, nombre_completo)
            VALUES (%s, %s, %s, %s, %s)
            """, (username, email, password, rol, nombre))
        
        # Datos de ejemplo
        cursor.execute("""
        INSERT IGNORE INTO aerolineas (codigo_iata, nombre, pais) VALUES
        ('AA', 'American Airlines', 'USA'),
        ('DL', 'Delta Air Lines', 'USA'),
        ('AM', 'Aeromexico', 'Mexico'),
        ('IB', 'Iberia', 'Spain')
        """)
        
        cursor.execute("""
        INSERT IGNORE INTO aeropuertos (codigo_iata, nombre, ciudad, pais) VALUES
        ('MEX', 'Aeropuerto Internacional Benito Juárez', 'Ciudad de México', 'Mexico'),
        ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA'),
        ('MAD', 'Adolfo Suárez Madrid-Barajas', 'Madrid', 'Spain'),
        ('CDG', 'Charles de Gaulle Airport', 'Paris', 'France')
        """)
        
        connection.commit()
        logging.info("Base de datos y tablas creadas exitosamente")
        
    except Exception as e:
        logging.error(f"Error creando base de datos: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    crear_base_datos()
    print("Base de datos inicializada exitosamente")