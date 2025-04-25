# Ejemplos de SQLite

*[English](../../en/examples/sqlite-examples.md) | [中文](../../zh/examples/sqlite-examples.md) | [Français](../../fr/examples/sqlite-examples.md) | Español | [العربية](../../ar/examples/sqlite-examples.md) | [Русский](../../ru/examples/sqlite-examples.md)*

Este documento proporciona ejemplos prácticos para trabajar con bases de datos SQLite usando MCP Database Utilities.

## Configuración Básica

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
```

## Operaciones Comunes

### Listar Tablas

**Usted**: "Lista todas las tablas en mi base de datos SQLite."

**IA**: "Aquí están las tablas en su base de datos SQLite:
- usuarios
- productos
- pedidos
- categorias"

### Ver Estructura de Tabla

**Usted**: "Muéstrame la estructura de la tabla usuarios."

**IA**: "La tabla usuarios tiene la siguiente estructura:
- id (INTEGER, PRIMARY KEY)
- username (TEXT, NOT NULL)
- email (TEXT, NOT NULL, UNIQUE)
- created_at (TIMESTAMP)
- last_login (TIMESTAMP)
- status (TEXT)"

### Consulta Básica

**Usted**: "Muéstrame los 5 principales usuarios por fecha de último inicio de sesión."

**IA**: "Aquí están los 5 principales usuarios por fecha de último inicio de sesión:

| id | username | email | last_login |
|----|----------|-------|------------|
| 42 | johndoe | john@example.com | 2023-11-25 14:32:15 |
| 17 | janedoe | jane@example.com | 2023-11-24 09:45:22 |
| 31 | bobsmith | bob@example.com | 2023-11-23 18:12:05 |
| 8 | alicejones | alice@example.com | 2023-11-22 11:30:47 |
| 53 | mikebrown | mike@example.com | 2023-11-21 16:08:33 |"

## Consultas Avanzadas

### Uniendo Tablas

**Usted**: "Muéstrame los últimos 3 pedidos con información de usuario."

**IA**: "Aquí están los últimos 3 pedidos con información de usuario:

| order_id | order_date | username | email | total_amount |
|----------|------------|----------|-------|--------------|
| 1042 | 2023-11-25 | johndoe | john@example.com | $125.99 |
| 1041 | 2023-11-24 | alicejones | alice@example.com | $89.50 |
| 1040 | 2023-11-23 | bobsmith | bob@example.com | $212.75 |"

### Funciones de Agregación

**Usted**: "¿Cuál es el monto promedio de pedido por categoría?"

**IA**: "Aquí está el monto promedio de pedido por categoría:

| categoría | monto_promedio |
|----------|----------------|
| Electrónica | $245.75 |
| Ropa | $78.30 |
| Libros | $32.50 |
| Hogar y Cocina | $124.90 |
| Deportes y Aire Libre | $156.25 |"

## Análisis de Rendimiento

### Plan de Ejecución de Consulta

**Usted**: "Explica el plan de ejecución para: SELECT * FROM pedidos WHERE user_id = 42"

**IA**: "Plan de ejecución para la consulta:
```
QUERY PLAN
------------------------------------------------------------
SEARCH TABLE pedidos USING INDEX idx_user_id (user_id=?)
```

Esta consulta usa el índice `idx_user_id` para encontrar eficientemente pedidos para user_id 42."

### Estadísticas de Tabla

**Usted**: "Obtén estadísticas para la tabla pedidos."

**IA**: "Estadísticas para la tabla pedidos:
- Recuento de filas: 1,245
- Tamaño: 2.3 MB
- Índices: 3 (clave primaria, idx_user_id, idx_order_date)
- Longitud promedio de fila: 1.9 KB"

## Trabajando con Características Específicas de SQLite

### Usando FTS (Búsqueda de Texto Completo)

**Usted**: "Busca productos que contengan 'auriculares inalámbricos'."

**IA**: "Aquí están los productos que coinciden con 'auriculares inalámbricos':

| product_id | nombre | descripción | precio |
|------------|------|-------------|-------|
| 123 | Auriculares Inalámbricos Premium | Auriculares inalámbricos con cancelación de ruido y 30 horas de batería | $199.99 |
| 145 | Auriculares Inalámbricos Deportivos | Auriculares inalámbricos resistentes al agua para deportes | $89.99 |
| 187 | Auriculares Inalámbricos Económicos | Auriculares inalámbricos asequibles con buena calidad de sonido | $49.99 |"

### Usando Funciones JSON

**Usted**: "Muéstrame usuarios con 'premium' en sus preferencias."

**IA**: "Aquí están los usuarios con 'premium' en sus preferencias:

| id | username | preferencias |
|----|----------|-------------|
| 42 | johndoe | {\"subscription\": \"premium\", \"theme\": \"dark\"} |
| 17 | janedoe | {\"subscription\": \"premium\", \"theme\": \"light\"} |
| 53 | mikebrown | {\"subscription\": \"premium\", \"theme\": \"auto\"} |"

## Solución de Problemas

### Problemas Comunes

1. **Archivo No Encontrado**
   - Asegúrese de que la ruta a su archivo de base de datos SQLite sea correcta
   - Verifique los permisos del archivo
   - Verifique que el archivo exista

2. **Base de Datos Bloqueada**
   - SQLite permite solo un escritor a la vez
   - Asegúrese de que ningún otro proceso esté escribiendo en la base de datos
   - Considere usar el modo WAL para mejor concurrencia

3. **Problemas de Rendimiento**
   - Agregue índices para columnas consultadas frecuentemente
   - Use EXPLAIN QUERY PLAN para identificar consultas lentas
   - Considere usar declaraciones preparadas para consultas repetidas
