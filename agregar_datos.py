# agregar_datos.py - Agrega datos de prueba a todas las tablas
import psycopg2
from datetime import datetime, timedelta

print("="*60)
print("📊 AGREGANDO DATOS DE PRUEBA A TODAS LAS TABLAS")
print("="*60)

# Configuración de conexión
DB_CONFIG = {
    'host': 'dpg-d4qoq70gjchc73bg6qug-a.virginia-postgres.render.com',
    'database': 'sistema_3szc',
    'user': 'yova',
    'password': 'wtL5fI3nEyhrYPqmP4TKVqS2h0IVT6qP'
}

try:
    # Conectar a la base de datos
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Conectado a la base de datos")
    
    # 1. AGREGAR MÁS AEROLÍNEAS (5 total)
    print("\n1. ✈️  Agregando aerolíneas...")
    
    aerolineas = [
        ('Delta Air Lines', 'DL', 'Estados Unidos', '1924-05-30'),
        ('Air France', 'AF', 'Francia', '1933-10-07'),
        ('Lufthansa', 'LH', 'Alemania', '1926-01-06'),
        ('British Airways', 'BA', 'Reino Unido', '1974-03-31'),
        ('Emirates', 'EK', 'Emiratos Árabes', '1985-03-25')
    ]
    
    for nombre, codigo, pais, fecha in aerolineas:
        cursor.execute('''
            INSERT INTO Aerolineas (nombre, codigo_IATA, pais_origen, fecha_fundacion)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (codigo_IATA) DO NOTHING
        ''', (nombre, codigo, pais, fecha))
    
    print("   ✅ 5 aerolíneas agregadas")
    
    # 2. AGREGAR MÁS VUELOS (10 total)
    print("\n2. 🛫 Agregando vuelos...")
    
    # Fechas para los vuelos
    hoy = datetime.now()
    
    vuelos = [
        # Vuelos para hoy
        ('DL789', 5, 'ATL', 'MEX', hoy.replace(hour=9, minute=30), hoy.replace(hour=12, minute=45), 'Programado', 'E12'),
        ('AF123', 6, 'CDG', 'JFK', hoy.replace(hour=11, minute=0), hoy.replace(hour=15, minute=30), 'Programado', 'F5'),
        ('LH456', 7, 'FRA', 'LAX', hoy.replace(hour=14, minute=20), hoy.replace(hour=18, minute=45), 'Abordando', 'G8'),
        ('BA789', 8, 'LHR', 'MAD', hoy.replace(hour=16, minute=45), hoy.replace(hour=19, minute=30), 'Programado', 'H3'),
        ('EK101', 9, 'DXB', 'SIN', hoy.replace(hour=20, minute=0), hoy.replace(hour=6, minute=30), 'Programado', 'I7'),
        
        # Vuelos para mañana
        ('DL202', 5, 'MEX', 'ATL', hoy + timedelta(days=1, hours=8), hoy + timedelta(days=1, hours=11), 'Programado', 'A1'),
        ('AF303', 6, 'JFK', 'CDG', hoy + timedelta(days=1, hours=10), hoy + timedelta(days=1, hours=22), 'Programado', 'B2'),
        ('LH404', 7, 'LAX', 'FRA', hoy + timedelta(days=1, hours=12), hoy + timedelta(days=1, hours=6), 'Programado', 'C3'),
        ('BA505', 8, 'MAD', 'LHR', hoy + timedelta(days=1, hours=14), hoy + timedelta(days=1, hours=16), 'Programado', 'D4'),
        ('EK606', 9, 'SIN', 'DXB', hoy + timedelta(days=1, hours=18), hoy + timedelta(days=1, hours=22), 'Programado', 'E5')
    ]
    
    for id_vuelo, id_aero, origen, destino, salida, llegada, estado, puerta in vuelos:
        cursor.execute('''
            INSERT INTO Vuelos (id_vuelo, id_aerolinea, origen, destino, fecha_salida, fecha_llegada, estado, puerta_embarque)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_vuelo) DO NOTHING
        ''', (id_vuelo, id_aero, origen, destino, salida, llegada, estado, puerta))
    
    print("   ✅ 10 vuelos agregados")
    
    # 3. AGREGAR PASAJEROS (10 total)
    print("\n3. 👥 Agregando pasajeros...")
    
    pasajeros = [
        ('Ana', 'García', 'MEX123456', 'Mexicana', '1985-04-12', 'ana.garcia@email.com', '555-1001'),
        ('Luis', 'Martínez', 'ESP789012', 'Española', '1990-07-25', 'luis.martinez@email.com', '555-1002'),
        ('Sophie', 'Dubois', 'FRA345678', 'Francesa', '1988-11-03', 'sophie.dubois@email.com', '555-1003'),
        ('Hans', 'Schmidt', 'GER901234', 'Alemana', '1975-02-18', 'hans.schmidt@email.com', '555-1004'),
        ('Emma', 'Wilson', 'USA567890', 'Estadounidense', '1995-09-30', 'emma.wilson@email.com', '555-1005'),
        ('Carlos', 'Rodríguez', 'MEX234567', 'Mexicana', '1992-12-15', 'carlos.rod@email.com', '555-1006'),
        ('Isabella', 'Rossi', 'ITA890123', 'Italiana', '1987-06-22', 'isabella.rossi@email.com', '555-1007'),
        ('Kenji', 'Tanaka', 'JPN456789', 'Japonesa', '1993-03-08', 'kenji.tanaka@email.com', '555-1008'),
        ('Mohammed', 'Ali', 'UAE012345', 'Emiratí', '1980-08-17', 'mohammed.ali@email.com', '555-1009'),
        ('Olivia', 'Brown', 'UK678901', 'Británica', '1998-01-05', 'olivia.brown@email.com', '555-1010')
    ]
    
    for nombre, apellidos, pasaporte, nacionalidad, fecha_nac, correo, telefono in pasajeros:
        cursor.execute('''
            INSERT INTO Pasajeros (nombre, apellidos, pasaporte, nacionalidad, fecha_nacimiento, correo, telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (pasaporte) DO NOTHING
        ''', (nombre, apellidos, pasaporte, nacionalidad, fecha_nac, correo, telefono))
    
    print("   ✅ 10 pasajeros agregados")
    
    # 4. AGREGAR EMPLEADOS (5 total)
    print("\n4. 👨‍✈️ Agregando empleados...")
    
    empleados = [
        ('Roberto', 'González', 'Piloto', 2, '2015-03-15'),
        ('Fernanda', 'López', 'Azafata', 2, '2018-07-22'),
        ('David', 'Smith', 'Controlador', None, '2010-11-10'),
        ('Laura', 'Chen', 'Mantenimiento', 1, '2016-05-30'),
        ('Santiago', 'Ramírez', 'Seguridad', None, '2019-02-14')
    ]
    
    for nombre, apellidos, puesto, id_aerolinea, fecha_cont in empleados:
        cursor.execute('''
            INSERT INTO Empleados (nombre, apellidos, puesto, id_aerolinea, fecha_contratacion)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nombre, apellidos, puesto, id_aerolinea, fecha_cont))
    
    print("   ✅ 5 empleados agregados")
    
    # 5. AGREGAR RESERVAS (8 total)
    print("\n5. 📅 Agregando reservas...")
    
    reservas = [
        (1, 'AA123', 'Ejecutiva', '12A', 450.00, 'Confirmada'),
        (2, 'AM456', 'Economica', '25B', 220.00, 'Confirmada'),
        (3, 'Y4789', 'Primera', '1A', 850.00, 'Confirmada'),
        (4, 'UA789', 'Economica', '30C', 180.00, 'Confirmada'),
        (5, 'DL789', 'Ejecutiva', '8D', 520.00, 'Confirmada'),
        (6, 'AF123', 'Primera', '2A', 1200.00, 'Confirmada'),
        (7, 'LH456', 'Economica', '15F', 195.00, 'En espera'),
        (8, 'BA789', 'Ejecutiva', '10B', 480.00, 'Confirmada')
    ]
    
    for id_pasajero, id_vuelo, clase, asiento, precio, estado in reservas:
        cursor.execute('''
            INSERT INTO Reservas (id_pasajero, id_vuelo, clase, asiento, precio, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (id_pasajero, id_vuelo, clase, asiento, precio, estado))
    
    print("   ✅ 8 reservas agregadas")
    
    # 6. AGREGAR EQUIPAJE (6 total)
    print("\n6. 🧳 Agregando equipaje...")
    
    equipaje = [
        (1, 'AA123', 23.5, 'Bodega', 'BAG001'),
        (2, 'AM456', 8.0, 'Mano', 'BAG002'),
        (3, 'Y4789', 32.0, 'Bodega', 'BAG003'),
        (4, 'UA789', 12.5, 'Bodega', 'BAG004'),
        (5, 'DL789', 10.0, 'Mano', 'BAG005'),
        (6, 'AF123', 28.0, 'Bodega', 'BAG006')
    ]
    
    for id_pasajero, id_vuelo, peso, tipo, etiqueta in equipaje:
        cursor.execute('''
            INSERT INTO Equipaje (id_pasajero, id_vuelo, peso_kg, tipo, etiqueta)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (etiqueta) DO NOTHING
        ''', (id_pasajero, id_vuelo, peso, tipo, etiqueta))
    
    print("   ✅ 6 equipajes agregados")
    
    # 7. AGREGAR MÁS USUARIOS (2 adicionales)
    print("\n7. 👤 Agregando usuarios adicionales...")
    
    usuarios = [
        ('supervisor', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'responsable'),
        ('auditor', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'consulta')
    ]
    
    for username, password_hash, rol in usuarios:
        cursor.execute('''
            INSERT INTO Usuarios_Sistema (username, password_hash, rol)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        ''', (username, password_hash, rol))
    
    print("   ✅ 2 usuarios adicionales agregados")
    
    # 8. AGREGAR LOGS DE PRUEBA
    print("\n8. 📝 Agregando logs de prueba...")
    
    for i in range(1, 6):
        cursor.execute('''
            INSERT INTO Log_Operaciones (id_usuario, operacion, tabla_afectada, id_registro_afectado, detalles)
            VALUES (1, 'PRUEBA', 'Sistema', 'TEST', 'Log de prueba %s - Inicialización del sistema')
        ''', (i,))
    
    print("   ✅ 5 logs de prueba agregados")
    
    # Confirmar cambios
    conn.commit()
    
    print("\n" + "="*60)
    print("🎉 ¡DATOS AGREGADOS EXITOSAMENTE! 🎉")
    print("="*60)
    
    # Mostrar resumen
    cursor.execute("SELECT COUNT(*) FROM Aerolineas")
    print(f"📊 Resumen:")
    print(f"  • Aerolíneas: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Vuelos")
    print(f"  • Vuelos: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Pasajeros")
    print(f"  • Pasajeros: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Empleados")
    print(f"  • Empleados: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Usuarios_Sistema")
    print(f"  • Usuarios del sistema: {cursor.fetchone()[0]}")
    
    print(f"\n🔑 Usuarios disponibles:")
    cursor.execute("SELECT username, rol FROM Usuarios_Sistema")
    for user in cursor.fetchall():
        print(f"  • {user[0]} ({user[1]}) - contraseña: admin123")
    
    cursor.close()
    conn.close()
    
    print("\n🚀 Ahora puedes usar el sistema con datos completos!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPresiona Enter para salir...")
