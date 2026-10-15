# Dependencias del sistema original

| Aplicación | Tabla | Operación | Criticidad |
|---|---|---|---|
| Educación | AFI_MAE | Lectura | Alta |
| Educación | EMPRESA | Lectura | Alta |
| Subsidios | AFI_MAE | Escritura | Alta |
| Subsidios | LOGMOV | Escritura | Alta |
| Reportes nocturnos | AFI_MAE | Lectura | Media |
| Reportes nocturnos | LOGMOV | Lectura | Media |

## Alcance y fuentes

La tabla conserva las seis dependencias del sistema original indicadas en [procesos.md](procesos.md). El procedimiento suministrado en db/init/03_procedures.sql confirma las dos escrituras de Subsidios: estado del afiliado y movimiento de retiro.

Las lecturas de Educación son críticas para verificar afiliación antes de matrícula. Las escrituras de Subsidios cambian el estado operativo y dejan trazabilidad. Los reportes nocturnos dependen de los datos, con criticidad media por su ejecución diferida.

## Efecto de la transición

Portal no accede directamente a tablas; consulta HTTP desde el kit. El consumidor móvil también usa HTTP. En DUAL/MODERN, las escrituras de Subsidios pasan por gateway y su adapter; la dependencia original vuelve a utilizarse directamente después del rollback.

El cambio de esquema renombra AFI_MAE a PERSON_MASTER y modifica dos columnas. El mapa conserva los nombres originales para describir el descubrimiento del kit; la compatibilidad de nombres está encapsulada en el adapter. Los comprobantes y la cola son componentes nuevos, no dependencias originales adicionales.
