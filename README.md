# Legacy Escape — nivel tecnólogo

## Descripción

La solución moderniza Afiliaciones y Retiros de una caja de compensación mediante una API estable, sin sustituir de golpe su sistema antiguo. Portal, Subsidios y un consumidor móvil consultan o escriben por HTTP; Educación conserva su funcionamiento. Los retiros usan comprobantes transaccionales para reconocer reintentos y una cola persistente para recuperarse después de caídas.

Repositorio: [juaness1282/hackaton-fesc](https://github.com/juaness1282/hackaton-fesc). La procedencia de la reconstrucción está documentada en [docs/procedencia.md](docs/procedencia.md).

## Integrantes

- Juan Esteban Mantilla Vega

## Requisitos

- Docker con motor Linux y Docker Compose.
- Git para descargar el repositorio.
- Bash para los scripts y ejemplos, incluido Git Bash en Windows.
- curl para las consultas de ejemplo.
- Python 3.8 o superior en el host para los validadores y scripts de eventos. El gateway y las pruebas de integración usan Python 3.12 dentro de contenedores.
- Puertos 8082, 8090, 8091, 8092 y 8093 disponibles.

## Instalación y ejecución

Desde una carpeta de trabajo, ejecutar:

```bash
git clone https://github.com/juaness1282/hackaton-fesc.git
cd hackaton-fesc
cp .env.example .env
```

Editar .env antes del arranque: sustituir POSTGRES_PASSWORD y los tres tokens por valores propios y distintos. Mantener el archivo fuera de Git. Los demás valores del ejemplo permiten la comunicación entre contenedores.

```bash
docker compose up -d --build
docker compose ps
curl http://localhost:8082/health
```

La salud debe responder con status UP y legacy UP. Si la base aún está inicializándose, esperar y repetir la consulta. En un volumen nuevo se instalan automáticamente esquema, datos sintéticos, procedimiento y tabla de comprobantes.

Si se reutiliza un volumen creado con una versión del kit que no incluía comprobantes, aplicar la migración aditiva antes de registrar retiros:

```bash
docker compose exec -T legacy-db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/init/04_receipts.sql
```

Para detener y volver a iniciar conservando datos:

```bash
docker compose stop
docker compose up -d
```

Para revertir Afiliaciones:

```bash
./rollback.sh affiliations
```

El rollback mantiene datos y solicitudes pendientes. Para volver a DUAL:

```bash
docker compose run --rm --no-deps gateway python migration.py DUAL
```

reset.sh y docker compose down -v borran volúmenes; no forman parte de la reversión de un dominio.

## Configuración

| Variable de .env.example | Propósito | Ejemplo |
|---|---|---|
| POSTGRES_DB | Base de datos utilizada por las aplicaciones | legacy |
| POSTGRES_USER | Usuario de PostgreSQL | legacy |
| POSTGRES_PASSWORD | Contraseña de PostgreSQL leída del entorno | cambiar-esta-clave |
| LEGACY_DB_HOST | Nombre interno del servicio de base | legacy-db |
| LEGACY_DB_PORT | Puerto interno de PostgreSQL | 5432 |
| GATEWAY_URL | URL interna utilizada por los consumidores HTTP | http://gateway:8082 |
| PORTAL_TOKEN | Credencial de Portal | cambiar-portal |
| SUBSIDIOS_TOKEN | Credencial de Subsidios | cambiar-subsidios |
| MOBILE_TOKEN | Credencial del consumidor móvil de solo lectura | cambiar-mobile |

Los ejemplos cambiar-... son marcadores, no credenciales de producción. Al modificar .env, recrear los contenedores afectados mediante docker compose up -d.

Compose establece STATE_DIR=/state dentro de gateway. SUBSIDIOS_MODE es opcional y solo actúa si no existe /state/domains.json; ese control persistente tiene prioridad. EDUCACION_PORT, PORTAL_PORT y SUBSIDIOS_PORT permiten cambiar los puertos publicados de esos consumidores; sus valores predeterminados son 8090, 8092 y 8091. El contrato del gateway conserva el puerto 8082.

## Arquitectura

| Servicio de Compose | Responsabilidad |
|---|---|
| legacy-db | Conserva la fuente de datos y los procedimientos originales en PostgreSQL |
| educacion-app | Consulta directamente como antes; código del kit sin modificaciones |
| portal-client | Construye la ficha mediante HTTP al gateway; código del kit sin modificaciones |
| subsidios-app | Registra por gateway en DUAL/MODERN y por el camino original en LEGACY |
| gateway | Expone el contrato, autentica, audita, adapta datos y recupera retiros pendientes |
| mobile-client | Interfaz web adaptable a teléfonos y proxy de solo lectura; conserva el token en el servidor |
| tests | Pruebas de integración activadas exclusivamente con el perfil test |

gateway-state conserva la cola SQLite y el estado administrativo; legacy-db-data conserva datos y comprobantes PostgreSQL. El adapter está en src/db_adapter.py. Entre los consumidores nuevos, el móvil solo se comunica por HTTP y no recibe configuración de PostgreSQL.

## Uso

Gateway y documentación interactiva: [localhost:8082/docs](http://localhost:8082/docs).
Consumidor móvil: [localhost:8093](http://localhost:8093).
Ejemplo de documento sintético: 1019886173; empresa: 2015.

Los siguientes ejemplos se ejecutan en Bash desde la raíz del repositorio. Cargar las variables del archivo local:

```bash
set -a
. ./.env
set +a
```

| Ruta requerida | Finalidad |
|---|---|
| GET /health | Disponibilidad del gateway y del legacy; sin autenticación obligatoria |
| GET /api/v1/members/{document} | Documento, nombre completo, estado y empresa |
| GET /api/v1/members/{document}/beneficiaries | Beneficiarios y parentescos |
| GET /api/v1/companies/{id} | Empresa y cantidad de afiliados activos |
| POST /api/v1/members/{document}/retirements | Retiro identificado por requestId |
| GET /api/v1/migration/status | Estado de los dominios |

```bash
curl http://localhost:8082/health
curl -H "Authorization: Bearer $PORTAL_TOKEN" http://localhost:8082/api/v1/members/1019886173
curl -H "Authorization: Bearer $PORTAL_TOKEN" http://localhost:8082/api/v1/members/1019886173/beneficiaries
curl -H "Authorization: Bearer $PORTAL_TOKEN" http://localhost:8082/api/v1/companies/2015
curl -H "Authorization: Bearer $PORTAL_TOKEN" http://localhost:8082/api/v1/migration/status
curl -X POST -H "Authorization: Bearer $SUBSIDIOS_TOKEN" -H "Content-Type: application/json" -d '{"requestId":"demo-retiro-1","date":"2026-10-15","reason":"Retiro de demostración"}' http://localhost:8082/api/v1/members/1019886173/retirements
```

Un retiro confirmado inicialmente devuelve 201, movement y status completed. Repetir el mismo contenido y requestId devuelve 200; reutilizarlo con otros datos devuelve 409. MOBILE_TOKEN permite consultas y recibe 403 al intentar un retiro.

Si PostgreSQL está caído, las consultas que dependen de él devuelven 503 con LEGACY_UNAVAILABLE en menos de tres segundos. Un retiro persistido puede responder 202 con status pending y movement null. Consultar el resultado posterior:

```bash
curl -H "Authorization: Bearer $SUBSIDIOS_TOKEN" http://localhost:8082/api/v1/retirement-requests/demo-retiro-1
```

La solicitud termina en completed, not_found o conflict según su aplicación al recuperar el legacy. No cambiar requestId al reintentar una misma operación.

Subsidios conserva POST :8091/retiros con documento, fecha y motivo; permite requestId o Idempotency-Key. Sin identificador suministrado, cada petición se considera nueva:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"documento":"1019886173","fecha":"2026-10-15","motivo":"Retiro desde Subsidios","requestId":"demo-subsidios-1"}' http://localhost:8091/retiros
```

## Pruebas

Con los servicios en funcionamiento, ejecutar:

```bash
docker compose --profile test run --rm tests
```

El servicio genera test-results/contract.xml con quince casos de integración contra PostgreSQL real. Comprueba consultas, activeMembers, permisos, errores, retiros, repetición, concurrencia, Subsidios, Educación, Portal y móvil. Modifica datos sintéticos y termina con error si falla una prueba.

Para los cinco controles de eventos desde el host:

```bash
python3 scripts/verify-events.py
```

El script aplica el cambio de esquema, detiene y recupera PostgreSQL, reinicia gateway y comprueba rollback con gateway apagado. Deja test-results/events.json, conserva el esquema renombrado y restaura DUAL al finalizar.

Revisiones públicas del kit, con UTF-8 para incluir el proceso hijo del revisor en Windows:

```bash
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 validator check
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 validator entregables
```

Si la instalación del host proporciona python en lugar de python3, usar ese ejecutable. No se necesitan dependencias Python del gateway en el host para estas revisiones. Las fechas y resultados ejecutados están en docs/verification.md.

## Documentación

- [Arquitectura](docs/architecture.md)
- [Dependencias](docs/dependency-map.md)
- [Migración](docs/migration-plan.md)
- [OpenAPI](openapi.yaml)
- [Uso de IA](AI_USAGE.md)
- [Procedencia](docs/procedencia.md)
- [Verificación](docs/verification.md)
- [Auditoría de requisitos](docs/auditoria-requisitos.md)
- [Guion y entrega del pitch](docs/pitch.md)

## Qué resolvimos

Se construyó una API con modelo canónico y acceso al esquema encapsulado en el adapter. Subsidios registra por HTTP y los retiros incluyen comprobantes transaccionales para reconocer reintentos. La cola persistente independiente del legacy conserva solicitudes durante caídas y reinicios. El rollback mantiene el procedimiento original disponible y el móvil consume las consultas existentes. Pasaron quince pruebas de integración, los cinco controles de eventos y un arranque con volúmenes vacíos.

## Limitaciones y pendientes

La auditoría de implementación documenta dos comportamientos: consumer unknown en algunas líneas y respuestas detail en rutas inexistentes. Su alcance se describe en docs/auditoria-requisitos.md.

El móvil es una web adaptable; la persistencia local no ofrece alta disponibilidad. En LEGACY, el procedimiento original conserva su falta de idempotencia. Las pruebas de carga no forman parte de esta entrega.
