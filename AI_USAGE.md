# Registro detallado del uso de inteligencia artificial

## Alcance y procedencia

La reconstrucción fue solicitada por Juan Esteban Mantilla Vega y ejecutada con asistencia de Codex en una carpeta nueva, partiendo del kit original. Existía una solución previa en otra carpeta; su código y su historial no se importaron. Los diez commits asociados registran los bloques de esta reconstrucción con sus fechas reales.

**Los prompts de este documento son resúmenes ampliados y reconstruidos a posteriori del encargo, las decisiones y las acciones observadas en esta conversación. No son transcripciones literales ni diez mensajes independientes que el participante haya enviado al asistente.** Se separan por commit para facilitar la trazabilidad técnica.

Se mantienen los cinco campos exigidos por el reglamento. En «Qué modificó o corrigió el equipo» se identifica expresamente al asistente cuando fue quien hizo la corrección. No se atribuyen revisiones o modificaciones humanas que no estén verificadas. Una intervención puede extenderse a varios commits; la asociación siguiente indica dónde quedó incorporado su resultado principal.

## Uso 1
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Preparar una reconstrucción independiente a partir del kit suministrado por la universidad, conservando la solución anterior y separando su historial del repositorio nuevo.
- Prompt principal (resumido): Resumen reconstruido: Reconstruir el reto de nivel tecnólogo en una carpeta nueva a partir del kit original. Conservar intacta la solución anterior, inicializar un repositorio independiente con la identidad confirmada del participante y excluir credenciales, archivos temporales y registros. Documentar que existe una implementación previa y que los commits nuevos corresponden a esta reconstrucción, sin importar ni alterar su historial.
- Qué produjo: La carpeta fesc-tecnologo-nuevo, un repositorio Git en main, origin apuntando al repositorio proporcionado, .gitignore, .gitattributes y docs/procedencia.md. El primer commit contiene el kit y esa declaración de procedencia.
- Qué modificó o corrigió el equipo: El asistente separó el repositorio nuevo del repositorio padre y dejó .env fuera de Git; las credenciales se generaron después de registrar el kit. Esta preparación no se presenta como una contribución humana verificada.
- Commit relacionado: `d8a08ea` — Importa el kit original y registra la procedencia de la reconstrucción.
- Comprobación realizada: Se comprobó la creación del repositorio independiente y el estado de Git; posteriormente se revisaron los diez commits para confirmar que .env y los valores reales de las credenciales no aparecieran en el historial.

## Uso 2
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Crear el servicio HTTP inicial y comprobar que pudiera conectarse a una base de datos nueva sin reutilizar los volúmenes del proyecto anterior.
- Prompt principal (resumido): Resumen reconstruido: Construir el gateway mínimo en Python y ejecutarlo en el puerto obligatorio 8082 mediante Docker Compose. Añadir GET /health para distinguir la disponibilidad del gateway de la disponibilidad del legacy, leer la conexión desde variables de entorno y mantener el nombre legacy-db. Usar un proyecto Compose independiente y liberar los puertos deteniendo los contenedores anteriores, conservando sus volúmenes y archivos.
- Qué produjo: src/Dockerfile, src/requirements.txt, src/server.py, la conexión inicial en src/db_adapter.py y el servicio gateway en docker-compose.yml. El despliegue nuevo usa el nombre legacy-escape-rebuild.
- Qué modificó o corrigió el equipo: El asistente distinguió entre un contenedor iniciado y una base realmente disponible: la primera consulta de salud mostró legacy DOWN y después se comprobó legacy UP mediante una conexión SQL real. No se borraron los volúmenes anteriores.
- Commit relacionado: `d49dcdc` — Configura el gateway Docker y verifica su salud con PostgreSQL.
- Comprobación realizada: docker compose config --quiet, construcción y arranque de los servicios, GET /health y SELECT 1 dentro del gateway.

