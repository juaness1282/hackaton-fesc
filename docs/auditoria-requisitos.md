# Auditoría de requisitos — nivel tecnólogo

Proyecto revisado: fesc-tecnologo-nuevo.
Commit de implementación: d9d9291.
Resultado: funcionalidad principal verificada, pero no se puede afirmar cumplimiento completo.
La revisión no modifica la implementación ni crea commits. Las ejecuciones actualizan los reportes de pruebas.

## Evidencia ejecutada en esta auditoría

- docker compose --profile test run --rm tests: 15 pruebas aprobadas.
- python scripts/verify-events.py: cinco controles aprobados; esquema, caída, persistencia al reiniciar, recuperación con un movimiento y rollback con gateway apagado.
- validator check: nueve comprobaciones públicas aprobadas; seis reservadas al calificador oficial.
- validator entregables: 21.65/22 en apartados evaluables localmente. GE04 y GE10 no se incluyen en ese subtotal.
- Revisión de Docker Compose resuelto: sin privileged, cap_add, devices, red/procesos del host ni montajes de rutas externas.
- Comparación binaria contra el kit: Educación y Portal, incluidos Dockerfiles, permanecen intactos.
- Revisión de los diez commits: .env no fue versionado y los valores reales de las cuatro credenciales actuales no aparecen en sus archivos.
- Ningún archivo versionado supera 1 MB.
- Repositorio GitHub accesible sin autenticación: HTTP 200. git ls-remote origin no devuelve referencias; todavía no contiene los commits locales.

## Matriz funcional

| Requisito | Resultado y límites |
|---|---|
| G01 Salud | Verificado: 200, status UP y estado del legacy |
| G02 Afiliado | Prueba pública y muestra de integración aprobadas; no se dispone de muestras ocultas |
| G03 Beneficiarios | Estructura y consumidor verificados; datos de la muestra oculta no comprobables |
| G04 Empresa y activeMembers | Conteo comparado con PostgreSQL real y correcto |
| G05 Autenticación y permisos | Sin token 401; móvil consulta 200 y retiro 403 |
| G06 Errores | Registros inexistentes del contrato devuelven 404 con message/error_id; hay un desajuste fuera de esas rutas, descrito abajo |
| G07 Retiro migrado | Confirmación 201, estado visible en PostgreSQL, Educación y Portal |
| G08 Idempotencia | Repetición 200, concurrencia y exactamente un movimiento SQL verificados |
| G09 Cambio de esquema | Evento real aplicado; tres respuestas idénticas antes y después |
| G10 Base caída | Consulta 503 LEGACY_UNAVAILABLE en menos de tres segundos |
| G11 Recuperación | Solicitud aceptada 202 sobrevive a reinicio y se aplica una sola vez |
| G12 Auditoría | Campos y enmascaramiento correctos en prueba pública; consumer presenta un desajuste literal |
| G13 Procedimiento original | Ejecutado mediante Subsidios con gateway apagado después del rollback |
| G14 Estado de migración | DUAL y LEGACY persistentes; documentos coinciden tras administración |
| G15 Subsidios | HTTP por gateway y auditoría como subsidios; comprobación SQL de no duplicación |
| App móvil | Interfaz web adaptable con consultas HTTP y permisos de solo lectura; no es un paquete nativo |

El arranque con volúmenes vacíos ya se comprobó para esta implementación y pasó las quince pruebas. No se repitió durante esta auditoría porque el código no cambió desde esa comprobación.

## Desajustes técnicos reproducidos

### 1. consumer fuera del conjunto exigido

RETO.md requiere consumer portal, subsidios o mobile. src/observability.py usa unknown cuando no se ejecutó la dependencia de autenticación.
Se reprodujo GET /health enviando PORTAL_TOKEN válido y la auditoría registró unknown, 200.
Al inspeccionar el archivo en esta revisión se observaron 31 registros unknown; también hay peticiones públicas y rechazadas.

Se debe reconocer al consumidor cuando exista un token válido, aun en salud, y definir explícitamente el tratamiento de peticiones sin identidad. No corresponde inventar un consumidor para una petición anónima. El contrato no describe esa excepción; el ajuste debe resolverla o documentar una aclaración del organizador.

### 2. Error estándar en rutas inexistentes

GET /ruta-inexistente devuelve 404 con {"detail":"Not Found"}.
El formato exigido es {"message","error_id"}.
src/observability.py registra el manejador sobre fastapi.HTTPException, sin cubrir la excepción base que genera el router de Starlette.
Los 404 de registros inexistentes de las rutas del contrato sí tienen el formato correcto.

Conviene cubrir las excepciones HTTP del router y comprobar también los métodos no permitidos. No se ha modificado el código como parte de esta verificación.

## Entregables

| Entregable | Estado |
|---|---|
| Adapter | 5/5 en GE01 |
| Mapa de dependencias | 3/3 |
| Plan de migración | 3/3 |
| Rollback | Prueba propia real aprobada; GE04 se ejecuta oficialmente |
| Pruebas y reporte JUnit | 3/3, quince casos aprobados |
| OpenAPI 3 | 2/2, seis rutas requeridas y ruta adicional de seguimiento |
| Arquitectura | 1/1 |
| Git | Diez commits reales y mensajes descriptivos; 0.83/1 por un único integrante con tres o más commits |
| Uso de IA | 2/2; revisión humana del contenido y dominio del código pendientes |
| README | 1.82/2; sección Integrantes incompleta según la comprobación automática |
| Pitch | Solo existe guion; no se proporcionó enlace al video público ni evidencia de registro |

La revisión de historial se ejecutó sin fecha de inicio o cierre. Por eso contar diez commits localmente no demuestra que estén dentro de la ventana oficial: hace falta la fecha del evento.

## Entrega externa pendiente o no verificable

1. Subir los commits al repositorio público: actualmente no hay referencias remotas.
2. Confirmar que el enlace está registrado en Mi equipo.
3. Grabar y subir el video de hasta sesenta segundos, compartirlo públicamente y registrar el enlace.
4. Confirmar ventana de entrega e integrantes conforme a las reglas del evento.
5. Revisión humana: entender, ejecutar, depurar y modificar el código no puede certificarse con un test automático.

No existe un requisito de separar commits quince minutos. RETO.md exige cantidad, identidades, contribuciones y mensajes, además de las fechas dentro del evento.

## Conclusión

La revisión funcional es satisfactoria en las pruebas disponibles y propias. Quedan dos desajustes técnicos y tareas de entrega antes de declarar cumplimiento total. Los casos ocultos y el pitch del comité no han sido evaluados.
