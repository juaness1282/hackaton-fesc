# Uso de inteligencia artificial

La reconstrucción fue implementada por Codex a petición de Juan Esteban Mantilla Vega, tras una implementación previa en otra carpeta. Las correcciones siguientes las realizó el asistente y requieren revisión humana. Los commits registran esta reconstrucción con fechas reales, sin atribuir trabajo a otra persona.

## Uso 1
- Herramienta: Codex.
- Para qué se usó: reconstruir el gateway desde el kit original.
- Prompt principal (resumido): empezar el desarrollo desde cero en una carpeta completamente nueva.
- Qué produjo: proyecto Docker nuevo, adapter, consultas y autenticación.
- Qué modificó o corrigió el equipo: El asistente esperó la disponibilidad real del gateway antes de comprobar las rutas; arrancar el contenedor no garantiza que la API ya acepte conexiones.

## Uso 2
- Herramienta: Codex.
- Para qué se usó: migrar retiros de Subsidios y proteger reintentos.
- Prompt principal (resumido): reconstruir por componentes con comprobaciones y commits reales.
- Qué produjo: comprobantes PostgreSQL, bloqueo transaccional y cliente HTTP de Subsidios.
- Qué modificó o corrigió el equipo: El asistente corrigió la lectura UTF-8 de los archivos del kit en Windows y volvió a comprobar idempotencia y auditoría antes del commit.

## Uso 3
- Herramienta: Codex.
- Para qué se usó: recuperar solicitudes y volver al camino original.
- Prompt principal (resumido): continuar la reconstrucción de cola persistente, rollback y consumidor móvil.
- Qué produjo: SQLite independiente, worker, estado administrativo compartido y cliente móvil web.
- Qué modificó o corrigió el equipo: El asistente conservó pendientes durante cambios de modo, evitó el fallback tras timeouts y comprobó un retiro original con gateway apagado.

Ambos estudiantes deben entender y modificar lo entregado según el reglamento. Este documento no afirma revisión humana todavía realizada ni aprobación del validador oficial.
