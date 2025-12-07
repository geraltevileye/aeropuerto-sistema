# app.py - Sistema de Gestión Aeroportuaria Completo
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
import psycopg2.extras
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'aeropuerto_secret_key_2024'

# Configuración de la base de datos (TUS DATOS DE RENDER)
DB_CONFIG = {
    'host': 'dpg-d4qoq70gjchc73bg6qug-a.virginia-postgres.render.com',
    'database': 'sistema_3szc',
    'user': 'yova',
    'password': 'wtL5fI3nEyhrYPqmP4TKVqS2h0IVT6qP'
}

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    return psycopg2.connect(**DB_CONFIG)

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
            pass  # Si falla el log, continuamos igual

# ========== RUTAS PÚBLICAS ==========
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # En este ejemplo, cualquier contraseña funciona
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM Usuarios_Sistema WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            # Para esta demo, aceptamos cualquier contraseña
            # En producción usarías bcrypt para verificar
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

# ========== MIDDLEWARE PARA VERIFICAR SESIÓN ==========
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión primero', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'rol' not in session or session['rol'] not in roles:
                flash('No tienes permisos para acceder a esta sección', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== DASHBOARD Y RUTAS COMUNES ==========
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Estadísticas para el dashboard
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

# ========== MÓDULO PARA ADMINISTRADOR ==========
@app.route('/admin/aerolineas')
@login_required
@role_required('admin')
def admin_aerolineas():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM Aerolineas ORDER BY id_aerolinea')
    aerolineas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin/aerolineas.html', aerolineas=aerolineas)

@app.route('/admin/agregar_aerolinea', methods=['POST'])
@login_required
@role_required('admin')
def agregar_aerolinea():
    nombre = request.form['nombre']
    codigo = request.form['codigo']
    pais = request.form['pais']
    fecha = request.form['fecha'] if request.form['fecha'] else None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            '''INSERT INTO Aerolineas (nombre, codigo_IATA, pais_origen, fecha_fundacion) 
               VALUES (%s, %s, %s, %s) RETURNING id_aerolinea''',
            (nombre, codigo, pais, fecha)
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        
        log_operacion('ALTA', 'Aerolineas', nuevo_id, f'Aerolínea: {nombre}')
        flash('Aerolínea agregada exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_aerolineas'))