## Uso 3
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Exponer afiliados, beneficiarios y empresas mediante HTTP sin que Portal ni los futuros consumidores conozcan las tablas o códigos del legacy.
- Prompt principal (resumido): Resumen reconstruido: Implementar las tres consultas de datos obligatorias del contrato. Concentrar en un adapter las tablas, columnas, códigos de estado y parentesco; traducirlos al modelo canónico, unir correctamente los nombres y calcular activeMembers. Mantener parametrizados los valores SQL y contemplar tanto el esquema original como el renombrado. Verificar las respuestas con datos sintéticos reales y comprobar Portal sin modificar su código.
- Qué produjo: Las funciones de consulta en src/db_adapter.py y las rutas de afiliados, beneficiarios y empresas en src/server.py. El adapter detecta la tabla renombrada y convierte los estados y parentescos a sus representaciones canónicas.
- Qué modificó o corrigió el equipo: El asistente encapsuló los identificadores físicos y seleccionó nombres de tabla y columna desde opciones internas permitidas, mientras mantuvo los datos recibidos como parámetros SQL. Los modelos Pydantic explícitos se incorporaron posteriormente al cerrar el contrato.
- Commit relacionado: `10447fe` — Implementa el adapter y las consultas canónicas de afiliación.
- Comprobación realizada: Se consultaron las tres rutas y se comprobó que Portal devolviera la ficha de MONICA PABON MENDOZA desde la nueva API.

## Uso 4
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Identificar Portal, Subsidios y Móvil mediante sus tokens y limitar al consumidor móvil a operaciones de lectura.
- Prompt principal (resumido): Resumen reconstruido: Añadir autenticación Authorization: Bearer a las rutas protegidas usando PORTAL_TOKEN, SUBSIDIOS_TOKEN y MOBILE_TOKEN desde el entorno. Asociar cada token a su consumidor, devolver 401 cuando falte o sea inválido y preparar la restricción 403 para escrituras móviles. Incluir el esquema de seguridad en OpenAPI, evitar credenciales dentro del código y comprobar el acceso solo cuando el gateway ya esté listo.
- Qué produjo: src/access.py, el esquema HTTPBearer, la comparación de credenciales con hmac.compare_digest y las dependencias de autenticación en las consultas.
- Qué modificó o corrigió el equipo: El asistente repitió la comprobación después de que una petición inmediatamente posterior al reinicio encontrara la conexión cerrada. Se esperó la disponibilidad real de la API antes de registrar como válida la autenticación, sin alterar las fechas del commit.
- Commit relacionado: `69d2947` — Añade autenticación Bearer y permisos por consumidor.
- Comprobación realizada: Sin token se obtuvo 401; con los tokens de Portal y Móvil se obtuvo 200. La prohibición de retiros móviles se comprobó cuando se implementó la escritura en el uso 6.

## Uso 5
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Evitar que los errores de las operaciones expongan SQL o trazas y dejar evidencia estructurada de las peticiones al gateway.
- Prompt principal (resumido): Resumen reconstruido: Crear una capa transversal de manejo de errores y auditoría. Devolver message y error_id en errores de aplicación, y 503 con LEGACY_UNAVAILABLE ante fallas de PostgreSQL. Registrar por petición timestamp, consumer, endpoint, status y latency_ms en logs/audit.log. Enmascarar los identificadores en las rutas y comprobar tanto el formato JSON del registro como la ausencia del documento sin enmascarar.
- Qué produjo: src/observability.py, sus manejadores de errores y el middleware de auditoría. Los registros se escriben como líneas JSON y las rutas de afiliados y seguimiento de solicitudes ocultan su identificador.
- Qué modificó o corrigió el equipo: El asistente enmascaró el segmento del identificador antes de escribir el endpoint y sustituyó detalles internos por mensajes controlados. Una auditoría posterior detectó dos casos aún pendientes: consumer unknown y errores estándar del router; no se presentan como resueltos.
- Commit relacionado: `cfba589` — Controla los errores y audita peticiones con documentos enmascarados.
- Comprobación realizada: Se comprobó el formato de un error 401 y los cinco campos de la auditoría. La revisión pública pasó G12, aunque no cubre completamente los dos desajustes posteriores.

