# Catálogo de códigos postales de México

`sepomex.sqlite3` contiene 158 864 asentamientos, 31 878 códigos postales y las
32 entidades federativas. Solo se abre en modo lectura. No contiene información
de usuarios y no forma parte de PostgreSQL.

Fuente original: Servicio Postal Mexicano (SEPOMEX),
https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx

El catálogo oficial se proporciona gratuitamente y no está permitida su
comercialización total ni parcial. La integración en TalentLink es una consulta
gratuita para completar domicilios.

Copia de distribución utilizada: IcaliaLabs/sepomex, `lib/sepomex_db.csv`, revisión
`3899c9e68c5ab46a9a789911d298833254a88b26` (última modificación del archivo:
23 de julio de 2026; esta fecha corresponde a la copia, no a una garantía de
actualización del catálogo oficial).

https://github.com/IcaliaLabs/sepomex/blob/3899c9e68c5ab46a9a789911d298833254a88b26/lib/sepomex_db.csv

SHA-256 del CSV de origen:
`3411a0be5e11c3613f16939ea85707901c2d66e4031914e4ca42bd146993dfee`

Para actualizar, descarga el TXT nacional oficial y ejecuta:

```bash
python maintenance/import_postal_catalog.py /ruta/CPdescarga.txt --encoding cp1252
```

La copia CSV utilizada inicialmente está en UTF-8 (sin cabecera): usa
`--encoding utf-8` al reconstruir a partir de esa copia. El importador valida
el tamaño, las 32 entidades, la codificación y la integridad del archivo antes
de reemplazar el catálogo anterior. No modifica PostgreSQL.

En zonas rurales, SEPOMEX puede no indicar una ciudad: se mantiene ese campo
vacío. Municipio y colonia son datos distintos. Un mismo C.P. puede tener
varios asentamientos; el usuario debe seleccionar el suyo.
