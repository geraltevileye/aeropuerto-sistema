# init_db_corregido.py - Versión corregida
print("🚀 Iniciando configuración de la base de datos...")
print("="*50)

try:
    # Verificar instalación
    print("1. Verificando psycopg2...")
    try:
        import psycopg2
        print("   ✅ psycopg2 ya está instalado")
    except ImportError:
        print("   📦 Instalando psycopg2-binary...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        import psycopg2
    
    # Tus datos de conexión
    print("\n2. Conectando a Render...")
    
    DB_HOST = "dpg-d4qoq70gjchc73bg6qug-a.virginia-postgres.render.com"
    DB_NAME = "sistema_3szc"
    DB_USER = "yova"
    DB_PASSWORD = "wtL5fI3nEyhrYPqmP4TKVqS2h0IVT6qP"
    
    # String de conexión CORREGIDO
    conn_string = f"host='{DB_HOST}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASSWORD}'"
    
    print(f"   Conectando a: {DB_HOST}")
    
    # Conectar
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print(f"   ✅ ¡Conectado exitosamente!")
    
    # Insertar datos de prueba si no existen
    print("\n3. Insertando datos de prueba...")
    
    # Verificar si ya existen aerolíneas
    cursor.execute("SELECT COUNT(*) FROM Aerolineas")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insertar aerolíneas
        aerolineas = [
            ('American Airlines', 'AA', 'Estados Unidos', '1926-04-15'),
            ('Aeroméxico', 'AM', 'México', '1934-09-14'),
            ('Volaris', 'Y4', 'México', '2005-03-13'),
            ('United Airlines', 'UA', 'Estados Unidos', '1926-04-06')
        ]
        
        for nombre, codigo, pais, fecha in aerolineas:
            cursor.execute(
                "INSERT INTO Aerolineas (nombre, codigo_IATA, pais_origen, fecha_fundacion) VALUES (%s, %s, %s, %s)",
                (nombre, codigo, pais, fecha)
            )
        
        print("   ✅ 4 aerolíneas insertadas")
    else:
        print(f"   ⚠️  Ya existen {count} aerolíneas")
    
    # Verificar usuarios
    cursor.execute("SELECT COUNT(*) FROM Usuarios_Sistema")
    count_usuarios = cursor.fetchone()[0]
    
    if count_usuarios == 0:
        # Insertar usuarios (todos con contraseña: admin123)
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
        
        print("   ✅ 3 usuarios insertados")
    else:
        print(f"   ⚠️  Ya existen {count_usuarios} usuarios")
    
    # Insertar algunos vuelos de prueba
    cursor.execute("SELECT COUNT(*) FROM Vuelos")
    count_vuelos = cursor.fetchone()[0]
    
    if count_vuelos == 0:
        vuelos = [
            ('AA123', 1, 'CDMX', 'NYC', '2024-12-10 08:00:00', '2024-12-10 14:30:00', 'Programado', 'A12'),
            ('AM456', 2, 'GDL', 'CUN', '2024-12-11 10:30:00', '2024-12-11 13:00:00', 'Abordando', 'B5'),
            ('Y4789', 3, 'MTY', 'TJS', '2024-12-12 07:45:00', '2024-12-12 09:15:00', 'Despegado', 'C3'),
            ('UA789', 1, 'LAX', 'MEX', '2024-12-13 22:00:00', '2024-12-14 04:30:00', 'Programado', 'D8')
        ]
        
        for id_vuelo, id_aero, origen, destino, salida, llegada, estado, puerta in vuelos:
            cursor.execute("""
                INSERT INTO Vuelos (id_vuelo, id_aerolinea, origen, destino, fecha_salida, fecha_llegada, estado, puerta_embarque) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (id_vuelo, id_aero, origen, destino, salida, llegada, estado, puerta))
        
        print("   ✅ 4 vuelos de prueba insertados")
    
    conn.commit()
    
    print("\n" + "="*50)
    print("🎉 ¡BASE DE DATOS CONFIGURADA EXITOSAMENTE! 🎉")
    print("="*50)
    
    print("""
📊 DATOS INSERTADOS:
------------------
• 4 aerolíneas
• 3 usuarios del sistema
• 4 vuelos de prueba

🔑 USUARIOS PARA INICIAR SESIÓN:
------------------------------
1. admin / admin123       → Control total
2. responsable / admin123 → Puede editar pero no borrar todo
3. consulta / admin123    → Solo ver información

🚀 INSTRUCCIONES:
---------------
1. Ejecuta: python app.py
2. Abre tu navegador en: http://localhost:5000
3. Inicia sesión con cualquiera de los usuarios anteriores
""")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("\nVerifica:")
    print("1. Tu conexión a internet")
    print("2. Que la base de datos en Render esté 'Active'")
    print("3. Los datos de conexión sean correctos")
except Exception as e:
    print(f"❌ Error inesperado: {e}")

input("\nPresiona Enter para salir...")