@app.route('/admin/eliminar_aerolinea/<int:id>')
@login_required
@role_required('admin')
def eliminar_aerolinea(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT nombre FROM Aerolineas WHERE id_aerolinea = %s', (id,))
        nombre = cursor.fetchone()[0]
        
        cursor.execute('DELETE FROM Aerolineas WHERE id_aerolinea = %s', (id,))
        conn.commit()
        
        log_operacion('BAJA', 'Aerolineas', id, f'Aerolínea eliminada: {nombre}')
        flash(f'Aerolínea "{nombre}" eliminada', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_aerolineas'))

# ========== MÓDULO PARA RESPONSABLE ==========
@app.route('/responsable/vuelos')
@login_required
@role_required('admin', 'responsable')
def responsable_vuelos():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT v.*, a.nombre as aerolinea_nombre 
        FROM Vuelos v 
        LEFT JOIN Aerolineas a ON v.id_aerolinea = a.id_aerolinea 
        ORDER BY v.fecha_salida DESC
    ''')
    vuelos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('responsable/vuelos.html', vuelos=vuelos)

@app.route('/responsable/agregar_vuelo', methods=['POST'])
@login_required
@role_required('admin', 'responsable')
def agregar_vuelo():
    id_vuelo = request.form['id_vuelo']
    id_aerolinea = request.form['id_aerolinea']
    origen = request.form['origen']
    destino = request.form['destino']
    fecha_salida = request.form['fecha_salida']
    fecha_llegada = request.form['fecha_llegada']
    estado = request.form['estado']
    puerta = request.form['puerta']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Vuelos (id_vuelo, id_aerolinea, origen, destino, fecha_salida, fecha_llegada, estado, puerta_embarque)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (id_vuelo, id_aerolinea, origen, destino, fecha_salida, fecha_llegada, estado, puerta))
        conn.commit()
        
        log_operacion('ALTA', 'Vuelos', id_vuelo, f'Vuelo: {id_vuelo} - {origen} a {destino}')
        flash('Vuelo agregado exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('responsable_vuelos'))

# ========== MÓDULO PARA CONSULTA ==========
@app.route('/consulta/vuelos_hoy')
@login_required
def consulta_vuelos_hoy():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT v.*, a.nombre as aerolinea_nombre 
        FROM Vuelos v 
        LEFT JOIN Aerolineas a ON v.id_aerolinea = a.id_aerolinea 
        WHERE DATE(v.fecha_salida) = CURRENT_DATE
        ORDER BY v.fecha_salida
    ''')
    vuelos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('consulta/vuelos_hoy.html', vuelos=vuelos)

@app.route('/consulta/pasajeros')
@login_required
def consulta_pasajeros():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM Pasajeros ORDER BY apellidos, nombre')
    pasajeros = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('consulta/pasajeros.html', pasajeros=pasajeros)

# ========== API PARA DATOS ==========
@app.route('/api/estadisticas')
@login_required
def api_estadisticas():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute("SELECT COUNT(*) FROM Vuelos")
    total_vuelos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Vuelos WHERE estado = 'Programado'")
    vuelos_programados = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Vuelos WHERE estado = 'Abordando'")
    vuelos_abordando = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_vuelos': total_vuelos,
        'vuelos_programados': vuelos_programados,
        'vuelos_abordando': vuelos_abordando
    })

@app.route('/api/logs')
@login_required
@role_required('admin')
def api_logs():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT l.*, u.username 
        FROM Log_Operaciones l 
        LEFT JOIN Usuarios_Sistema u ON l.id_usuario = u.id_usuario 
        ORDER BY l.fecha_hora DESC 
        LIMIT 50
    ''')
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify([dict(log) for log in logs])

# ========== RUTA PARA VER LOGS (HTML) ==========
@app.route('/admin/logs')
@login_required
@role_required('admin')
def ver_logs():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT l.*, u.username 
        FROM Log_Operaciones l 
        LEFT JOIN Usuarios_Sistema u ON l.id_usuario = u.id_usuario 
        ORDER BY l.fecha_hora DESC 
        LIMIT 100
    ''')
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin/logs.html', logs=logs)

# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500

