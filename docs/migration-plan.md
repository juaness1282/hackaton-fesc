# Migración gradual

| Dominio | Estado | Criterio para avanzar | Rollback |
|---|---|---|---|
| Afiliaciones | DUAL | 100 consultas equivalentes y 7 días sin diferencias | ./rollback.sh affiliations |
| Retiros | DUAL | 100 reintentos sin duplicados y 0 retiros aceptados perdidos durante 7 días | ./rollback.sh affiliations; Subsidios vuelve al procedimiento original |
| Empresas | LEGACY | 100 conteos correctos durante 7 días | Mantener la fuente legacy y restaurar la versión anterior del adapter |

Siguiente dominio: Empresas

DUAL significa coexistencia de consumidores antiguos y API sobre una misma fuente; no significa dos bases ni doble escritura. Los plazos son criterios futuros para promoción, no resultados históricos.

La administración se realiza con docker compose run --rm --no-deps gateway python migration.py DUAL (o MODERN después de validar los criterios). El rollback ejecuta esa administración en LEGACY, persiste el control en gateway-state y actualiza esta tabla. No existe endpoint público para cambiar estados.

Subsidios lee el estado compartido y registra directamente con el procedimiento original en LEGACY. Esto funciona aun si gateway está apagado. Los pendientes aceptados no se borran; se recuperan al volver gateway y PostgreSQL. El procedimiento original conserva su falta de idempotencia.
