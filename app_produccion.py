# app.py - Versión para producción
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
import psycopg2.extras
from datetime import datetime
from functools import wraps

app = Flask(__name__)

# Configuración para producción
app.secret_key = os.environ.get('SECRET_KEY', 'clave_por_defecto_cambiar_en_produccion')
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Obtener DATABASE_URL de variables de entorno
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://yova:wtL5fI3nEyhrYPqmP4TKVqS2h0IVT6qP@dpg-d4qoq70gjchc73bg6qug-a.virginia-postgres.render.com/sistema_3szc')

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    return psycopg2.connect(DATABASE_URL)

# ... [TODO EL RESTO DEL CÓDIGO SE MANTIENE IGUAL] ...
# Copia aquí TODO el código de tu app_final.py empezando desde la función log_operacion
# hasta el final, pero manteniendo las configuraciones de arriba

# ========== FUNCIONES AUXILIARES ==========
def log_operacion(operacion, tabla=None, registro_id=None, detalles=""):
    """Registra una operación en el log"""
    if 'user_id' in session:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO Log_Operaciones 
                   (id_usuario, operacion, tabla_afectada, id_registro_afectado, detalles) 
                   VALUES (%s, %s, %s, %s, %s)''',
                (session['user_id'], operacion, tabla, str(registro_id), detalles)
            )
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass

def obtener_aerolineas():
    """Obtiene lista de aerolíneas"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM Aerolineas ORDER BY nombre')
    aerolineas = cursor.fetchall()
    cursor.close()
    conn.close()
    return aerolineas

# ========== DECORADORES PARA PERMISOS ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión primero', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'rol' not in session or session['rol'] not in roles:
                flash('No tienes permisos para acceder a esta sección', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ... [COPIA AQUÍ TODAS LAS RUTAS DE TU app_final.py] ...
# Copia TODO el código desde @app.route('/') hasta el final

# ========== RUTAS PÚBLICAS ==========
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM Usuarios_Sistema WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            # Para esta demo, aceptamos cualquier contraseña
            session['user_id'] = user['id_usuario']
            session['username'] = user['username']
            session['rol'] = user['rol']
            
            log_operacion('LOGIN', 'Usuarios_Sistema', user['id_usuario'], f'Inicio de sesión: {username}')
            flash(f'¡Bienvenido {user["username"]}! Rol: {user["rol"]}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario no encontrado', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_operacion('LOGOUT', 'Usuarios_Sistema', session['user_id'], f'Cierre de sesión: {session["username"]}')
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

# ========== DASHBOARD ==========
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT COUNT(*) FROM Vuelos WHERE DATE(fecha_salida) = CURRENT_DATE")
    vuelos_hoy = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Aerolineas")
    total_aerolineas = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Pasajeros")
    total_pasajeros = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return render_template('dashboard.html',
                         username=session['username'],
                         rol=session['rol'],
                         vuelos_hoy=vuelos_hoy,
                         total_aerolineas=total_aerolineas,
                         total_pasajeros=total_pasajeros)

# ... [COPIA AQUÍ TODAS LAS DEMÁS RUTAS DE app_final.py] ...

# ========== INICIO ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print("="*60)
    print("🚀 SISTEMA AEROPORTUARIO EN PRODUCCIÓN")
    print("="*60)
    print(f"🌐 Servidor iniciado en puerto: {port}")
    print(f"🔧 Modo debug: {debug}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
