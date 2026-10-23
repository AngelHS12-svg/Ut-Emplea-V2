-- Aditiva e idempotente: no modifica ni elimina los registros existentes.
-- Ejecutar antes de iniciar los contenedores web con esta versión.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';
ALTER TABLE candidatos
    ADD COLUMN IF NOT EXISTS formacion_academica JSONB,
    ADD COLUMN IF NOT EXISTS estado VARCHAR(150),
    ADD COLUMN IF NOT EXISTS municipio VARCHAR(150),
    ADD COLUMN IF NOT EXISTS ciudad VARCHAR(150),
    ADD COLUMN IF NOT EXISTS colonia VARCHAR(150);
ALTER TABLE direcciones_empresa
    ADD COLUMN IF NOT EXISTS municipio VARCHAR(150);
COMMIT;
