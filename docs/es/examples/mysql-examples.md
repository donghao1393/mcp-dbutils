# Ejemplos de MySQL

*[English](../../en/examples/mysql-examples.md) | [中文](../../zh/examples/mysql-examples.md) | [Français](../../fr/examples/mysql-examples.md) | Español | [العربية](../../ar/examples/mysql-examples.md) | [Русский](../../ru/examples/mysql-examples.md)*

Este documento proporciona ejemplos prácticos para trabajar con bases de datos MySQL usando MCP Database Utilities.

## Configuración Básica

```yaml
connections:
  my-mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
    charset: utf8mb4  # Recomendado para soporte completo de Unicode
```

## Operaciones Comunes

### Listar Tablas

**Usted**: "Lista todas las tablas en mi base de datos MySQL."

**IA**: "Aquí están las tablas en su base de datos MySQL:
- usuarios
- productos
- pedidos
- categorias
- proveedores
- inventario"

### Ver Estructura de Tabla

**Usted**: "Muéstrame la estructura de la tabla usuarios."

**IA**: "La tabla usuarios tiene la siguiente estructura:
- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- nombre (VARCHAR(100), NOT NULL)
- email (VARCHAR(100), NOT NULL, UNIQUE)
- fecha_creacion (DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
- ultimo_login (DATETIME)
- estado (ENUM('activo', 'inactivo', 'suspendido'), DEFAULT 'activo')
- rol_id (INT, FOREIGN KEY references roles(id))"

### Consulta Básica

**Usted**: "Muéstrame los 5 últimos usuarios registrados."

**IA**: "Aquí están los 5 últimos usuarios registrados:

| id | nombre | email | fecha_creacion |
|----|--------|-------|----------------|
| 42 | Juan Pérez | juan@ejemplo.com | 2023-11-25 14:32:15 |
| 41 | María García | maria@ejemplo.com | 2023-11-24 09:45:22 |
| 40 | Pedro Rodríguez | pedro@ejemplo.com | 2023-11-23 18:12:05 |
| 39 | Sofía López | sofia@ejemplo.com | 2023-11-22 11:30:47 |
| 38 | Tomás Martínez | tomas@ejemplo.com | 2023-11-21 16:08:33 |"

## Consultas Avanzadas

### Uniendo Tablas

**Usted**: "Muéstrame los 3 últimos pedidos con información de cliente y producto."

**IA**: "Aquí están los 3 últimos pedidos con información de cliente y producto:

| pedido_id | fecha_pedido | nombre_cliente | email_cliente | nombre_producto | precio | cantidad |
|-----------|--------------|----------------|---------------|-----------------|--------|----------|
| 1042 | 2023-11-25 | Juan Pérez | juan@ejemplo.com | Smartphone Pro | $899.99 | 1 |
| 1041 | 2023-11-24 | Sofía López | sofia@ejemplo.com | Auriculares Inalámbricos | $129.50 | 2 |
| 1040 | 2023-11-23 | Pedro Rodríguez | pedro@ejemplo.com | Laptop | $1299.00 | 1 |"

### Funciones de Agregación

**Usted**: "¿Cuál es el monto total de ventas por categoría de producto este mes?"

**IA**: "Aquí está el monto total de ventas por categoría de producto para este mes:

| categoría | total_ventas |
|-----------|--------------|
| Electrónica | $28,456.75 |
| Ropa | $12,389.30 |
| Hogar y Jardín | $9,876.50 |
| Deportes y Aire Libre | $7,654.25 |
| Libros y Medios | $3,210.80 |"

### Uso de Subconsultas

**Usted**: "¿Qué clientes han gastado más que el promedio este mes?"

**IA**: "Aquí están los clientes que han gastado más que el promedio este mes:

| cliente_id | nombre | email | total_gastado | promedio_global |
|------------|--------|-------|---------------|-----------------|
| 23 | María García | maria@ejemplo.com | $1,456.78 | $345.67 |
| 42 | Juan Pérez | juan@ejemplo.com | $1,245.50 | $345.67 |
| 15 | Tomás Martínez | tomas@ejemplo.com | $987.25 | $345.67 |
| 31 | Sofía López | sofia@ejemplo.com | $876.30 | $345.67 |
| 8 | Pedro Rodríguez | pedro@ejemplo.com | $654.90 | $345.67 |"

## Análisis de Rendimiento

### Plan de Ejecución de Consulta

**Usted**: "Explica el plan de ejecución para: SELECT * FROM pedidos JOIN clientes ON pedidos.cliente_id = clientes.id WHERE pedidos.fecha > '2023-01-01'"

**IA**: "Plan de ejecución para la consulta:
```
+----+-------------+------------+------------+--------+---------------+---------+---------+----------------------+------+----------+-------+
| id | select_type | table      | partitions | type   | possible_keys | key     | key_len | ref                  | rows | filtered | Extra |
+----+-------------+------------+------------+--------+---------------+---------+---------+----------------------+------+----------+-------+
|  1 | SIMPLE      | pedidos    | NULL       | range  | idx_fecha     | idx_fecha| 5       | NULL                 | 1250 | 100.00   | Using where |
|  1 | SIMPLE      | clientes   | NULL       | eq_ref | PRIMARY       | PRIMARY | 4       | db.pedidos.cliente_id | 1    | 100.00   | NULL  |
+----+-------------+------------+------------+--------+---------------+---------+---------+----------------------+------+----------+-------+
```

Esta consulta utiliza:
1. Un escaneo de rango en la tabla 'pedidos' usando el índice 'idx_fecha'
2. Una búsqueda por clave primaria en la tabla 'clientes' para cada fila coincidente de 'pedidos'
3. Estimación: aproximadamente 1250 filas serán examinadas en la tabla 'pedidos'"

### Estadísticas de Tabla

**Usted**: "Obtén estadísticas para la tabla pedidos."

**IA**: "Estadísticas para la tabla pedidos:
- Recuento de filas: 15,423
- Tamaño de tabla: 4.2 MB
- Tamaño promedio de fila: 285 bytes
- Índices:
  * PRIMARY (id): 1.1 MB
  * idx_cliente_id (cliente_id): 0.8 MB
  * idx_fecha (fecha): 0.7 MB
  * idx_estado (estado): 0.4 MB
- Fragmentación: 2.3%
- Último ANALYZE TABLE: 2023-11-20 08:15:32"

## Características Específicas de MySQL

### Uso de Procedimientos Almacenados

**Usted**: "¿Puedes mostrarme cómo llamar al procedimiento almacenado 'get_client_orders'?"

**IA**: "Para llamar al procedimiento almacenado 'get_client_orders' que recupera todos los pedidos de un cliente específico, puede usar:

```sql
CALL get_client_orders(42);
```

Resultado:

| pedido_id | fecha | monto | estado |
|-----------|-------|-------|--------|
| 1042 | 2023-11-25 | $899.99 | entregado |
| 987 | 2023-10-12 | $245.50 | entregado |
| 856 | 2023-09-03 | $78.25 | entregado |
| 743 | 2023-08-17 | $129.99 | entregado |

Este procedimiento almacenado acepta un parámetro cliente_id y devuelve todos los pedidos asociados a ese cliente."

### Uso de Vistas

**Usted**: "¿Qué información está disponible en la vista 'cliente_resumen'?"

**IA**: "La vista 'cliente_resumen' proporciona un resumen de las actividades de cada cliente:

| cliente_id | nombre | email | total_pedidos | monto_total | ultimo_pedido | estado_fidelidad |
|------------|--------|-------|---------------|-------------|---------------|------------------|
| 42 | Juan Pérez | juan@ejemplo.com | 12 | $3,456.78 | 2023-11-25 | Oro |
| 23 | María García | maria@ejemplo.com | 8 | $2,345.67 | 2023-11-24 | Plata |
| 15 | Tomás Martínez | tomas@ejemplo.com | 5 | $1,234.56 | 2023-11-20 | Bronce |

Esta vista combina datos de las tablas clientes, pedidos y programa_fidelidad para proporcionar una visión general de la actividad de cada cliente."

### Uso de Eventos

**Usted**: "¿Hay eventos programados en la base de datos?"

**IA**: "Sí, aquí están los eventos programados en la base de datos:

1. **daily_sales_report**
   - Frecuencia: Diariamente a las 23:00
   - Descripción: Genera un informe diario de ventas y lo inserta en la tabla 'informes_ventas'
   
2. **monthly_customer_cleanup**
   - Frecuencia: El 1er día de cada mes a las 02:00
   - Descripción: Archiva clientes inactivos por más de 12 meses
   
3. **hourly_inventory_check**
   - Frecuencia: Cada hora
   - Descripción: Verifica los niveles de inventario y genera alertas para productos agotados"

## Solución de Problemas

### Problemas Comunes

1. **Error "Too many connections"**
   - Causa: Se ha alcanzado el número máximo de conexiones simultáneas
   - Solución: Aumente max_connections en my.cnf u optimice su aplicación para usar un pool de conexiones

2. **Error "Lock wait timeout exceeded"**
   - Causa: Una transacción está esperando demasiado tiempo para adquirir un bloqueo
   - Solución: Verifique transacciones largas o bloqueadas con `SHOW PROCESSLIST` y optimice sus transacciones

3. **Rendimiento lento**
   - Posibles causas:
     * Consultas no optimizadas
     * Índices faltantes
     * Configuración de servidor inadecuada
   - Soluciones:
     * Use EXPLAIN para analizar consultas
     * Agregue índices apropiados
     * Optimice la configuración del servidor (innodb_buffer_pool_size, etc.)

### Comandos de Diagnóstico Útiles

```sql
-- Ver procesos en ejecución
SHOW PROCESSLIST;

-- Verificar el estado de las tablas
CHECK TABLE nombre_tabla;

-- Optimizar una tabla
OPTIMIZE TABLE nombre_tabla;

-- Ver variables del sistema
SHOW VARIABLES LIKE '%buffer%';

-- Ver estadísticas de rendimiento
SHOW ENGINE INNODB STATUS;
```

## Mejores Prácticas

1. **Seguridad**
   - Use cuentas con privilegios mínimos
   - Active SSL para conexiones
   - Use consultas preparadas para evitar inyecciones SQL

2. **Rendimiento**
   - Indexe columnas frecuentemente usadas en cláusulas WHERE, JOIN y ORDER BY
   - Evite SELECT * y seleccione solo las columnas necesarias
   - Use EXPLAIN para analizar y optimizar consultas

3. **Mantenimiento**
   - Programe copias de seguridad regulares
   - Configure replicación para alta disponibilidad
   - Monitoree regularmente el rendimiento y uso de recursos
