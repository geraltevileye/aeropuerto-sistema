# setup_completo.py - Crea tablas Y inserta datos
import psycopg2
import sys

def ejecutar_sql(cursor, sql):
    """Ejecuta comandos SQL separados por punto y coma"""
    comandos = sql.split(';')
    for comando in comandos:
        comando = comando.strip()
        if comando and not comando.startswith('--'):
            try:
                cursor.execute(comando)
                print(f"   ✅ Ejecutado: {comando[:50]}...")
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"   ⚠️  {e}")

def main():
    print("="*60)
    print("🚀 CONFIGURACIÓN COMPLETA DEL SISTEMA AEROPORTUARIO")
    print("="*60)
    
    try:
        # 1. Conectar a Render
        print("\n1. 🔗 Conectando a la base de datos en Render...")
        
        DB_HOST = "dpg-d4qoq70gjchc73bg6qug-a.virginia-postgres.render.com"
        DB_NAME = "sistema_3szc"
        DB_USER = "yova"
        DB_PASSWORD = "wtL5fI3nEyhrYPqmP4TKVqS2h0IVT6qP"
        
        conn_string = f"host='{DB_HOST}' dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASSWORD}'"
        
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print(f"   ✅ Conectado a: {DB_HOST}")
        
        # 2. Leer y ejecutar schema.sql
        print("\n2. 📄 Creando tablas desde schema.sql...")
        
        try:
            with open('schema.sql', 'r', encoding='utf-8') as file:
                sql_content = file.read()
            ejecutar_sql(cursor, sql_content)
            print("   ✅ Todas las tablas creadas")
        except FileNotFoundError:
            print("   ❌ Archivo schema.sql no encontrado")
            print("   Creando tablas manualmente...")
            
            # Crear tablas manualmente si no existe el archivo
            tablas_sql = '''
            CREATE TABLE IF NOT EXISTS Aerolineas (
                id_aerolinea SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                codigo_IATA CHAR(2) UNIQUE NOT NULL,
                pais_origen VARCHAR(50),
                fecha_fundacion DATE
            );

            CREATE TABLE IF NOT EXISTS Vuelos (
                id_vuelo VARCHAR(10) PRIMARY KEY,
                id_aerolinea INTEGER,
                origen VARCHAR(50) NOT NULL,
                destino VARCHAR(50) NOT NULL,
                fecha_salida TIMESTAMP NOT NULL,
                fecha_llegada TIMESTAMP NOT NULL,
                estado VARCHAR(20),
                puerta_embarque VARCHAR(10),
                FOREIGN KEY (id_aerolinea) REFERENCES Aerolineas(id_aerolinea)
            );

            CREATE TABLE IF NOT EXISTS Pasajeros (
                id_pasajero SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellidos VARCHAR(100) NOT NULL,
                pasaporte VARCHAR(20) UNIQUE NOT NULL,
                nacionalidad VARCHAR(50),
                fecha_nacimiento DATE,
                correo VARCHAR(100),
                telefono VARCHAR(20)
            );

            CREATE TABLE IF NOT EXISTS Empleados (
                id_empleado SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellidos VARCHAR(100) NOT NULL,
                puesto VARCHAR(20),
                id_aerolinea INTEGER,
                fecha_contratacion DATE,
                FOREIGN KEY (id_aerolinea) REFERENCES Aerolineas(id_aerolinea)
            );

            CREATE TABLE IF NOT EXISTS Usuarios_Sistema (
                id_usuario SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                rol VARCHAR(20) NOT NULL,
                id_empleado INTEGER NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
            );

            CREATE TABLE IF NOT EXISTS Log_Operaciones (
                id_log SERIAL PRIMARY KEY,
                id_usuario INTEGER,
                operacion VARCHAR(50) NOT NULL,
                tabla_afectada VARCHAR(50),
                id_registro_afectado VARCHAR(100),
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detalles TEXT,
                FOREIGN KEY (id_usuario) REFERENCES Usuarios_Sistema(id_usuario)
            );
            '''
            ejecutar_sql(cursor, tablas_sql)
        
        # 3. Insertar datos de prueba
        print("\n3. 📝 Insertando datos de prueba...")
        
        # Verificar e insertar aerolíneas
        cursor.execute("SELECT COUNT(*) FROM Aerolineas")
        if cursor.fetchone()[0] == 0:
            aerolineas = [
                ('American Airlines', 'AA', 'USA', '1926-04-15'),
                ('Aeroméxico', 'AM', 'México', '1934-09-14'),
                ('Volaris', 'Y4', 'México', '2005-03-13'),
                ('United Airlines', 'UA', 'USA', '1926-04-06')
            ]
            
            for nombre, codigo, pais, fecha in aerolineas:
                cursor.execute(
                    "INSERT INTO Aerolineas (nombre, codigo_IATA, pais_origen, fecha_fundacion) VALUES (%s, %s, %s, %s)",
                    (nombre, codigo, pais, fecha)
                )
            print("   ✅ 4 aerolíneas insertadas")
        else:
            print("   ⏩ Aerolíneas ya existen")
        
        # Verificar e insertar usuarios
        cursor.execute("SELECT COUNT(*) FROM Usuarios_Sistema")
        if cursor.fetchone()[0] == 0:
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
            print("   ⏩ Usuarios ya existen")
        
        # Verificar e insertar vuelos
        cursor.execute("SELECT COUNT(*) FROM Vuelos")
        if cursor.fetchone()[0] == 0:
            vuelos = [
                ('AA123', 1, 'CDMX', 'NYC', '2024-12-10 08:00:00', '2024-12-10 14:30:00', 'Programado', 'A12'),
                ('AM456', 2, 'GDL', 'CUN', '2024-12-11 10:30:00', '2024-12-11 13:00:00', 'Abordando', 'B5'),
                ('Y4789', 3, 'MTY', 'TJS', '2024-12-12 07:45:00', '2024-12-12 09:15:00', 'Despegado', 'C3'),
                ('UA789', 4, 'LAX', 'MEX', '2024-12-13 22:00:00', '2024-12-14 04:30:00', 'Programado', 'D8')
            ]
            
            for id_vuelo, id_aero, origen, destino, salida, llegada, estado, puerta in vuelos:
                cursor.execute("""
                    INSERT INTO Vuelos (id_vuelo, id_aerolinea, origen, destino, fecha_salida, fecha_llegada, estado, puerta_embarque) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (id_vuelo, id_aero, origen, destino, salida, llegada, estado, puerta))
            
            print("   ✅ 4 vuelos insertados")
        else:
            print("   ⏩ Vuelos ya existen")
        
        # 4. Mostrar resumen
        print("\n4. 📊 Resumen de la base de datos:")
        
        tablas = ['Aerolineas', 'Vuelos', 'Pasajeros', 'Empleados', 'Usuarios_Sistema', 'Log_Operaciones']
        for tabla in tablas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"   • {tabla}: {count} registros")
            except:
                print(f"   • {tabla}: No existe aún")
        
        # 5. Cerrar conexión
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 ¡CONFIGURACIÓN COMPLETA EXITOSA! 🎉")
        print("="*60)
        
        print("""
🔑 CREDENCIALES DE ACCESO:
------------------------
Usuario        | Contraseña | Rol
---------------|------------|-------------
admin          | admin123   | Administrador
responsable    | admin123   | Responsable  
consulta       | admin123   | Solo lectura

🚀 SIGUIENTES PASOS:
-------------------
1. Instalar Flask: python -m pip install Flask flask-login
2. Ejecutar la app: python app.py
3. Abrir navegador: http://localhost:5000
4. Iniciar sesión con las credenciales arriba
""")
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}")
        print("\nPosibles causas:")
        print("• No tienes conexión a internet")
        print("• La base de datos en Render no está activa")
        print("• Credenciales incorrectas")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("\nPresiona Enter para salir...")
