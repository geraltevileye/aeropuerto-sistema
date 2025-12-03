import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Usuario, Aeropuerto, Vuelo, Reservacion
from database import Database
import logging
from functools import wraps

# Cargar variables de entorno desde .env (solo en desarrollo)
load_dotenv()

app = Flask(__name__)
app.config.from_object('config.Config')

# Configurar login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor inicia sesión para acceder a esta página"

db = Database()

@login_manager.user_loader
def load_user(user_id):
    return Usuario.obtener_por_id(user_id)

def rol_requerido(rol):
    """Decorador para verificar roles"""
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.rol != rol and current_user.rol != 'admin':
                flash('No tienes permiso para acceder a esta página', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = Usuario.autenticar(username, password)
        
        if usuario:
            login_user(usuario)
            db.log_operation(usuario.id, 'LOGIN', 'usuarios', usuario.id, f"Inicio de sesión exitoso")
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    db.log_operation(current_user.id, 'LOGOUT', 'usuarios', current_user.id, "Cierre de sesión")
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Obtener estadísticas
    stats = {}
    try:
        # Contar vuelos
        vuelos_result = db.execute_query("SELECT COUNT(*) as total FROM vuelos")
        stats['total_vuelos'] = vuelos_result[0]['total'] if vuelos_result else 0
        
        # Contar reservaciones activas
        reservas_result = db.execute_query("SELECT COUNT(*) as total FROM reservaciones WHERE estado = 'confirmada'")
        stats['reservas_activas'] = reservas_result[0]['total'] if reservas_result else 0
        
        # Contar aerolíneas
        aerolineas_result = db.execute_query("SELECT COUNT(*) as total FROM aerolineas WHERE activa = TRUE")
        stats['aerolineas_activas'] = aerolineas_result[0]['total'] if aerolineas_result else 0
        
    except Exception as e:
        logging.error(f"Error obteniendo estadísticas: {e}")
        stats = {'total_vuelos': 0, 'reservas_activas': 0, 'aerolineas_activas': 0}
    
    return render_template('dashboard.html', stats=stats)

# Rutas para Aeropuertos
@app.route('/aeropuertos')
@login_required
def aeropuertos():
    aeropuertos_list = Aeropuerto.obtener_todos()
    return render_template('aeropuertos.html', aeropuertos=aeropuertos_list)

@app.route('/aeropuertos/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('responsable')
def crear_aeropuerto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        codigo_iata = request.form['codigo_iata'].upper()
        ciudad = request.form['ciudad']
        pais = request.form['pais']
        
        try:
            Aeropuerto.crear(nombre, codigo_iata, ciudad, pais)
            db.log_operation(current_user.id, 'CREATE', 'aeropuertos', None, f"Aeropuerto creado: {nombre}")
            flash('Aeropuerto creado exitosamente', 'success')
            return redirect(url_for('aeropuertos'))
        except Exception as e:
            flash(f'Error creando aeropuerto: {str(e)}', 'danger')
    
    return render_template('crear_aeropuerto.html')

@app.route('/aeropuertos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@rol_requerido('responsable')
def editar_aeropuerto(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        codigo_iata = request.form['codigo_iata'].upper()
        ciudad = request.form['ciudad']
        pais = request.form['pais']
        
        try:
            Aeropuerto.actualizar(id, nombre, codigo_iata, ciudad, pais)
            db.log_operation(current_user.id, 'UPDATE', 'aeropuertos', id, f"Aeropuerto actualizado")
            flash('Aeropuerto actualizado exitosamente', 'success')
            return redirect(url_for('aeropuertos'))
        except Exception as e:
            flash(f'Error actualizando aeropuerto: {str(e)}', 'danger')
    
    # Obtener datos actuales
    aeropuerto = db.execute_query("SELECT * FROM aeropuertos WHERE id = %s", (id,))
    if aeropuerto:
        return render_template('editar_aeropuerto.html', aeropuerto=aeropuerto[0])
    else:
        flash('Aeropuerto no encontrado', 'danger')
        return redirect(url_for('aeropuertos'))

@app.route('/aeropuertos/eliminar/<int:id>')
@login_required
@rol_requerido('responsable')
def eliminar_aeropuerto(id):
    try:
        Aeropuerto.eliminar(id)
        db.log_operation(current_user.id, 'DELETE', 'aeropuertos', id, "Aeropuerto eliminado")
        flash('Aeropuerto eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error eliminando aeropuerto: {str(e)}', 'danger')
    
    return redirect(url_for('aeropuertos'))

# Rutas para Vuelos
@app.route('/vuelos')
@login_required
def vuelos():
    vuelos_list = Vuelo.obtener_todos()
    return render_template('vuelos.html', vuelos=vuelos_list)

@app.route('/vuelos/crear', methods=['GET', 'POST'])
@login_required
@rol_requerido('responsable')
def crear_vuelo():
    if request.method == 'POST':
        try:
            Vuelo.crear(
                request.form['numero_vuelo'],
                request.form['aerolinea_id'],
                request.form['aeropuerto_origen_id'],
                request.form['aeropuerto_destino_id'],
                request.form['fecha_salida'],
                request.form['fecha_llegada'],
                request.form['estado'],
                request.form['capacidad']
            )
            db.log_operation(current_user.id, 'CREATE', 'vuelos', None, f"Vuelo creado: {request.form['numero_vuelo']}")
            flash('Vuelo creado exitosamente', 'success')
            return redirect(url_for('vuelos'))
        except Exception as e:
            flash(f'Error creando vuelo: {str(e)}', 'danger')
    
    # Obtener datos para los select
    aerolineas = db.execute_query("SELECT * FROM aerolineas WHERE activa = TRUE")
    aeropuertos = db.execute_query("SELECT * FROM aeropuertos")
    
    return render_template('crear_vuelo.html', 
                          aerolineas=aerolineas, 
                          aeropuertos=aeropuertos)

# Rutas para Reservaciones
@app.route('/reservaciones')
@login_required
def reservaciones():
    reservaciones_list = Reservacion.obtener_todos()
    return render_template('reservaciones.html', reservaciones=reservaciones_list)

# API para consultas (para usuarios de consulta)
@app.route('/api/consultas/vuelos')
@login_required
def api_vuelos():
    """API para consultar vuelos (accesible para todos los usuarios)"""
    vuelos = Vuelo.obtener_todos()
    return jsonify(vuelos)

@app.route('/api/consultas/reservaciones')
@login_required
def api_reservaciones():
    """API para consultar reservaciones"""
    reservaciones = Reservacion.obtener_todos()
    return jsonify(reservaciones)

# Sistema de logs
@app.route('/logs')
@login_required
@rol_requerido('admin')
def ver_logs():
    """Solo el admin puede ver todos los logs"""
    logs = db.execute_query("""
    SELECT l.*, u.username, u.nombre_completo 
    FROM log_operaciones l
    LEFT JOIN usuarios u ON l.usuario_id = u.id
    ORDER BY l.fecha_hora DESC
    LIMIT 100
    """)
    return render_template('logs.html', logs=logs)

# Gestión de usuarios (solo admin)
@app.route('/usuarios')
@login_required
@rol_requerido('admin')
def usuarios():
    usuarios_list = db.execute_query("SELECT id, username, email, rol, nombre_completo FROM usuarios")
    return render_template('usuarios.html', usuarios=usuarios_list)

@app.route('/usuarios/crear', methods=['POST'])
@login_required
@rol_requerido('admin')
def crear_usuario():
    data = request.json
    try:
        query = """
        INSERT INTO usuarios (username, email, password_hash, rol, nombre_completo)
        VALUES (%s, %s, %s, %s, %s)
        """
        db.execute_query(query, (
            data['username'],
            data['email'],
            data['password'],  # En producción usar hash
            data['rol'],
            data['nombre_completo']
        ), commit=True)
        
        db.log_operation(current_user.id, 'CREATE', 'usuarios', None, f"Usuario creado: {data['username']}")
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Solo para desarrollo local
    app.run(debug=True, host='0.0.0.0', port=5000)