# ========== INICIALIZACIÓN ==========
def crear_templates_si_no_existen():
    """Crea templates básicos si no existen"""
    templates_necesarios = {
        'templates/login.html': '''
{% extends "base.html" %}
{% block title %}Iniciar Sesión{% endblock %}
{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-6">
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="bi bi-person-badge"></i> Sistema Aeroportuario - Login</h4>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ url_for('login') }}">
                    <div class="mb-3">
                        <label class="form-label">Usuario:</label>
                        <input type="text" name="username" class="form-control" required 
                               placeholder="admin, responsable o consulta">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Contraseña:</label>
                        <input type="password" name="password" class="form-control" value="admin123" required>
                        <div class="form-text">Usa "admin123" para todos los usuarios de prueba</div>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-box-arrow-in-right"></i> Iniciar Sesión
                    </button>
                </form>
                <hr>
                <div class="alert alert-info">
                    <h6><i class="bi bi-info-circle"></i> Usuarios de prueba:</h6>
                    <strong>admin</strong> - Control total<br>
                    <strong>responsable</strong> - Puede editar (no borrar todo)<br>
                    <strong>consulta</strong> - Solo ver información
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
        
        'templates/base.html': '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Aeroportuario - {% block title %}Inicio{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.8.1/font/bootstrap-icons.css">
    <style>
        body { padding-top: 20px; background-color: #f8f9fa; }
        .navbar-brand { font-weight: bold; }
        .card { margin-bottom: 20px; border-radius: 10px; }
        .sidebar { background-color: #343a40; min-height: calc(100vh - 80px); }
        .sidebar a { color: white; padding: 10px 15px; display: block; text-decoration: none; }
        .sidebar a:hover { background-color: #495057; }
        .stat-card { border-left: 4px solid; }
        .stat-card.vuelos { border-color: #0d6efd; }
        .stat-card.aerolineas { border-color: #198754; }
        .stat-card.pasajeros { border-color: #ffc107; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="bi bi-airplane"></i> Sistema Aeroportuario
            </a>
            {% if 'username' in session %}
            <div class="navbar-text text-light">
                <i class="bi bi-person-circle"></i> {{ session.username }} 
                <span class="badge bg-secondary">{{ session.rol }}</span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm ms-3">
                    <i class="bi bi-box-arrow-right"></i> Salir
                </a>
            </div>
            {% endif %}
        </div>
    </nav>

    <div class="container">
        <!-- Mensajes Flash -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <!-- Contenido Principal -->
        {% block content %}{% endblock %}
    </div>

    <footer class="mt-5 py-3 bg-dark text-white text-center">
        <div class="container">
            <p class="mb-0">
                <i class="bi bi-airplane-engines"></i> Sistema de Gestión Aeroportuaria 
                &copy; 2024 - Base de datos en Render
            </p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
''',
        
        'templates/dashboard.html': '''
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<div class="row">
    <!-- Sidebar -->
    <div class="col-md-3">
        <div class="card sidebar">
            <div class="card-body">
                <h5 class="text-white mb-3"><i class="bi bi-menu-button"></i> Menú</h5>
                <div class="list-group list-group-flush">
                    {% if session.rol == 'admin' %}
                    <a href="{{ url_for('admin_aerolineas') }}" class="list-group-item list-group-item-action bg-transparent text-white">
                        <i class="bi bi-building"></i> Aerolíneas
                    </a>
                    <a href="{{ url_for('ver_logs') }}" class="list-group-item list-group-item-action bg-transparent text-white">
                        <i class="bi bi-journal-text"></i> Logs del Sistema
                    </a>
                    {% endif %}
                    
                    {% if session.rol in ['admin', 'responsable'] %}
                    <a href="{{ url_for('responsable_vuelos') }}" class="list-group-item list-group-item-action bg-transparent text-white">
                        <i class="bi bi-airplane"></i> Gestionar Vuelos
                    </a>
                    {% endif %}
                    
                    <a href="{{ url_for('consulta_vuelos_hoy') }}" class="list-group-item list-group-item-action bg-transparent text-white">
                        <i class="bi bi-calendar-check"></i> Vuelos de Hoy
                    </a>
                    
                    <a href="{{ url_for('consulta_pasajeros') }}" class="list-group-item list-group-item-action bg-transparent text-white">
                        <i class="bi bi-people"></i> Ver Pasajeros
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="col-md-9">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="bi bi-speedometer2"></i> Dashboard</h4>
            </div>
            <div class="card-body">
                <h5>Bienvenido, {{ username }}!</h5>
                <p class="text-muted">Rol: <span class="badge bg-secondary">{{ rol }}</span></p>
                
                <div class="row mt-4">
                    <div class="col-md-4">
                        <div class="card stat-card vuelos">
                            <div class="card-body">
                                <h5><i class="bi bi-airplane"></i> Vuelos Hoy</h5>
                                <h2 class="text-primary">{{ vuelos_hoy }}</h2>
                                <p class="text-muted">Vuelos programados para hoy</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card stat-card aerolineas">
                            <div class="card-body">
                                <h5><i class="bi bi-building"></i> Aerolíneas</h5>
                                <h2 class="text-success">{{ total_aerolineas }}</h2>
                                <p class="text-muted">Aerolíneas registradas</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-4">
                        <div class="card stat-card pasajeros">
                            <div class="card-body">
                                <h5><i class="bi bi-people"></i> Pasajeros</h5>
                                <h2 class="text-warning">{{ total_pasajeros }}</h2>
                                <p class="text-muted">Pasajeros en el sistema</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="bi bi-info-circle"></i> Instrucciones Rápidas</h6>
                        </div>
                        <div class="card-body">
                            <ul>
                                <li>Usa el menú lateral para navegar</li>
                                {% if session.rol == 'admin' %}
                                <li>Como <strong>Administrador</strong> tienes acceso completo</li>
                                {% elif session.rol == 'responsable' %}
                                <li>Como <strong>Responsable</strong> puedes gestionar vuelos pero no eliminar tablas</li>
                                {% elif session.rol == 'consulta' %}
                                <li>Como <strong>Consulta</strong> solo puedes ver información</li>
                                {% endif %}
                                <li>Todas las operaciones se registran en el log del sistema</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
    }
    
    for template_path, template_content in templates_necesarios.items():
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            print(f"✅ Template creado: {template_path}")

if __name__ == '__main__':
    # Crear templates si no existen
    crear_templates_si_no_existen()
    
    # Ejecutar la aplicación
    print("🚀 Iniciando Sistema Aeroportuario...")
    print("🌐 Accede en: http://localhost:5000")
    print("🔑 Usa: admin / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)

# ========== FUNCIONES PARA AEROLÍNEAS ==========
@app.route('/admin/editar_aerolinea/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def editar_aerolinea(id):
    nombre = request.form['nombre']
    codigo = request.form['codigo']
    pais = request.form['pais']
    fecha = request.form['fecha'] if request.form['fecha'] else None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE Aerolineas 
            SET nombre = %s, codigo_IATA = %s, pais_origen = %s, fecha_fundacion = %s
            WHERE id_aerolinea = %s
        ''', (nombre, codigo, pais, fecha, id))
        conn.commit()
        
        log_operacion('EDICION', 'Aerolineas', id, f'Aerolínea actualizada: {nombre}')
        flash('Aerolínea actualizada exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_aerolineas'))

