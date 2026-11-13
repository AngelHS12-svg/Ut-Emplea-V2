-- Ejecutar antes de iniciar la versión que permite rangos salariales.
-- Conserva todos los importes fijos y las vacantes sin salario.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';
ALTER TABLE vacantes ADD COLUMN IF NOT EXISTS salario_max NUMERIC(10,2);
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'vacantes_salario_rango_check'
                   AND conrelid = 'vacantes'::regclass) THEN
        ALTER TABLE vacantes ADD CONSTRAINT vacantes_salario_rango_check
            CHECK (salario_max IS NULL OR (salario IS NOT NULL AND salario_max > salario));
    END IF;
END $$;
COMMIT;
