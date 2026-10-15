# Arquitectura

## Contexto

La caja utiliza una base compartida por aplicaciones antiguas que deben continuar funcionando. La reconstrucción crea una frontera HTTP para Afiliaciones y Retiros, manteniendo Educación y Portal sin modificaciones. El kit original es independiente de las carpetas de soluciones anteriores.

## Componentes

legacy-db mantiene datos y procedimientos. educacion-app consulta directamente y portal-client utiliza HTTP. subsidios-app envía retiros a gateway y conserva su acceso original para reversión. mobile-client es un consumidor web adaptable a teléfonos. tests verifica servicios reales. gateway encapsula autenticación, modelo canónico, adapter, auditoría, cola y recuperación.

## Modelo canónico

Afiliado contiene document, fullName, status y company. Beneficiarios contienen document, fullName y relationship. Empresa contiene id, name y activeMembers. Retiro recibe requestId, date y reason; devuelve movement y status. Los nombres físicos y códigos del sistema antiguo permanecen dentro de src/db_adapter.py.

## Cambio de esquema

El adapter detecta si existe la tabla renombrada en cada transacción y selecciona identificadores de una lista interna permitida. Los valores se parametrizan. El evento cambia los nombres físicos sin modificar la API, los consumidores ni las representaciones canónicas de los datos.

## Alternativas descartadas

- Acceso directo de consumidores nuevos a PostgreSQL: propaga el conocimiento del esquema y viola el contrato. Se usa HTTP y una única frontera de adaptación.
- Cola en memoria: perdería solicitudes ante reinicios. SQLite usa WAL y sincronización completa en un volumen independiente de la base antigua.
- Comprobante únicamente local: una conexión perdida después de confirmar PostgreSQL podría duplicar un retiro. El cambio y su comprobante se confirman en la misma transacción PostgreSQL.
- Fallback automático de Subsidios después de un timeout: puede ejecutar de nuevo un retiro ya confirmado. El camino original requiere una reversión administrativa explícita.

## Escritura y recuperación

Primero se persiste la solicitud en SQLite. Se intenta aplicar el procedimiento junto con un comprobante de requestId, protegido por un bloqueo transaccional. Una primera confirmación devuelve 201; una repetición confirmada devuelve 200. Datos distintos con el mismo identificador devuelven 409.

Durante una caída, un retiro persistido devuelve 202 y permanece pending. El worker reintenta sin eliminarlo. Si hubo un commit ambiguo, PostgreSQL devuelve el comprobante existente sin repetir el procedimiento. Si el afiliado no existe, la solicitud termina not_found; un conflicto contra un comprobante existente termina conflict. El consumidor consulta GET /api/v1/retirement-requests/{request_id}.

## Persistencia y límites

gateway-state guarda solicitudes y control administrativo; legacy-db-data guarda fuente y comprobantes. El despliegue usa un gateway y un worker; no se afirma alta disponibilidad de almacenamiento local ni rendimiento bajo carga. El rollback no elimina volúmenes y mantiene los pendientes. El consumidor móvil guarda MOBILE_TOKEN únicamente del lado servidor.