# ========== FUNCIONES PARA VUELOS ==========
@app.route('/responsable/editar_vuelo/<id>', methods=['POST'])
@login_required
@role_required('admin', 'responsable')
def editar_vuelo(id):
    id_vuelo_nuevo = request.form['id_vuelo']
    id_aerolinea = request.form['id_aerolinea']
    origen = request.form['origen']
    destino = request.form['destino']
    fecha_salida = request.form['fecha_salida']
    fecha_llegada = request.form['fecha_llegada']
    estado = request.form['estado']
    puerta = request.form['puerta']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Si cambió el ID del vuelo, necesitamos actualizar la referencia
        if id_vuelo_nuevo != id:
            cursor.execute('UPDATE Vuelos SET id_vuelo = %s WHERE id_vuelo = %s', (id_vuelo_nuevo, id))
            id = id_vuelo_nuevo
        
        cursor.execute('''
            UPDATE Vuelos 
            SET id_aerolinea = %s, origen = %s, destino = %s, 
                fecha_salida = %s, fecha_llegada = %s, estado = %s, puerta_embarque = %s
            WHERE id_vuelo = %s
        ''', (id_aerolinea, origen, destino, fecha_salida, fecha_llegada, estado, puerta, id))
        conn.commit()
        
        log_operacion('EDICION', 'Vuelos', id, f'Vuelo actualizado: {id}')
        flash('Vuelo actualizado exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('responsable_vuelos'))

@app.route('/responsable/eliminar_vuelo/<id>')
@login_required
@role_required('admin')
def eliminar_vuelo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Vuelos WHERE id_vuelo = %s', (id,))
        conn.commit()
        
        log_operacion('BAJA', 'Vuelos', id, f'Vuelo eliminado: {id}')
        flash(f'Vuelo {id} eliminado', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('responsable_vuelos'))

# ========== FUNCIONES PARA PASAJEROS ==========
@app.route('/admin/pasajeros')
@login_required
@role_required('admin')
def admin_pasajeros():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Aplicar filtros si existen
    nombre = request.args.get('nombre', '')
    apellido = request.args.get('apellido', '')
    pasaporte = request.args.get('pasaporte', '')
    
    query = 'SELECT * FROM Pasajeros WHERE 1=1'
    params = []
    
    if nombre:
        query += ' AND nombre ILIKE %s'
        params.append(f'%{nombre}%')
    if apellido:
        query += ' AND apellidos ILIKE %s'
        params.append(f'%{apellido}%')
    if pasaporte:
        query += ' AND pasaporte ILIKE %s'
        params.append(f'%{pasaporte}%')
    
    query += ' ORDER BY apellidos, nombre'
    cursor.execute(query, params)
    pasajeros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/pasajeros.html', pasajeros=pasajeros)

@app.route('/admin/agregar_pasajero', methods=['POST'])
@login_required
@role_required('admin')
def agregar_pasajero():
    nombre = request.form['nombre']
    apellidos = request.form['apellidos']
    pasaporte = request.form['pasaporte']
    nacionalidad = request.form['nacionalidad']
    fecha_nacimiento = request.form['fecha_nacimiento'] if request.form['fecha_nacimiento'] else None
    correo = request.form['correo']
    telefono = request.form['telefono']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Pasajeros (nombre, apellidos, pasaporte, nacionalidad, fecha_nacimiento, correo, telefono)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (nombre, apellidos, pasaporte, nacionalidad, fecha_nacimiento, correo, telefono))
        conn.commit()
        
        log_operacion('ALTA', 'Pasajeros', pasaporte, f'Pasajero agregado: {nombre} {apellidos}')
        flash('Pasajero agregado exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_pasajeros'))

