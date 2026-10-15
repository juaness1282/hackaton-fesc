# Verificación de la reconstrucción

## Fechas de ejecución y actualización

Todas las fechas se expresan en la zona America/Bogota.

- Ejecución inicial de controles: 14 de octubre de 2026.
- Pruebas de eventos y arranque con volúmenes vacíos: 14 de octubre de 2026.
- Nueva ejecución de integración y validador público: 15 de octubre de 2026.
- Comprobación de Docker y estado de los servicios: 15 de octubre de 2026.
- Actualización de este documento: 15 de octubre de 2026.

## Controles ejecutados

| Comprobación | Resultado | Fecha de ejecución |
|---|---|---|
| Contrato e integración con PostgreSQL real | 15 pruebas aprobadas en la nueva ejecución | 15 de octubre de 2026 |
| Arranque con volúmenes completamente vacíos | 15 pruebas aprobadas | 14 de octubre de 2026 |
| Cambio real de esquema | Respuestas idénticas antes y después | 14 de octubre de 2026 |
| Caída de PostgreSQL | Consulta 503 con LEGACY_UNAVAILABLE en menos de 3 segundos | 14 de octubre de 2026 |
| Persistencia de retiro aceptado | 202; solicitud conservada al reiniciar gateway | 14 de octubre de 2026 |
| Recuperación e idempotencia | Solicitud completada; exactamente un movimiento en PostgreSQL | 14 de octubre de 2026 |
| Rollback | Estado LEGACY persistente; retiro desde Subsidios con gateway apagado | 14 de octubre de 2026 |
| Validador público | 9 comprobaciones disponibles aprobadas en la nueva ejecución | 15 de octubre de 2026 |
| Educación y Portal | Código idéntico al kit original, comprobado por hash | 14 de octubre de 2026 |
| Sintaxis Python y configuración Compose | Válidas | 14 de octubre de 2026 |
| Construcción y arranque de servicios | docker compose up -d --build completado correctamente | 15 de octubre de 2026 |

Se aprobaron los controles requeridos incluidos en estas verificaciones: consultas, autenticación, permisos, retiros idempotentes, integración de consumidores, cambio de esquema, recuperación durante caídas y rollback. La suite de integración compara activeMembers con PostgreSQL y cuenta movimientos reales para comprobar que los reintentos no dupliquen retiros.

## Evidencia

- [test-results/contract.xml](../test-results/contract.xml): reporte JUnit de la ejecución de integración del 15 de octubre.
- [test-results/events.json](../test-results/events.json): cinco controles de eventos aprobados en la ejecución del 14 de octubre.
- El validador público se ejecutó mediante ./validator check el 15 de octubre y aprobó sus nueve comprobaciones disponibles.
- El despliegue aislado usado para comprobar volúmenes vacíos se eliminó conservando los volúmenes del proyecto principal.

La integración y el validador público se repitieron el 15 de octubre. Los eventos destructivos y la comprobación con volúmenes vacíos conservan sus resultados del 14 de octubre; no se repitieron durante esta actualización.

## Estado del entorno comprobado

El 15 de octubre Docker respondió correctamente, con versión de motor 29.4.3. Al comenzar la consulta no había contenedores de este proyecto ejecutándose; se levantaron con docker compose up -d --build.

Al finalizar la comprobación se observaron seis servicios en ejecución:

| Servicio | Estado observado |
|---|---|
| legacy-db | En ejecución y healthy |
| gateway | En ejecución |
| educacion-app | En ejecución |
| portal-client | En ejecución |
| subsidios-app | En ejecución |
| mobile-client | En ejecución |

La base principal conserva el cambio de esquema aplicado en las pruebas de eventos. Afiliaciones y Retiros quedaron en DUAL al terminar aquellas pruebas; la nueva ejecución del validador público confirmó affiliations=DUAL.

La solución anterior conserva sus archivos y volúmenes. El estado de la tabla corresponde al momento de esta comprobación, no a un monitoreo continuo.

## Observaciones de implementación

1. **Identificación del consumidor en auditoría:** algunas peticiones, incluida salud con token válido, se registran con consumer unknown, fuera de portal, subsidios y mobile indicados en el contrato.
2. **Formato de errores del router:** una ruta inexistente devuelve {"detail":"Not Found"} en lugar de message y error_id. El manejador actual no cubre todas las excepciones HTTP del router.

Estos hallazgos están documentados en [auditoria-requisitos.md](auditoria-requisitos.md). La revisión documental conserva la descripción de esos comportamientos.

## Revisión documental del 15 de octubre de 2026

Se revisaron en orden README, arquitectura, plan de migración, mapa de dependencias, OpenAPI, AI_USAGE y apoyo del pitch, contrastándolos con el código y los resultados registrados.

- README: instalación, configuración, comandos de uso, pruebas y pendientes actualizados.
- Arquitectura: transacción de retiro, comprobantes, cola, recuperación y rollback explicados según la implementación.
- Migración: estado consultado DUAL/DUAL/LEGACY; criterios de promoción identificados como metas futuras.
- Dependencias: conservadas las seis filas del descubrimiento original y aclarado su alcance.
- OpenAPI: siete rutas y seguridad contrastadas con la aplicación; treinta y siete ejemplos validados con los modelos Pydantic reales.
- AI_USAGE: doce usos documentados, incluidos los commits documentales, con prompts identificados como resúmenes reconstruidos.
- Pitch: guion revisado y marcado como apoyo opcional; el video y su enlace se gestionan en Google Drive y Mi equipo.
- Enlaces y comandos: dieciséis enlaces locales existentes y trece bloques Bash del README con sintaxis comprobada.

La revisión contrastó la documentación con la implementación. Las dos observaciones técnicas constan en este documento; la entrega del video se gestiona en la plataforma del evento.
