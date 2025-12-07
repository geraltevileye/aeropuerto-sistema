# emergencia.py - Crea todo desde cero
print("="*60)
print("🚀 CREANDO SISTEMA AEROPORTUARIO COMPLETO")
print("="*60)

import psycopg2
import sys

try:
    print("\n1. 🔗 Conectando a la base de datos...")
    
    # Tus datos de Render
    conn = psycopg2.connect(
        host="dpg-d4qoq70gjchc73bg6qug-a.virginia-postgres.render.com",
        database="sistema_3szc",
        user="yova",
        password="wtL5fI3nEyhrYPqmP4TKVqS2h0IVT6qP"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("   ✅ ¡Conectado exitosamente a Render!")
    
    # 2. Crear tablas una por una
    print("\n2. 📄 Creando tablas...")
    
    # Tabla 1: Aerolineas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Aerolineas (
            id_aerolinea SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            codigo_IATA CHAR(2) UNIQUE NOT NULL,
            pais_origen VARCHAR(50),
            fecha_fundacion DATE
        )
    """)
    print("   ✅ Tabla 'Aerolineas' creada")
    
    # Tabla 2: Vuelos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Vuelos (
            id_vuelo VARCHAR(10) PRIMARY KEY,
            id_aerolinea INTEGER REFERENCES Aerolineas(id_aerolinea),
            origen VARCHAR(50) NOT NULL,
            destino VARCHAR(50) NOT NULL,
            fecha_salida TIMESTAMP NOT NULL,
            fecha_llegada TIMESTAMP NOT NULL,
            estado VARCHAR(20),
            puerta_embarque VARCHAR(10)
        )
    """)
    print("   ✅ Tabla 'Vuelos' creada")
    
    # Tabla 3: Pasajeros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Pasajeros (
            id_pasajero SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            pasaporte VARCHAR(20) UNIQUE NOT NULL,
            nacionalidad VARCHAR(50),
            fecha_nacimiento DATE,
            correo VARCHAR(100),
            telefono VARCHAR(20)
        )
    """)
    print("   ✅ Tabla 'Pasajeros' creada")
    
    # Tabla 4: Empleados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Empleados (
            id_empleado SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            puesto VARCHAR(20),
            id_aerolinea INTEGER REFERENCES Aerolineas(id_aerolinea),
            fecha_contratacion DATE
        )
    """)
    print("   ✅ Tabla 'Empleados' creada")
    
    # Tabla 5: Usuarios_Sistema (IMPORTANTE)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios_Sistema (
            id_usuario SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL,
            id_empleado INTEGER REFERENCES Empleados(id_empleado),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT TRUE
        )
    """)
    print("   ✅ Tabla 'Usuarios_Sistema' creada")
    
    # Tabla 6: Log_Operaciones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Log_Operaciones (
            id_log SERIAL PRIMARY KEY,
            id_usuario INTEGER REFERENCES Usuarios_Sistema(id_usuario),
            operacion VARCHAR(50) NOT NULL,
            tabla_afectada VARCHAR(50),
            id_registro_afectado VARCHAR(100),
            fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detalles TEXT
        )
    """)
    print("   ✅ Tabla 'Log_Operaciones' creada")
    
    # Tabla 7: Reservas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Reservas (
            id_reserva SERIAL PRIMARY KEY,
            id_pasajero INTEGER REFERENCES Pasajeros(id_pasajero),
            id_vuelo VARCHAR(10) REFERENCES Vuelos(id_vuelo),
            fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clase VARCHAR(20),
            asiento VARCHAR(5),
            precio NUMERIC(10,2),
            estado VARCHAR(20)
        )
    """)
    print("   ✅ Tabla 'Reservas' creada")
    
    # Tabla 8: Equipaje
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Equipaje (
            id_equipaje SERIAL PRIMARY KEY,
            id_pasajero INTEGER REFERENCES Pasajeros(id_pasajero),
            id_vuelo VARCHAR(10) REFERENCES Vuelos(id_vuelo),
            peso_kg NUMERIC(5,2),
            tipo VARCHAR(10),
            etiqueta VARCHAR(20) UNIQUE
        )
    """)
    print("   ✅ Tabla 'Equipaje' creada")
    
    # 3. Insertar datos básicos
    print("\n3. 📝 Insertando datos mínimos para probar...")
    
    # Insertar aerolíneas (si no existen)
    cursor.execute("SELECT COUNT(*) FROM Aerolineas")
    if cursor.fetchone()[0] == 0:
        aerolineas = [
            ('American Airlines', 'AA', 'USA', '1926-04-15'),
            ('Aeroméxico', 'AM', 'México', '1934-09-14'),
            ('Volaris', 'Y4', 'México', '2005-03-13')
        ]
        
        for nombre, codigo, pais, fecha in aerolineas:
            cursor.execute(
                "INSERT INTO Aerolineas (nombre, codigo_IATA, pais_origen, fecha_fundacion) VALUES (%s, %s, %s, %s)",
                (nombre, codigo, pais, fecha)
            )
        print("   ✅ 3 aerolíneas insertadas")
    
    # Insertar usuarios (si no existen)
    cursor.execute("SELECT COUNT(*) FROM Usuarios_Sistema")
    if cursor.fetchone()[0] == 0:
        # Contraseña para todos: admin123
        usuarios = [
            ('admin', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin'),
            ('responsable', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'responsable'),
            ('consulta', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'consulta')
        ]
        
        for username, password_hash, rol in usuarios:
            cursor.execute(
                "INSERT INTO Usuarios_Sistema (username, password_hash, rol) VALUES (%s, %s, %s)",
                (username, password_hash, rol)
            )
        print("   ✅ 3 usuarios insertados (admin/admin123)")
    
    # 4. Verificar
    print("\n4. 🔍 Verificando creación...")
    
    tablas = ['Aerolineas', 'Vuelos', 'Pasajeros', 'Usuarios_Sistema', 'Log_Operaciones']
    for tabla in tablas:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"   • {tabla}: {count} registros")
        except:
            print(f"   • {tabla}: Error al verificar")
    
    # 5. Cerrar
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 ¡SISTEMA CREADO EXITOSAMENTE! 🎉")
    print("="*60)
    
    print("""
✅ LOGRO PRINCIPAL:
-----------------
• 8 tablas creadas en tu base de datos de Render
• 3 usuarios listos para usar
• Estructura completa para tu proyecto

🔑 CREDENCIALES:
--------------
admin / admin123
responsable / admin123  
consulta / admin123

🚀 SIGUIENTE PASO:
---------------
1. Instalar Flask: python -m pip install Flask
2. Ejecutar: python app.py
3. Abrir: http://localhost:5000
""")
    
except psycopg2.Error as e:
    print(f"\n❌ ERROR DE BASE DE DATOS: {e}")
    print("\nPosibles soluciones:")
    print("• Verifica que tu base de datos en Render esté 'Active'")
    print("• Espera 1-2 minutos si acabas de crear la base de datos")
    print("• Revisa las credenciales")
except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()

input("\nPresiona Enter para salir...")