## Uso 6
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Registrar retiros visibles en el legacy y reconocer repeticiones de una misma solicitud sin ejecutar dos veces el procedimiento.
- Prompt principal (resumido): Resumen reconstruido: Implementar POST /api/v1/members/{document}/retirements con requestId, date y reason validados. Confirmar el procedimiento de retiro y su comprobante en la misma transacción PostgreSQL. Proteger solicitudes concurrentes con el mismo identificador, devolver 201 la primera vez y 200 al repetir el mismo contenido, y rechazar con 409 la reutilización con otros datos. Mantener 404 para afiliados inexistentes y 403 para el token móvil.
- Qué produjo: db/init/04_receipts.sql, retirement_receipts, la operación save_retirement del adapter y la ruta POST con validación Pydantic. Se utilizó un bloqueo transaccional por requestId y una clave primaria para el comprobante.
- Qué modificó o corrigió el equipo: El asistente evitó usar únicamente una comprobación previa en memoria: guardó el comprobante junto con el cambio de negocio y comparó documento, fecha y motivo antes de aceptar una repetición. La protección concurrente se verificó después con la suite de integración.
- Commit relacionado: `a9982f1` — Registra retiros con comprobantes transaccionales e idempotencia.
- Comprobación realizada: Una solicitud devolvió 201, su repetición devolvió 200 con el mismo resultado y el intento con MOBILE_TOKEN devolvió 403.

## Uso 7
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Cambiar el recorrido de los retiros de Subsidios sin eliminar su ruta pública ni el camino original necesario para una reversión.
- Prompt principal (resumido): Resumen reconstruido: Modificar únicamente el consumidor Subsidios para que POST :8091/retiros convierta documento, fecha y motivo al contrato del gateway y envíe SUBSIDIOS_TOKEN. Conservar movimiento en la respuesta y permitir requestId o Idempotency-Key para reintentos. Mantener la llamada original disponible para el modo legacy. Ante un timeout no volver automáticamente al procedimiento antiguo, porque el gateway podría haber confirmado el retiro.
- Qué produjo: services/subsidios/gateway_client.py, cambios en app.py y un Dockerfile que incluye el cliente HTTP. La ruta original sigue disponible y puede responder con el identificador y estado de la solicitud.
- Qué modificó o corrigió el equipo: El asistente corrigió una lectura con la codificación predeterminada de Windows que falló sobre el archivo UTF-8 del kit. Tras aplicar la modificación correctamente, volvió a construir Subsidios y repitió la prueba HTTP antes de crear el commit.
- Commit relacionado: `8cd3fb2` — Migra Subsidios al gateway conservando el procedimiento original.
- Comprobación realizada: Dos solicitudes con el mismo requestId devolvieron 201 y 200 con el mismo movimiento; se confirmó un registro de auditoría con consumer subsidios.

## Uso 8
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Aceptar retiros durante una caída de PostgreSQL y conservarlos aunque el gateway se reinicie antes de poder aplicarlos.
- Prompt principal (resumido): Resumen reconstruido: Introducir una cola persistente independiente de PostgreSQL. Guardar la solicitud antes de aceptarla y devolver 202 cuando no pueda confirmarse inmediatamente. Implementar un worker que reintente usando los comprobantes transaccionales existentes, incluyendo el caso en que PostgreSQL confirmó pero se perdió la respuesta. Persistir la cola en un volumen Docker y permitir consultar el resultado. Probar una caída real, reiniciar gateway con una solicitud pendiente y comprobar su recuperación.
- Qué produjo: src/inbox.py, src/dispatcher.py, el volumen gateway-state, el ciclo de vida del worker y GET /api/v1/retirement-requests/{request_id}. Las solicitudes pueden terminar en completed, not_found o conflict, conservando pending mientras deban reintentarse.
- Qué modificó o corrigió el equipo: El asistente mantuvo la cola fuera del legacy, utilizó WAL y sincronización completa en SQLite y cerró sus conexiones explícitamente. Los errores de PostgreSQL dejan el trabajo pendiente; el comprobante remoto evita repetir un retiro tras una confirmación ambigua.
- Commit relacionado: `cc262b8` — Persiste retiros pendientes y recupera operaciones tras caídas y reinicios.
- Comprobación realizada: Se detuvo legacy-db, se obtuvo 503 en menos de tres segundos en una consulta, se aceptó un retiro con 202, se reinició gateway y se comprobó que permanecía pending. Al volver la base, terminó completed y un nuevo envío devolvió 200.

