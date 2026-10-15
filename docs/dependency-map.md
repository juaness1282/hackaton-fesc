# Dependencias del sistema original

| Aplicación | Tabla | Operación | Criticidad |
|---|---|---|---|
| Educación | AFI_MAE | Lectura | Alta |
| Educación | EMPRESA | Lectura | Alta |
| Subsidios | AFI_MAE | Escritura | Alta |
| Subsidios | LOGMOV | Escritura | Alta |
| Reportes nocturnos | AFI_MAE | Lectura | Media |
| Reportes nocturnos | LOGMOV | Lectura | Media |

Fuente: docs/procesos.md y procedimiento suministrado en el kit. Portal consume HTTP; no se le atribuye una conexión directa a las tablas. El adapter implementa las nuevas dependencias del gateway.