# ========== REPORTES Y CONSULTAS ESPECIALES ==========
@app.route('/reportes/vuelos_por_aerolinea')
@login_required
def reporte_vuelos_por_aerolinea():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cursor.execute('''
        SELECT a.nombre, a.codigo_iata, COUNT(v.id_vuelo) as total_vuelos,
               SUM(CASE WHEN v.estado = 'Programado' THEN 1 ELSE 0 END) as programados,
               SUM(CASE WHEN v.estado = 'Abordando' THEN 1 ELSE 0 END) as abordando,
               SUM(CASE WHEN v.estado = 'Despegado' THEN 1 ELSE 0 END) as despegados
        FROM Aerolineas a
        LEFT JOIN Vuelos v ON a.id_aerolinea = v.id_aerolinea
        GROUP BY a.id_aerolinea, a.nombre, a.codigo_iata
        ORDER BY total_vuelos DESC
    ''')
    reporte = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reportes/vuelos_por_aerolinea.html', reporte=reporte)

@app.route('/reportes/logs_detallados')
@login_required
@role_required('admin')
def reporte_logs_detallados():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    usuario = request.args.get('usuario', '')
    
    query = '''
        SELECT l.*, u.username 
        FROM Log_Operaciones l 
        LEFT JOIN Usuarios_Sistema u ON l.id_usuario = u.id_usuario 
        WHERE 1=1
    '''
    params = []
    
    if fecha_inicio:
        query += ' AND DATE(l.fecha_hora) >= %s'
        params.append(fecha_inicio)
    if fecha_fin:
        query += ' AND DATE(l.fecha_hora) <= %s'
        params.append(fecha_fin)
    if usuario:
        query += ' AND u.username ILIKE %s'
        params.append(f'%{usuario}%')
    
    query += ' ORDER BY l.fecha_hora DESC'
    cursor.execute(query, params)
    logs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('reportes/logs_detallados.html', logs=logs)