## Uso 9
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Hacer reversible la migración y añadir un consumidor móvil que use exclusivamente la API con permisos de lectura.
- Prompt principal (resumido): Resumen reconstruido: Persistir los estados LEGACY, DUAL y MODERN y exponerlos por la ruta obligatoria de migración. Crear ./rollback.sh affiliations para seleccionar LEGACY mediante un contenedor administrativo incluso si gateway está detenido. Compartir ese control con Subsidios en modo de solo lectura y conservar la cola. Construir un consumidor móvil web adaptable que consulte afiliados y beneficiarios por HTTP, mantenga MOBILE_TOKEN en el servidor y no acceda a PostgreSQL.
- Qué produjo: src/migration.py, rollback.sh ejecutable, lectura del control persistente en Subsidios y services/mobile con su interfaz y proxy HTTP. El gateway puede actualizar el plan de migración mediante la administración local.
- Qué modificó o corrigió el equipo: El asistente separó el cambio administrativo de los endpoints públicos y evitó que el rollback borrara solicitudes aceptadas. Para demostrar la reversión, detuvo gateway después de seleccionar LEGACY y registró un retiro desde Subsidios antes de restaurar DUAL.
- Commit relacionado: `1de06a0` — Implementa estados persistentes rollback y consumidor móvil de lectura.
- Comprobación realizada: Se comprobó el consumidor móvil, el estado LEGACY y un retiro 201 con gateway apagado. Después se reanudó DUAL y se levantó gateway; la persistencia tras reinicio también se comprobó en el script final de eventos.

## Uso 10
- Herramienta: Codex, asistente de OpenAI utilizado en esta conversación.
- Para qué se usó: Contrastar la reconstrucción con el contrato, producir evidencia reproducible y completar los documentos exigidos por el reto.
- Prompt principal (resumido): Resumen reconstruido: Cerrar la implementación con modelos y contrato OpenAPI, una suite que pruebe los servicios reales y un reporte JUnit. Comparar activeMembers con PostgreSQL y contar movimientos para comprobar idempotencia. Crear verificaciones separadas de cambio de esquema, caída, reinicio y rollback sin montar el socket Docker en contenedores. Probar también un despliegue con volúmenes vacíos, conservar la instalación principal y completar README, dependencias, arquitectura, plan de migración y uso de IA sin inventar resultados oficiales.
- Qué produjo: Quince pruebas en tests/test_contract.py, el servicio tests, scripts/verify-events.py, modelos en src/schemas.py, openapi.yaml y documentación del proyecto. Se generaron contract.xml y events.json como evidencia de las ejecuciones.
- Qué modificó o corrigió el equipo: El asistente aisló la comprobación desde cero en otro proyecto Compose y eliminó únicamente sus volúmenes temporales. Comparó Educación y Portal con el kit original y revisó secretos en el historial. El problema de impresión Unicode del revisor en Windows se resolvió posteriormente con variables de codificación, sin editar el validador.
- Commit relacionado: `d9d9291` — Documenta el contrato y verifica integración eventos y arranque limpio.
- Comprobación realizada: Pasaron quince pruebas de integración y otros quince casos al ejecutarlas sobre volúmenes vacíos. El script aprobó cinco controles de eventos. Las nueve comprobaciones públicas pasaron; los casos ocultos oficiales no se ejecutaron.

## Estado de revisión y límites

La auditoría posterior está en [docs/auditoria-requisitos.md](docs/auditoria-requisitos.md): identifica el uso de consumer unknown y los errores estándar de rutas inexistentes como ajustes pendientes. Haber aprobado pruebas propias y el validador público no equivale a aprobar los casos ocultos ni a tener lista la entrega en la plataforma.
