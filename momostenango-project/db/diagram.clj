
Table "citizens" {
  "id" SERIAL [pk, increment]
  "nombre" VARCHAR(100) [not null]
  "email" VARCHAR(150)
  "identificacion" VARCHAR(50)
  "fecha_registro" TIMESTAMPTZ [default: `CURRENT_TIMESTAMP`]
}

Table "chat_sessions" {
  "id" SERIAL [pk, increment]
  "citizen_id" INT [not null]
  "fecha_inicio" TIMESTAMPTZ [default: `CURRENT_TIMESTAMP`]
  "fecha_fin" TIMESTAMPTZ
  "contexto" JSONB
}

Table "consultas" {
  "id" SERIAL [pk, increment]
  "session_id" INT [not null]
  "tipo_mensaje" VARCHAR(10) [not null]
  "contenido" TEXT [not null]
  "timestamp" TIMESTAMPTZ [default: `CURRENT_TIMESTAMP`]
}

Table "respuestas" {
  "id" SERIAL [pk, increment]
  "consulta_id" INT [not null]
  "contenido" TEXT [not null]
  "modelo_usado" VARCHAR(100)
  "confianza" NUMERIC(5,2)
  "timestamp" TIMESTAMPTZ [default: `CURRENT_TIMESTAMP`]
}

Table "archivos" {
  "id" SERIAL [pk, increment]
  "consulta_id" INT
  "tipo_archivo" ENUM('imagen','pdf')
  "url_archivo" TEXT
  "nombre_original" VARCHAR(255)
}

Ref:"citizens"."id" < "chat_sessions"."citizen_id"

Ref:"chat_sessions"."id" < "consultas"."session_id"

Ref:"consultas"."id" < "respuestas"."consulta_id"

Ref:"consultas"."id" < "archivos"."consulta_id"
