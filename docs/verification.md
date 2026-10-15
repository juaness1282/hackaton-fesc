# Verificación de la reconstrucción

Resultados ejecutados el 14 de octubre de 2026, zona America/Bogota.

| Comprobación | Resultado |
|---|---|
| Contrato e integración con PostgreSQL real | 15 pruebas aprobadas |
| Nueva ejecución con volúmenes completamente vacíos | 15 pruebas aprobadas |
| Cambio real de esquema | Respuestas idénticas antes y después |
| Caída de PostgreSQL | Consulta 503 con LEGACY_UNAVAILABLE en menos de 3 segundos |
| Persistencia de retiro aceptado | 202; conservado al reiniciar gateway |
| Recuperación e idempotencia | Solicitud completada; exactamente un movimiento en PostgreSQL |
| Rollback | Estado LEGACY persistente; retiro desde Subsidios con gateway apagado |
| Validador público | 9 comprobaciones disponibles aprobadas |
| Educación y Portal | Código idéntico al kit original, comprobado por hash |
| Sintaxis Python y configuración Compose | Válidas |

Evidencia: test-results/contract.xml y test-results/events.json. La suite de integración verifica la cantidad real de movimientos en PostgreSQL y compara activeMembers con un conteo SQL. El despliegue aislado de prueba se eliminó conservando los volúmenes del proyecto principal.

La base principal conserva el cambio de esquema aplicado por la prueba. Afiliaciones y Retiros quedaron en DUAL al terminar. Los seis servicios de la reconstrucción permanecen levantados. La solución anterior conserva sus archivos y volúmenes; sus contenedores se detuvieron para liberar puertos.

Las pruebas propias no sustituyen los casos ocultos del calificador oficial. No se afirma una nota final ni criterios temporales de siete días ya cumplidos.
