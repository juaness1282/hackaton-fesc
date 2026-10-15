# Auditoría de requisitos — nivel tecnólogo

Proyecto revisado: fesc-tecnologo-nuevo.
Última actualización documental: 15 de octubre de 2026, zona America/Bogota.
Commit de implementación verificado: d9d9291.
Versión publicada consultada: d8794e9, que incorpora la ampliación de AI_USAGE y esta auditoría.

Resultado: la funcionalidad principal pasó las comprobaciones registradas, pero quedan dos desajustes técnicos y tareas de entrega. Esta actualización documental no modifica la implementación ni crea commits.

## Publicación comprobada al iniciar la revisión documental

- Repositorio: [juaness1282/hackaton-fesc](https://github.com/juaness1282/hackaton-fesc).
- En la consulta previa al cierre de esta revisión, la rama publicada main tenía once commits.
- En esa consulta HEAD local y refs/heads/main del remoto coincidían en d8794e9c2941bd43e965713ad0af8758d6a8984e. Las modificaciones documentales posteriores se registran en un nuevo commit.
- La subida del proyecto está completada. El registro del enlace en Mi equipo no está verificado.
- En la primera consulta del 15 de octubre el motor Docker no estaba disponible. En una comprobación posterior respondió correctamente: se levantaron los seis servicios y pasaron nuevamente las quince pruebas de integración y las nueve comprobaciones públicas. Las fechas de cada control y el estado observado se detallan en [verification.md](verification.md).

## Evidencia de las ejecuciones registradas

Los siguientes resultados corresponden a las pruebas anteriores documentadas en test-results/contract.xml y test-results/events.json. La matriz funcional resume esas comprobaciones; no certifica disponibilidad en tiempo real.

- docker compose --profile test run --rm tests: 15 pruebas aprobadas.
- python scripts/verify-events.py: cinco controles aprobados; esquema, caída, persistencia al reiniciar, recuperación con un movimiento y rollback con gateway apagado.
- validator check: nueve comprobaciones públicas aprobadas; seis reservadas al calificador oficial.
- validator entregables: 21.65/22 en apartados evaluables localmente. GE04 y GE10 no se incluyen en ese subtotal.
- Revisión de Docker Compose resuelto: sin privileged, cap_add, devices, red/procesos del host ni montajes de rutas externas.
- Comparación binaria contra el kit: Educación y Portal, incluidos Dockerfiles, permanecen intactos.
- La auditoría de implementación revisó los diez primeros commits: .env no fue versionado y los valores reales de las cuatro credenciales no aparecieron en sus archivos. Antes de publicar el undécimo commit documental también se revisaron los archivos pendientes y la exclusión de .env.
- Ningún archivo versionado supera 1 MB.
- En la auditoría inicial GitHub era accesible sin autenticación, pero aún no tenía referencias. Esa situación fue resuelta al publicar main; la coincidencia local/remoto se comprobó nuevamente el 15 de octubre.

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
Al inspeccionar el archivo en la auditoría original se observaron 31 registros unknown; también había peticiones públicas y rechazadas. Es una observación histórica, no un recuento actualizado del archivo.

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
| Git | Once commits publicados al iniciar esta revisión; el resultado registrado fue 0.83/1 por un único integrante con tres o más commits. El commit documental de cierre se añade después |
| Uso de IA | 2/2; revisión humana del contenido y dominio del código pendientes |
| README | 1.82/2; sección Integrantes incompleta según la comprobación automática |
| Pitch | Solo existe guion; no se proporcionó enlace al video público ni evidencia de registro |

La revisión de historial se ejecutó sin fecha de inicio o cierre. La cantidad de commits, incluso publicados, no demuestra por sí sola que estén dentro de la ventana oficial: hace falta la fecha del evento.

## Entrega completada y pendientes externos

| Acción | Estado |
|---|---|
| Publicar el proyecto en GitHub | Completado; main coincide con la versión local consultada |
| Registrar el enlace en Mi equipo | No verificado |
| Grabar y subir el pitch de hasta sesenta segundos | Enlace al video no proporcionado; solo consta el guion |
| Hacer público el video y registrar su enlace | No verificado |
| Confirmar ventana de entrega e integrantes | Pendiente de los datos y reglas oficiales del evento |
| Revisión humana del código y AI_USAGE | Pendiente; entender, ejecutar, depurar y modificar el código no puede certificarse con un test automático |

No existe un requisito de separar commits quince minutos. RETO.md exige cantidad, identidades, contribuciones y mensajes, además de las fechas dentro del evento.

## Revisión documental posterior

El 15 de octubre se contrastaron los siete documentos y materiales acordados. OpenAPI recibió ejemplos validados con modelos reales; README incorporó comandos de instalación, uso y pruebas. Arquitectura y migración distinguen el comportamiento implementado de los criterios futuros. El pitch quedó identificado como material opcional dentro del repositorio: la entrega requerida es el video público registrado en Mi equipo.

Los dos hallazgos técnicos permanecen abiertos; esta revisión no los corrigió ni los eliminó del registro. Las fechas de pruebas y edición constan en verification.md.

## Conclusión

La revisión funcional es satisfactoria en las pruebas disponibles y propias. Quedan dos desajustes técnicos y tareas de entrega antes de declarar cumplimiento total. Los casos ocultos y el pitch del comité no han sido evaluados.
