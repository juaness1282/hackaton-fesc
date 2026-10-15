# Legacy Escape — reconstrucción del nivel tecnólogo

## Descripción

La solución permite modernizar Afiliaciones y Retiros de una caja de compensación sin sustituir de golpe su sistema antiguo. Un gateway expone datos canónicos y escrituras idempotentes. Los retiros aceptados durante caídas se guardan de forma persistente y se recuperan cuando vuelve la base. La reconstrucción y sus commits se describen en docs/procedencia.md.

## Integrantes

- Juan Esteban Mantilla Vega

## Requisitos

Docker con motor Linux y Docker Compose. Python 3.8 o superior para los validadores. Bash para los scripts, también mediante Git Bash en Windows. El gateway usa Python 3.12 dentro de su imagen.

## Instalación y ejecución

Desde una copia limpia ejecutar cp .env.example .env y cambiar la contraseña y los tres tokens por valores propios. Después ejecutar docker compose up -d --build. Esperar hasta que GET /health indique legacy UP. La primera inicialización carga el esquema, datos sintéticos y comprobantes automáticamente.

Para revertir ejecutar ./rollback.sh affiliations. No borrar volúmenes: son la fuente de datos y la cola. Para reanudar DUAL ejecutar docker compose run --rm --no-deps gateway python migration.py DUAL. reset.sh es destructivo y solo sirve para restablecer el kit de pruebas.

## Configuración

| Variable | Propósito | Ejemplo |
|---|---|---|
| POSTGRES_DB | Nombre de base | legacy |
| POSTGRES_USER | Usuario de base | legacy |
| POSTGRES_PASSWORD | Contraseña de base leída del entorno | cambiar-esta-clave |
| LEGACY_DB_HOST | Nombre del servicio de base | legacy-db |
| LEGACY_DB_PORT | Puerto interno de PostgreSQL | 5432 |
| GATEWAY_URL | URL interna del gateway | http://gateway:8082 |
| PORTAL_TOKEN | Credencial de Portal | cambiar-portal |
| SUBSIDIOS_TOKEN | Credencial de Subsidios | cambiar-subsidios |
| MOBILE_TOKEN | Credencial móvil de solo lectura | cambiar-mobile |

STATE_DIR=/state se establece dentro de Compose, no requiere configuración del usuario. SUBSIDIOS_MODE solo actúa si no existe el control persistente; después del rollback manda el archivo domains.json. Los secretos se conservan en .env, excluido de Git.

## Arquitectura

legacy-db conserva datos y procedimientos. educacion-app permanece sin cambios y lee la base. portal-client consume HTTP. subsidios-app utiliza gateway en DUAL y el procedimiento original en LEGACY. mobile-client ofrece consultas en una web adaptable a teléfonos sin exponer tokens al navegador. gateway reúne adapter, autenticación, auditoría y cola. tests comprueba la integración en su perfil independiente.

## Uso

Gateway: http://localhost:8082. Interfaz móvil: http://localhost:8093. Para datos protegidos usar Authorization: Bearer con el token correspondiente.

| Ruta | Ejemplo |
|---|---|
| GET /health | Consultar disponibilidad sin token |
| GET /api/v1/members/{document} | Documento 1019886173 |
| GET /api/v1/members/{document}/beneficiaries | Beneficiarios de 1019886173 |
| GET /api/v1/companies/{id} | Empresa 2015 |
| POST /api/v1/members/{document}/retirements | Cuerpo mostrado debajo |
| GET /api/v1/migration/status | Estado por dominio |

Ejemplo de retiro: {"requestId":"mi-retiro-1","date":"2026-10-14","reason":"Retiro voluntario"}. Primera confirmación: 201; repetición: 200; identificador con otros datos: 409. Con la base caída, una solicitud persistida responde 202. GET /api/v1/retirement-requests/{request_id} devuelve pending, completed, not_found o conflict.

Subsidios conserva POST :8091/retiros con documento, fecha y motivo. Se puede incluir requestId o Idempotency-Key para reutilizarlo en reintentos. Sin identificador suministrado, cada petición se considera nueva. Las consultas dependientes de una base no disponible responden 503 con LEGACY_UNAVAILABLE en menos de tres segundos.

## Pruebas

Ejecutar docker compose --profile test run --rm tests con el entorno levantado. El servicio verifica consultas, conteos contra PostgreSQL, permisos, errores, retiros, concurrencia, Subsidios, Educación, Portal y móvil; genera test-results/contract.xml con quince casos. Modifica exclusivamente datos sintéticos del kit.

El script python3 scripts/verify-events.py ejecuta eventos de esquema, caída y rollback contra Docker desde el host; deja test-results/events.json. Requiere el entorno de pruebas, Bash, Docker y .env. No montar el socket Docker dentro de contenedores.

## Documentación

- [Arquitectura](docs/architecture.md)
- [Dependencias](docs/dependency-map.md)
- [Migración](docs/migration-plan.md)
- [OpenAPI](openapi.yaml)
- [Uso de IA](AI_USAGE.md)
- [Procedencia](docs/procedencia.md)
- [Verificación](docs/verification.md)

## Qué resolvimos

Se construyó un gateway nuevo desde el kit original, encapsulando las consultas y el procedimiento en un adapter. Se añadió autenticación por consumidor y auditoría enmascarada. Subsidios usa HTTP y los retiros incluyen comprobantes transaccionales. La cola independiente de PostgreSQL permite recuperación después de reinicios; el modo administrativo permite volver al camino original.

## Limitaciones y pendientes

El móvil es una web adaptable, no un paquete nativo Android o iOS. No se dispone de pruebas ocultas del comité. No se hicieron pruebas de carga ni se afirma alta disponibilidad. La operación en LEGACY conserva las limitaciones originales del procedimiento. Faltan revisión humana del código, registro del repositorio y pitch del evento.
