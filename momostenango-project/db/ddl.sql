-- esquema de base de datos postgresql

-- Ciudadanos
CREATE TABLE citizens (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(150),
  identificacion VARCHAR(50), -- Ej: DPI o número de documento
  fecha_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Sesiones de chat
CREATE TABLE chat_sessions (
  id SERIAL PRIMARY KEY,
  citizen_id INT NOT NULL,
  fecha_inicio TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  fecha_fin TIMESTAMPTZ,
  contexto JSONB,
  FOREIGN KEY (citizen_id) REFERENCES citizens(id)
);

-- Consultas (mensajes de ciudadanos)
CREATE TABLE consultas (
  id SERIAL PRIMARY KEY,
  session_id INT NOT NULL,
  tipo_mensaje VARCHAR(10) NOT NULL CHECK (tipo_mensaje IN ('texto', 'imagen', 'pdf')),
  contenido TEXT NOT NULL, -- Texto o URL de archivo
  timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Respuestas del Agente
CREATE TABLE respuestas (
  id SERIAL PRIMARY KEY,
  consulta_id INT NOT NULL,
  contenido TEXT NOT NULL,
  modelo_usado VARCHAR(100), -- ej: 'gpt-4', 'llama-3'
  confianza NUMERIC(5,2), -- ej: 95.00 (%)
  timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (consulta_id) REFERENCES consultas(id)
);

CREATE TABLE archivos (
  id SERIAL PRIMARY KEY,
  consulta_id INT,
  tipo_archivo VARCHAR(10) not NULL,
  url_archivo TEXT,
  nombre_original VARCHAR(255),
  FOREIGN KEY (consulta_id) REFERENCES consultas(id)
);


CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE knowledge_embeddings (
    id SERIAL PRIMARY KEY,
    tipo TEXT NOT NULL,            -- 'FAQ' o 'REGLAMENTO'
    titulo TEXT,                   -- Opcional: título corto (ej. "Pago de IUSI", "Reglamento de basura")
    contenido TEXT NOT NULL,        -- Texto del fragmento que vamos a buscar
    embedding VECTOR(1536),         -- Vector del embedding (por ejemplo, 1536 para OpenAI models)
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Para control de cambios
);


-- FAQ sobre recolección de basura
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'FAQ',
    'Horarios de recolección de basura zona 3',
    'El camión de basura pasa por la zona 3 de Momostenango los miércoles y sábados a partir de las 7:00 AM.'
);

-- FAQ sobre reporte de baches
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'FAQ',
    'Reporte de baches y daños en calles',
    'Para reportar un bache o daño en la vía pública, debes enviar una fotografía y la ubicación exacta al WhatsApp municipal 1234-5678 o al correo reportes@momostenango.gob.gt.'
);

-- FAQ sobre acceso a formularios de trámites
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'FAQ',
    'Formulario de permiso de construcción',
    'El formulario de permiso de construcción está disponible en la página web municipal www.momostenango.gob.gt/tramites/construccion o en las oficinas de urbanismo.'
);

-- FAQ sobre impuesto vehicular
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'FAQ',
    'Costo del impuesto vehicular',
    'El costo del impuesto vehicular anual en Momostenango es de Q100 para motocicletas, Q300 para vehículos livianos y Q600 para vehículos pesados. El pago debe realizarse entre enero y marzo de cada año.'
);

-- FAQ sobre citas de identidad
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'FAQ',
    'Agendar cita para trámite de identidad',
    'Para agendar una cita de trámite de identidad debes ingresar al portal www.momostenango.gob.gt/citas, seleccionar el tipo de trámite y reservar fecha y hora disponible.'
);

-- Reglamento de basura
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'REGLAMENTO',
    'Reglamento de residuos sólidos',
    'Según el reglamento municipal, todo ciudadano es responsable de sacar su basura en bolsas cerradas el día que corresponde según su zona. El incumplimiento puede conllevar sanciones de hasta Q500.'
);

-- Reglamento de construcción
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'REGLAMENTO',
    'Normativa de construcción en zona urbana',
    'Todo proyecto de construcción en zona urbana de Momostenango debe contar con planos aprobados y permisos emitidos por la Dirección de Urbanismo. Edificaciones sin permisos pueden ser clausuradas.'
);

-- Reglamento de reportes de daños
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'REGLAMENTO',
    'Procedimiento de atención de baches y postes dañados',
    'La Municipalidad de Momostenango se compromete a atender reportes de baches y postes averiados en un plazo máximo de 15 días hábiles, una vez recibido el reporte ciudadano con evidencia.'
);

-- Reglamento de impuestos
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'REGLAMENTO',
    'Normativa de cobro de impuesto vehicular',
    'El impuesto vehicular es obligatorio para todos los vehículos registrados en Momostenango. El incumplimiento del pago puede generar multas de hasta Q150 adicionales por mora anual.'
);

-- Trámite de identidad
INSERT INTO knowledge_embeddings (tipo, titulo, contenido)
VALUES (
    'REGLAMENTO',
    'Requisitos para trámite de identidad',
    'Para tramitar la identidad personal es necesario presentar certificado de nacimiento, DPI anterior (si aplica), y realizar el pago correspondiente de Q50 en caja municipal.'
);
