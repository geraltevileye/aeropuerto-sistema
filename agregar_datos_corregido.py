# agregar_datos_corregido.py - Versión corregida
import psycopg2
from datetime import datetime, timedelta

print("="*60)
print("📊 AGREGANDO DATOS DE PRUEBA (VERSIÓN CORREGIDA)")
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
    
    # PRIMERO: OBTENER LOS IDs REALES DE LAS AEROLÍNEAS
    print("\n🔍 Obteniendo aerolíneas existentes...")
    cursor.execute("SELECT id_aerolinea, nombre, codigo_IATA FROM Aerolineas ORDER BY id_aerolinea")
    aerolineas_existentes = cursor.fetchall()
    
    # Crear mapeo de código IATA a ID
    mapa_aerolineas = {}
    for id_aero, nombre, codigo in aerolineas_existentes:
        mapa_aerolineas[codigo] = id_aero
        print(f"   • {nombre} ({codigo}) → ID: {id_aero}")
    
    if not mapa_aerolineas:
        print("❌ No hay aerolíneas en la base de datos")
        print("   Ejecuta primero: python emergencia.py")
        input("\nPresiona Enter para salir...")
        exit()
    
    # 1. AGREGAR MÁS AEROLÍNEAS SI FALTAN
    print("\n1. ✈️  Verificando aerolíneas...")
    
    aerolineas_necesarias = [
        ('Delta Air Lines', 'DL', 'Estados Unidos', '1924-05-30'),
        ('Air France', 'AF', 'Francia', '1933-10-07'),
        ('Lufthansa', 'LH', 'Alemania', '1926-01-06'),
        ('British Airways', 'BA', 'Reino Unido', '1974-03-31'),
        ('Emirates', 'EK', 'Emiratos Árabes', '1985-03-25')
    ]
    
    for nombre, codigo, pais, fecha in aerolineas_necesarias:
        if codigo not in mapa_aerolineas:
            cursor.execute('''
                INSERT INTO Aerolineas (nombre, codigo_IATA, pais_origen, fecha_fundacion)
                VALUES (%s, %s, %s, %s)
                RETURNING id_aerolinea
            ''', (nombre, codigo, pais, fecha))
            nuevo_id = cursor.fetchone()[0]
            mapa_aerolineas[codigo] = nuevo_id
            print(f"   ✅ {nombre} agregada (ID: {nuevo_id})")
        else:
            print(f"   ✓ {nombre} ya existe (ID: {mapa_aerolineas[codigo]})")
    
    # 2. AGREGAR MÁS VUELOS (usando IDs correctos)
    print("\n2. 🛫 Agregando vuelos...")
    
    # Fechas para los vuelos
    hoy = datetime.now()
    
    vuelos = [
        # Vuelos para hoy - Usar códigos IATA que se mapearán a IDs
        ('DL789', 'DL', 'ATL', 'MEX', hoy.replace(hour=9, minute=30), hoy.replace(hour=12, minute=45), 'Programado', 'E12'),
        ('AF123', 'AF', 'CDG', 'JFK', hoy.replace(hour=11, minute=0), hoy.replace(hour=15, minute=30), 'Programado', 'F5'),
        ('LH456', 'LH', 'FRA', 'LAX', hoy.replace(hour=14, minute=20), hoy.replace(hour=18, minute=45), 'Abordando', 'G8'),
        ('BA789', 'BA', 'LHR', 'MAD', hoy.replace(hour=16, minute=45), hoy.replace(hour=19, minute=30), 'Programado', 'H3'),
        ('EK101', 'EK', 'DXB', 'SIN', hoy.replace(hour=20, minute=0), hoy.replace(hour=6, minute=30), 'Programado', 'I7'),
        
        # Vuelos para mañana
        ('DL202', 'DL', 'MEX', 'ATL', hoy + timedelta(days=1, hours=8), hoy + timedelta(days=1, hours=11), 'Programado', 'A1'),
        ('AF303', 'AF', 'JFK', 'CDG', hoy + timedelta(days=1, hours=10), hoy + timedelta(days=1, hours=22), 'Programado', 'B2'),
        ('LH404', 'LH', 'LAX', 'FRA', hoy + timedelta(days=1, hours=12), hoy + timedelta(days=1, hours=6), 'Programado', 'C3'),
        ('BA505', 'BA', 'MAD', 'LHR', hoy + timedelta(days=1, hours=14), hoy + timedelta(days=1, hours=16), 'Programado', 'D4'),
        ('EK606', 'EK', 'SIN', 'DXB', hoy + timedelta(days=1, hours=18), hoy + timedelta(days=1, hours=22), 'Programado', 'E5')
    ]
    
    vuelos_agregados = 0
    for id_vuelo, codigo_aero, origen, destino, salida, llegada, estado, puerta in vuelos:
        if codigo_aero in mapa_aerolineas:
            id_aerolinea = mapa_aerolineas[codigo_aero]
            try:
                cursor.execute('''
                    INSERT INTO Vuelos (id_vuelo, id_aerolinea, origen, destino, fecha_salida, fecha_llegada, estado, puerta_embarque)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id_vuelo) DO NOTHING
                ''', (id_vuelo, id_aerolinea, origen, destino, salida, llegada, estado, puerta))
                vuelos_agregados += 1
            except:
                pass  # Si ya existe, no hay problema
        else:
            print(f"   ⚠️  Aerolínea {codigo_aero} no encontrada para vuelo {id_vuelo}")
    
    print(f"   ✅ {vuelos_agregados} vuelos agregados/actualizados")
    
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
    
    pasajeros_agregados = 0
    for nombre, apellidos, pasaporte, nacionalidad, fecha_nac, correo, telefono in pasajeros:
        try:
            cursor.execute('''
                INSERT INTO Pasajeros (nombre, apellidos, pasaporte, nacionalidad, fecha_nacimiento, correo, telefono)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (pasaporte) DO NOTHING
            ''', (nombre, apellidos, pasaporte, nacionalidad, fecha_nac, correo, telefono))
            pasajeros_agregados += 1
        except:
            pass
    
    print(f"   ✅ {pasajeros_agregados} pasajeros agregados")
    
    # 4. AGREGAR EMPLEADOS (5 total)
    print("\n4. 👨‍✈️ Agregando empleados...")
    
    # Obtener IDs de aerolíneas para empleados
    empleados = [
        ('Roberto', 'González', 'Piloto', 'AM', '2015-03-15'),  # Aeroméxico
        ('Fernanda', 'López', 'Azafata', 'AA', '2018-07-22'),   # American Airlines
        ('David', 'Smith', 'Controlador', None, '2010-11-10'),  # Sin aerolínea
        ('Laura', 'Chen', 'Mantenimiento', 'Y4', '2016-05-30'), # Volaris
        ('Santiago', 'Ramírez', 'Seguridad', None, '2019-02-14')
    ]
    
    empleados_agregados = 0
    for nombre, apellidos, puesto, codigo_aero, fecha_cont in empleados:
        id_aerolinea = mapa_aerolineas.get(codigo_aero) if codigo_aero else None
        try:
            cursor.execute('''
                INSERT INTO Empleados (nombre, apellidos, puesto, id_aerolinea, fecha_contratacion)
                VALUES (%s, %s, %s, %s, %s)
            ''', (nombre, apellidos, puesto, id_aerolinea, fecha_cont))
            empleados_agregados += 1
        except:
            pass
    
    print(f"   ✅ {empleados_agregados} empleados agregados")
    
    # 5. AGREGAR RESERVAS (necesitamos IDs de pasajeros y vuelos existentes)
    print("\n5. 📅 Agregando reservas...")
    
    # Obtener algunos IDs de pasajeros y vuelos
    cursor.execute("SELECT id_pasajero FROM Pasajeros ORDER BY id_pasajero LIMIT 8")
    ids_pasajeros = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id_vuelo FROM Vuelos ORDER BY fecha_salida LIMIT 8")
    ids_vuelos = [row[0] for row in cursor.fetchall()]
    
    reservas_agregadas = 0
    for i in range(min(8, len(ids_pasajeros), len(ids_vuelos))):
        clases = ['Economica', 'Ejecutiva', 'Primera']
        precios = [180.00, 450.00, 850.00]
        
        cursor.execute('''
            INSERT INTO Reservas (id_pasajero, id_vuelo, clase, asiento, precio, estado)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            ids_pasajeros[i],
            ids_vuelos[i],
            clases[i % 3],
            f'{i+10}{chr(65 + i % 6)}',  # Ej: 10A, 11B, etc.
            precios[i % 3],
            'Confirmada' if i < 6 else 'En espera'
        ))
        reservas_agregadas += 1
    
    print(f"   ✅ {reservas_agregadas} reservas agregadas")
    
    # 6. AGREGAR EQUIPAJE
    print("\n6. 🧳 Agregando equipaje...")
    
    for i in range(min(6, len(ids_pasajeros), len(ids_vuelos))):
        cursor.execute('''
            INSERT INTO Equipaje (id_pasajero, id_vuelo, peso_kg, tipo, etiqueta)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (etiqueta) DO NOTHING
        ''', (
            ids_pasajeros[i],
            ids_vuelos[i],
            15.0 + (i * 2.5),  # Peso variable
            'Bodega' if i % 2 == 0 else 'Mano',
            f'BAG{1000 + i}'
        ))
    
    print("   ✅ 6 equipajes agregados")
    
    # 7. AGREGAR MÁS USUARIOS
    print("\n7. 👤 Agregando usuarios adicionales...")
    
    usuarios = [
        ('supervisor', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'responsable'),
        ('auditor', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'consulta')
    ]
    
    for username, password_hash, rol in usuarios:
        try:
            cursor.execute('''
                INSERT INTO Usuarios_Sistema (username, password_hash, rol)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            ''', (username, password_hash, rol))
        except:
            pass
    
    print("   ✅ 2 usuarios adicionales verificados")
    
    # 8. AGREGAR LOGS DE PRUEBA
    print("\n8. 📝 Agregando logs de prueba...")
    
    cursor.execute("SELECT id_usuario FROM Usuarios_Sistema LIMIT 3")
    ids_usuarios = [row[0] for row in cursor.fetchall()]
    
    operaciones = ['LOGIN', 'ALTA', 'EDICION', 'BAJA', 'CONSULTA']
    tablas = ['Aerolineas', 'Vuelos', 'Pasajeros', 'Usuarios_Sistema', 'Reservas']
    
    for i in range(5):
        cursor.execute('''
            INSERT INTO Log_Operaciones (id_usuario, operacion, tabla_afectada, id_registro_afectado, detalles)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            ids_usuarios[i % len(ids_usuarios)],
            operaciones[i % len(operaciones)],
            tablas[i % len(tablas)],
            i + 100,
            f'Operación de prueba {i+1} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        ))
    
    print("   ✅ 5 logs de prueba agregados")
    
    # Confirmar cambios
    conn.commit()
    
    print("\n" + "="*60)
    print("🎉 ¡DATOS AGREGADOS EXITOSAMENTE! 🎉")
    print("="*60)
    
    # Mostrar resumen
    print(f"📊 RESUMEN FINAL:")
    
    cursor.execute("SELECT COUNT(*) FROM Aerolineas")
    print(f"  • Aerolíneas: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Vuelos")
    print(f"  • Vuelos: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Pasajeros")
    print(f"  • Pasajeros: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Empleados")
    print(f"  • Empleados: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Reservas")
    print(f"  • Reservas: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Equipaje")
    print(f"  • Equipaje: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Usuarios_Sistema")
    print(f"  • Usuarios del sistema: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM Log_Operaciones")
    print(f"  • Logs del sistema: {cursor.fetchone()[0]}")
    
    print(f"\n🔑 USUARIOS DISPONIBLES:")
    cursor.execute("SELECT username, rol FROM Usuarios_Sistema ORDER BY rol, username")
    for user in cursor.fetchall():
        print(f"  • {user[0]} ({user[1]}) - contraseña: admin123")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("🚀 ¡SISTEMA LISTO PARA USAR!")
    print("🌐 Accede en: http://localhost:5000")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPresiona Enter para salir...")
