# Ejemplos de PostgreSQL

*[English](../../en/examples/postgresql-examples.md) | [中文](../../zh/examples/postgresql-examples.md) | [Français](../../fr/examples/postgresql-examples.md) | Español | [العربية](../../ar/examples/postgresql-examples.md) | [Русский](../../ru/examples/postgresql-examples.md)*

Este documento proporciona ejemplos prácticos para trabajar con bases de datos PostgreSQL usando MCP Database Utilities.

## Configuración Básica

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
    # Opciones adicionales
    sslmode: prefer  # Opciones: disable, allow, prefer, require, verify-ca, verify-full
```

## Operaciones Comunes

### Listar Esquemas

**Usted**: "Lista todos los esquemas en mi base de datos PostgreSQL."

**IA**: "Aquí están los esquemas en su base de datos PostgreSQL:
- public
- analytics
- auth
- reporting
- audit"

### Listar Tablas

**Usted**: "Lista todas las tablas en el esquema public."

**IA**: "Aquí están las tablas en el esquema public:
- usuarios
- productos
- pedidos
- categorias
- proveedores
- inventario"

### Ver Estructura de Tabla

**Usted**: "Muéstrame la estructura de la tabla usuarios."

**IA**: "La tabla usuarios tiene la siguiente estructura:
- id (SERIAL, PRIMARY KEY)
- nombre (VARCHAR(100), NOT NULL)
- email (VARCHAR(100), NOT NULL, UNIQUE)
- fecha_creacion (TIMESTAMP WITH TIME ZONE, NOT NULL, DEFAULT NOW())
- ultimo_login (TIMESTAMP WITH TIME ZONE)
- estado (VARCHAR(20), DEFAULT 'activo')
- metadata (JSONB)
- rol_id (INTEGER, REFERENCES roles(id))"

### Consulta Básica

**Usted**: "Muéstrame los 5 últimos usuarios registrados."

**IA**: "Aquí están los 5 últimos usuarios registrados:

| id | nombre | email | fecha_creacion |
|----|--------|-------|----------------|
| 42 | Juan Pérez | juan@ejemplo.com | 2023-11-25 14:32:15+01 |
| 41 | María García | maria@ejemplo.com | 2023-11-24 09:45:22+01 |
| 40 | Pedro Rodríguez | pedro@ejemplo.com | 2023-11-23 18:12:05+01 |
| 39 | Sofía López | sofia@ejemplo.com | 2023-11-22 11:30:47+01 |
| 38 | Tomás Martínez | tomas@ejemplo.com | 2023-11-21 16:08:33+01 |"

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

### Uso de CTE (Common Table Expressions)

**Usted**: "Usa una CTE para encontrar clientes que han gastado más que el promedio este mes."

**IA**: "Aquí están los clientes que han gastado más que el promedio este mes, usando una CTE:

| cliente_id | nombre | email | total_gastado | promedio_global |
|------------|--------|-------|---------------|-----------------|
| 23 | María García | maria@ejemplo.com | $1,456.78 | $345.67 |
| 42 | Juan Pérez | juan@ejemplo.com | $1,245.50 | $345.67 |
| 15 | Tomás Martínez | tomas@ejemplo.com | $987.25 | $345.67 |
| 31 | Sofía López | sofia@ejemplo.com | $876.30 | $345.67 |
| 8 | Pedro Rodríguez | pedro@ejemplo.com | $654.90 | $345.67 |

Esta consulta utiliza una CTE para calcular primero el promedio de gastos, luego encuentra los clientes cuyos gastos superan ese promedio."

### Uso de Funciones de Ventana (Window Functions)

**Usted**: "Muéstrame el ranking de productos más vendidos por categoría."

**IA**: "Aquí está el ranking de productos más vendidos por categoría:

| categoría | nombre_producto | cantidad_vendida | rango_en_categoría |
|-----------|-----------------|------------------|---------------------|
| Electrónica | Smartphone Pro | 1245 | 1 |
| Electrónica | Auriculares Inalámbricos | 987 | 2 |
| Electrónica | Tablet Ultra | 876 | 3 |
| Ropa | Camiseta Premium | 543 | 1 |
| Ropa | Jeans Clásicos | 432 | 2 |
| Ropa | Zapatillas Deportivas | 321 | 3 |
| Hogar y Jardín | Cafetera Automática | 234 | 1 |
| Hogar y Jardín | Set de Cocina | 210 | 2 |
| Hogar y Jardín | Lámpara de Diseño | 198 | 3 |

Esta consulta utiliza la función de ventana ROW_NUMBER() para clasificar los productos por cantidad vendida dentro de cada categoría."

## Análisis de Rendimiento

### Plan de Ejecución de Consulta

**Usted**: "Explica el plan de ejecución para: SELECT * FROM pedidos JOIN clientes ON pedidos.cliente_id = clientes.id WHERE pedidos.fecha > '2023-01-01'"

**IA**: "Plan de ejecución para la consulta:
```
                                                   QUERY PLAN
