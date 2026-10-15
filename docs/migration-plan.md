# Plan de migración gradual

## Dominios y estado

| Dominio | Estado | Criterio para avanzar | Rollback |
|---|---|---|---|
| Afiliaciones | DUAL | 100 consultas equivalentes entre gateway y fuente, y 7 días sin diferencias antes de promover a MODERN | ./rollback.sh affiliations; conserva Educación y selecciona el recorrido original de Subsidios |
| Retiros | DUAL | 100 reintentos sin duplicados y 0 retiros aceptados perdidos durante 7 días | ./rollback.sh affiliations; conserva cola y comprobantes y selecciona el procedimiento original |
| Empresas | LEGACY | 100 conteos equivalentes y 7 días sin diferencias antes de iniciar la siguiente migración | Mantener la fuente legacy y volver al despliegue anterior del adapter |

Siguiente dominio: Empresas

Los plazos y cantidades de la tabla son criterios de promoción pendientes de cumplir, no resultados de pruebas ya acumulados. Empresas continúa en LEGACY aunque sus consultas estén expuestas por la API.

## Significado de los estados

- LEGACY: se conserva el recorrido original. En Afiliaciones/Retiros, Subsidios llama al procedimiento directamente.
- DUAL: coexisten consumidores antiguos y consumidores HTTP sobre la misma fuente. No hay doble escritura en dos bases.
- MODERN: selección administrativa del recorrido nuevo para Subsidios. La implementación mantiene disponibles PostgreSQL y los consumidores antiguos; este estado no sustituye la fuente de datos ni ejecuta una migración física.

En esta implementación Afiliaciones y Retiros cambian juntos. La administración no verifica automáticamente los criterios de promoción: quien opera el comando debe comprobar sus evidencias antes de promover. Los criterios de Empresas describen la siguiente etapa; no existe un comando de promoción independiente para ese dominio.

## Comprobar el estado

Con las variables de .env cargadas en Bash:

```bash
curl -H "Authorization: Bearer $PORTAL_TOKEN" http://localhost:8082/api/v1/migration/status
```

La respuesta incluye affiliations, retirements y companies. Al terminar las pruebas registradas, los dos primeros quedaron en DUAL y companies en LEGACY.

## Reversión

```bash
./rollback.sh affiliations
```

El script debe terminar con código 0 en menos de tres minutos. Su contenedor temporal escribe LEGACY en el control persistente aunque gateway esté detenido. Cuando la API está disponible, migration/status debe mostrar affiliations y retirements en LEGACY.

Subsidios lee domains.json en cada petición y vuelve al procedimiento original. Su ruta pública POST :8091/retiros se conserva. El procedimiento registra el cambio en la fuente y continúa visible para Educación.

Si gateway está apagado, su endpoint de estado no responderá; el control persiste y puede consultarse al reiniciar gateway. La prueba de reversión registró un retiro desde Subsidios con el gateway apagado.

El rollback no borra volúmenes, no revierte el evento de esquema y no elimina solicitudes aceptadas. Los pendientes conservados se recuperan al volver gateway y PostgreSQL. El recorrido original conserva su falta de idempotencia.

## Reanudar o promover

Para reanudar DUAL:

```bash
docker compose run --rm --no-deps gateway python migration.py DUAL
```

Después de comprobar los criterios de promoción, seleccionar MODERN:

```bash
docker compose run --rm --no-deps gateway python migration.py MODERN
```

Los comandos escriben domains.json en gateway-state y actualizan la tabla de este documento mediante el montaje de docs. El cambio de modo solo se realiza por administración local, sin endpoint público.