# ========== FUNCIÓN PARA OBTENER AEROLÍNEAS (usada en varios lugares) ==========
def obtener_aerolineas():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM Aerolineas ORDER BY nombre')
    aerolineas = cursor.fetchall()
    cursor.close()
    conn.close()
    return aerolineas

# Modificar la ruta responsable_vuelos para pasar aerolíneas
@app.route('/responsable/vuelos')
@login_required
@role_required('admin', 'responsable')
def responsable_vuelos():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Aplicar filtros
    estado = request.args.get('estado', '')
    fecha = request.args.get('fecha', '')
    origen = request.args.get('origen', '')
    destino = request.args.get('destino', '')
    
    query = '''
        SELECT v.*, a.nombre as aerolinea_nombre 
        FROM Vuelos v 
        LEFT JOIN Aerolineas a ON v.id_aerolinea = a.id_aerolinea 
        WHERE 1=1
    '''
    params = []
    
    if estado:
        query += ' AND v.estado = %s'
        params.append(estado)
    if fecha:
        query += ' AND DATE(v.fecha_salida) = %s'
        params.append(fecha)
    if origen:
        query += ' AND v.origen ILIKE %s'
        params.append(f'%{origen}%')
    if destino:
        query += ' AND v.destino ILIKE %s'
        params.append(f'%{destino}%')
    
    query += ' ORDER BY v.fecha_salida DESC'
    cursor.execute(query, params)
    vuelos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Obtener aerolíneas para los selects
    aerolineas = obtener_aerolineas()
    
    return render_template('responsable/vuelos.html', vuelos=vuelos, aerolineas=aerolineas)

# Modificar admin_aerolineas para soportar filtros
@app.route('/admin/aerolineas')
@login_required
@role_required('admin')
def admin_aerolineas():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Aplicar filtros
    nombre = request.args.get('nombre', '')
    pais = request.args.get('pais', '')
    codigo = request.args.get('codigo', '')
    
    query = 'SELECT * FROM Aerolineas WHERE 1=1'
    params = []
    
    if nombre:
        query += ' AND nombre ILIKE %s'
        params.append(f'%{nombre}%')
    if pais:
        query += ' AND pais_origen ILIKE %s'
        params.append(f'%{pais}%')
    if codigo:
        query += ' AND codigo_IATA ILIKE %s'
        params.append(f'%{codigo}%')
    
    query += ' ORDER BY id_aerolinea'
    cursor.execute(query, params)
    aerolineas = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/aerolineas.html', aerolineas=aerolineas)

# ========== CONSULTAS PARA USUARIO "CONSULTA" ==========
@app.route('/consulta/vuelos_hoy')
@login_required
def consulta_vuelos_hoy():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT v.*, a.nombre as aerolinea_nombre 
        FROM Vuelos v 
        LEFT JOIN Aerolineas a ON v.id_aerolinea = a.id_aerolinea 
        WHERE DATE(v.fecha_salida) = CURRENT_DATE
        ORDER BY v.fecha_salida
    ''')
    vuelos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('consulta/vuelos_hoy.html', vuelos=vuelos)

@app.route('/consulta/pasajeros')
@login_required
def consulta_pasajeros():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Aplicar filtros
    nombre = request.args.get('nombre', '')
    apellido = request.args.get('apellido', '')
    pasaporte = request.args.get('pasaporte', '')
    
    query = 'SELECT * FROM Pasajeros WHERE 1=1'
    params = []
    
    if nombre:
        query += ' AND nombre ILIKE %s'
        params.append(f'%{nombre}%')
    if apellido:
        query += ' AND apellidos ILIKE %s'
        params.append(f'%{apellido}%')
    if pasaporte:
        query += ' AND pasaporte ILIKE %s'
        params.append(f'%{pasaporte}%')
    
    query += ' ORDER BY apellidos, nombre'
    cursor.execute(query, params)
    pasajeros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('consulta/pasajeros.html', pasajeros=pasajeros)

# ========== FUNCIONES ADICIONALES ==========
@app.route('/admin/usuarios')
@login_required
@role_required('admin')
def admin_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT u.*, e.nombre as empleado_nombre 
        FROM Usuarios_Sistema u 
        LEFT JOIN Empleados e ON u.id_empleado = e.id_empleado 
        ORDER BY u.id_usuario
    ''')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/agregar_usuario', methods=['POST'])
