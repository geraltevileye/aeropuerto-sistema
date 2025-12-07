-- Tabla 1: Aerolineas
CREATE TABLE Aerolineas (
    id_aerolinea SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo_IATA CHAR(2) UNIQUE NOT NULL,
    pais_origen VARCHAR(50),
    fecha_fundacion DATE
);

-- Tabla 2: Vuelos
CREATE TABLE Vuelos (
    id_vuelo VARCHAR(10) PRIMARY KEY,
    id_aerolinea INTEGER,
    origen VARCHAR(50) NOT NULL,
    destino VARCHAR(50) NOT NULL,
    fecha_salida TIMESTAMP NOT NULL,
    fecha_llegada TIMESTAMP NOT NULL,
    estado VARCHAR(20) CHECK (estado IN ('Programado', 'Abordando', 'Despegado', 'Aterrizado', 'Cancelado', 'Retrasado')),
    puerta_embarque VARCHAR(10),
    FOREIGN KEY (id_aerolinea) REFERENCES Aerolineas(id_aerolinea)
);

-- Tabla 3: Pasajeros
CREATE TABLE Pasajeros (
    id_pasajero SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    pasaporte VARCHAR(20) UNIQUE NOT NULL,
    nacionalidad VARCHAR(50),
    fecha_nacimiento DATE,
    correo VARCHAR(100),
    telefono VARCHAR(20)
);

-- Tabla 4: Empleados
CREATE TABLE Empleados (
    id_empleado SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    puesto VARCHAR(20) CHECK (puesto IN ('Piloto', 'Azafata', 'Controlador', 'Mantenimiento', 'Seguridad', 'Administrativo')),
    id_aerolinea INTEGER,
    fecha_contratacion DATE,
    FOREIGN KEY (id_aerolinea) REFERENCES Aerolineas(id_aerolinea)
);

-- Tabla 5: Reservas
CREATE TABLE Reservas (
    id_reserva SERIAL PRIMARY KEY,
    id_pasajero INTEGER,
    id_vuelo VARCHAR(10),
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    clase VARCHAR(20) CHECK (clase IN ('Economica', 'Ejecutiva', 'Primera')),
    asiento VARCHAR(5),
    precio NUMERIC(10,2),
    estado VARCHAR(20) CHECK (estado IN ('Confirmada', 'Cancelada', 'En espera')),
    FOREIGN KEY (id_pasajero) REFERENCES Pasajeros(id_pasajero),
    FOREIGN KEY (id_vuelo) REFERENCES Vuelos(id_vuelo)
);

-- Tabla 6: Equipaje
CREATE TABLE Equipaje (
    id_equipaje SERIAL PRIMARY KEY,
    id_pasajero INTEGER,
    id_vuelo VARCHAR(10),
    peso_kg NUMERIC(5,2),
    tipo VARCHAR(10) CHECK (tipo IN ('Mano', 'Bodega')),
    etiqueta VARCHAR(20) UNIQUE,
    FOREIGN KEY (id_pasajero) REFERENCES Pasajeros(id_pasajero),
    FOREIGN KEY (id_vuelo) REFERENCES Vuelos(id_vuelo)
);

-- Tabla 7: Usuarios_Sistema
CREATE TABLE Usuarios_Sistema (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) CHECK (rol IN ('admin', 'responsable', 'consulta')) NOT NULL,
    id_empleado INTEGER NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_empleado) REFERENCES Empleados(id_empleado)
);

-- Tabla 8: Log_Operaciones
CREATE TABLE Log_Operaciones (
    id_log SERIAL PRIMARY KEY,
    id_usuario INTEGER,
    operacion VARCHAR(50) NOT NULL,
    tabla_afectada VARCHAR(50),
    id_registro_afectado VARCHAR(100),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalles TEXT,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios_Sistema(id_usuario)
);