-----------------------------------------------------------------------------------------------------------------
 Hash Join  (cost=33.38..1756.15 rows=1250 width=172)
   Hash Cond: (pedidos.cliente_id = clientes.id)
   ->  Seq Scan on pedidos  (cost=0.00..1250.50 rows=1250 width=96)
         Filter: (fecha > '2023-01-01'::date)
   ->  Hash  (cost=18.50..18.50 rows=1150 width=76)
         ->  Seq Scan on clientes  (cost=0.00..18.50 rows=1150 width=76)
```

Análisis:
1. Se realiza un escaneo secuencial en la tabla 'pedidos' con un filtro en la fecha
2. Se realiza un escaneo secuencial en la tabla 'clientes'
3. Se utiliza una unión hash para combinar los resultados

Recomendaciones de optimización:
- Agregar un índice en pedidos.fecha para evitar el escaneo secuencial
- Verificar si ya existe un índice en clientes.id (clave primaria)"

### Estadísticas de Tabla

**Usted**: "Obtén estadísticas para la tabla pedidos."

**IA**: "Estadísticas para la tabla pedidos:
- Recuento estimado de filas: 15,423
- Tamaño de tabla: 4.2 MB
- Tamaño de índices: 3.1 MB
- Tasa de aciertos de caché: 98.5%
- Último VACUUM: 2023-11-20 08:15:32
- Último ANALYZE: 2023-11-20 08:15:32
- Bloat estimado: 3.2%
- Índices:
  * pedidos_pkey (id): 1.1 MB
  * idx_pedidos_cliente_id (cliente_id): 0.8 MB
  * idx_pedidos_fecha (fecha): 0.7 MB
  * idx_pedidos_estado (estado): 0.5 MB"

## Características Específicas de PostgreSQL

### Uso de Tipos de Datos JSON/JSONB

**Usted**: "Muéstrame los usuarios con preferencias específicas en su campo metadata."

**IA**: "Aquí están los usuarios con preferencias específicas en su campo metadata JSONB:

| id | nombre | email | preferencias |
|----|--------|-------|--------------|
| 42 | Juan Pérez | juan@ejemplo.com | {\"tema\": \"oscuro\", \"notificaciones\": true, \"idioma\": \"es\"} |
| 23 | María García | maria@ejemplo.com | {\"tema\": \"claro\", \"notificaciones\": false, \"idioma\": \"es\"} |
| 15 | Tomás Martínez | tomas@ejemplo.com | {\"tema\": \"auto\", \"notificaciones\": true, \"idioma\": \"en\"} |

Esta consulta utiliza el operador -> para acceder a las propiedades JSONB y filtrar los resultados según las preferencias de los usuarios."

### Uso de Tipos Geométricos

**Usted**: "Encuentra tiendas en un radio de 5 km alrededor de un punto dado."

**IA**: "Aquí están las tiendas en un radio de 5 km alrededor del punto (40.4168, -3.7038) (coordenadas de Madrid):

| id | nombre | dirección | distancia_km |
|----|--------|-----------|--------------|
| 12 | Tienda Centro | Calle Gran Vía 25, Madrid | 0.8 |
| 8 | Tienda Salamanca | Calle Serrano 43, Madrid | 1.2 |
| 15 | Tienda Moncloa | Avenida Complutense 5, Madrid | 2.5 |
| 23 | Tienda Alcobendas | Avenida Olímpica 10, Alcobendas | 4.7 |

Esta consulta utiliza el tipo de datos POINT y la función ST_Distance para calcular la distancia entre ubicaciones."

### Uso de Vistas Materializadas

**Usted**: "¿Qué información está disponible en la vista materializada 'informe_ventas_mensual'?"

**IA**: "La vista materializada 'informe_ventas_mensual' contiene los siguientes datos:

| año | mes | categoría | total_ventas | numero_pedidos | cesta_promedio |
|-----|-----|-----------|--------------|----------------|----------------|
| 2023 | 11 | Electrónica | $125,456.78 | 1245 | $100.77 |
| 2023 | 11 | Ropa | $87,654.32 | 1876 | $46.72 |
| 2023 | 11 | Hogar y Jardín | $65,432.10 | 876 | $74.69 |
| 2023 | 10 | Electrónica | $115,678.90 | 1156 | $100.07 |
| 2023 | 10 | Ropa | $76,543.21 | 1654 | $46.28 |
| 2023 | 10 | Hogar y Jardín | $54,321.09 | 765 | $71.01 |

Esta vista materializada se actualiza diariamente y proporciona un resumen preagregado de ventas por mes y categoría."

### Uso de Extensiones

**Usted**: "¿Qué extensiones de PostgreSQL están instaladas en la base de datos?"

**IA**: "Las siguientes extensiones están instaladas en la base de datos:

1. **pg_stat_statements**
   - Proporciona estadísticas de ejecución para todas las sentencias SQL ejecutadas

2. **PostGIS**
   - Agrega soporte para objetos geográficos permitiendo consultas de ubicación

3. **pgcrypto**
   - Proporciona funciones criptográficas

4. **uuid-ossp**
   - Proporciona funciones para generar UUIDs

5. **pg_trgm**
   - Proporciona funciones y operadores para determinar la similitud de texto basada en coincidencia de trigramas

6. **hstore**
   - Proporciona un tipo de datos para almacenar conjuntos de pares clave/valor"

## Solución de Problemas

### Problemas Comunes

1. **Error "too many connections"**
   - Causa: Se ha alcanzado el número máximo de conexiones simultáneas
   - Solución: Aumente max_connections en postgresql.conf u optimice su aplicación para usar un pool de conexiones

2. **Rendimiento lento**
   - Posibles causas:
     * Consultas no optimizadas
     * Índices faltantes
     * VACUUM no ejecutado regularmente
     * Configuración de servidor inadecuada
   - Soluciones:
     * Use EXPLAIN ANALYZE para analizar consultas
     * Agregue índices apropiados
     * Configure autovacuum correctamente
     * Optimice la configuración del servidor (shared_buffers, work_mem, etc.)

3. **Bloqueos (deadlocks)**
   - Causa: Dos o más transacciones esperando mutuamente la liberación de bloqueos
   - Solución: Verifique pg_locks y pg_stat_activity para identificar transacciones bloqueantes

### Comandos de Diagnóstico Útiles

```sql
-- Ver conexiones activas
SELECT * FROM pg_stat_activity;