@login_required
@role_required('admin')
def agregar_usuario():
    username = request.form['username']
    password = request.form['password']
    rol = request.form['rol']
    
    # En producción, usar bcrypt para hashear la contraseña
    # Para esta demo, usamos un hash fijo
    password_hash = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'  # admin123
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Usuarios_Sistema (username, password_hash, rol)
            VALUES (%s, %s, %s)
        ''', (username, password_hash, rol))
        conn.commit()
        
        log_operacion('ALTA', 'Usuarios_Sistema', username, f'Usuario creado: {username} ({rol})')
        flash('Usuario agregado exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_usuarios'))

# ========== PÁGINA DE INICIO MEJORADA ==========
@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Crear carpeta para reportes si no existe
    os.makedirs('templates/reportes', exist_ok=True)
    os.makedirs('templates/admin', exist_ok=True)
    
    print("="*60)
    print("🚀 SISTEMA AEROPORTUARIO COMPLETO")
    print("="*60)
    print("🌐 Accede en: http://localhost:5000")
    print("🔑 Usuarios de prueba:")
    print("   • admin / admin123       (Control total)")
    print("   • responsable / admin123 (Puede editar)")
    print("   • consulta / admin123    (Solo ver)")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)



# ========== ADMINISTRACIÓN DE PASAJEROS ==========
@app.route('/admin/pasajeros')
@login_required
@role_required('admin')
def admin_pasajeros():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    # Aplicar filtros si existen
    nombre = request.args.get('nombre', '')
    apellido = request.args.get('apellido', '')
    pasaporte = request.args.get('pasaporte', '')
    
    query = 'SELECT * FROM Pasajeros WHERE 1=1'
    params = []
    
    if nombre:
        query += ' AND nombre ILIKE %s'
        params.append(f'%{nombre}%')
    if apellido:
        query += ' AND apellidos ILIKE %s'
        params.append(f'%{apellido}%')
    if pasaporte:
        query += ' AND pasaporte ILIKE %s'
        params.append(f'%{pasaporte}%')
    
    query += ' ORDER BY apellidos, nombre'
    cursor.execute(query, params)
    pasajeros = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/pasajeros.html', pasajeros=pasajeros)


# ========== ADMINISTRACIÓN DE USUARIOS ==========
@app.route('/admin/usuarios')
@login_required
@role_required('admin')
def admin_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('''
        SELECT u.*, e.nombre as empleado_nombre 
        FROM Usuarios_Sistema u 
        LEFT JOIN Empleados e ON u.id_empleado = e.id_empleado 
        ORDER BY u.id_usuario
    ''')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/admin/agregar_usuario', methods=['POST'])
@login_required
@role_required('admin')
def agregar_usuario():
    username = request.form['username']
    password = request.form['password']
    rol = request.form['rol']
    
    # En producción, usar bcrypt para hashear la contraseña
    # Para esta demo, usamos un hash fijo
    password_hash = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'  # admin123
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Usuarios_Sistema (username, password_hash, rol)
            VALUES (%s, %s, %s)
        ''', (username, password_hash, rol))
        conn.commit()
        
        log_operacion('ALTA', 'Usuarios_Sistema', username, f'Usuario creado: {username} ({rol})')
        flash('Usuario agregado exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_usuarios'))