-- Identificar consultas lentas
SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- Verificar bloqueos
SELECT * FROM pg_locks l JOIN pg_stat_activity a ON l.pid = a.pid;

-- Verificar tamaño de tablas e índices
SELECT
  table_name,
  pg_size_pretty(table_size) AS table_size,
  pg_size_pretty(indexes_size) AS indexes_size,
  pg_size_pretty(total_size) AS total_size
FROM (
  SELECT
    table_name,
    pg_table_size(table_name) AS table_size,
    pg_indexes_size(table_name) AS indexes_size,
    pg_total_relation_size(table_name) AS total_size
  FROM (
    SELECT ('"' || table_schema || '"."' || table_name || '"') AS table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
  ) AS all_tables
) AS pretty_sizes
ORDER BY total_size DESC;
```

## Mejores Prácticas

1. **Seguridad**
   - Use roles con privilegios mínimos
   - Active SSL para conexiones
   - Use consultas preparadas para evitar inyecciones SQL
   - Considere usar Row-Level Security para control de acceso granular

2. **Rendimiento**
   - Indexe columnas frecuentemente usadas en cláusulas WHERE, JOIN y ORDER BY
   - Use EXPLAIN ANALYZE para entender y optimizar planes de ejecución
   - Configure autovacuum para mantener la salud de la base de datos
   - Use vistas materializadas para consultas complejas ejecutadas frecuentemente

3. **Mantenimiento**
   - Programe copias de seguridad regulares con pg_dump
   - Configure replicación para alta disponibilidad
   - Monitoree regularmente el rendimiento con pg_stat_statements
   - Actualice regularmente a las últimas versiones menores para parches de seguridad
