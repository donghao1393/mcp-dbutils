# Guía de Uso

*[English](../en/usage.md) | [中文](../zh/usage.md) | [Français](../fr/usage.md) | Español | [العربية](../ar/usage.md) | [Русский](../ru/usage.md)*

Este documento proporciona instrucciones detalladas para usar MCP Database Utilities, ayudándole a aprovechar al máximo sus capacidades para el análisis de datos con IA.

## Flujo de Trabajo Básico

El flujo de trabajo básico para usar MCP Database Utilities es el siguiente:

1. **Configurar Conexiones de Base de Datos**: Defina sus conexiones de base de datos en el archivo `config.yaml`
2. **Iniciar el Servicio MCP**: Lance el servicio a través de la configuración de su cliente de IA
3. **Interactuar con la IA**: Haga preguntas sobre sus bases de datos usando lenguaje natural
4. **Ver Resultados**: La IA ejecutará las consultas necesarias y presentará los resultados en un formato fácil de entender

## Herramientas Disponibles

MCP Database Utilities proporciona varias herramientas que su IA puede usar:

### dbutils-list-connections

Lista todas las conexiones de base de datos disponibles definidas en su configuración.

**Ejemplo de Interacción**:

**Usted**: "¿Qué conexiones de base de datos tengo disponibles?"

**IA**: "Verificaré sus conexiones de base de datos disponibles. Esto es lo que encontré:

1. **postgres-db**
   - Tipo: PostgreSQL
   - Host: localhost
   - Base de datos: analytics
   - Usuario: analyst

2. **sqlite-db**
   - Tipo: SQLite
   - Ruta: /path/to/database.db

3. **mysql-db**
   - Tipo: MySQL
   - Host: db.example.com
   - Base de datos: customer_data
   - Usuario: reader"

### dbutils-list-tables

Lista todas las tablas en la base de datos especificada.

**Ejemplo de Interacción**:

**Usted**: "Lista todas las tablas en mi base de datos postgres."

**IA**: "Verificaré eso para usted. Aquí están las tablas en su base de datos postgres:
- clientes
- productos
- pedidos
- inventario
- empleados"

### dbutils-run-query

Ejecuta consultas SQL en la base de datos especificada (solo operaciones SELECT).

**Ejemplo de Interacción**:

**Usted**: "Consulta el número de clientes que se registraron en los últimos 30 días."

**IA**: "Verificaré eso para usted. Según los datos, ha habido 42 nuevos registros de clientes en los últimos 30 días."

### dbutils-get-stats

Obtiene estadísticas sobre una tabla, como recuento de filas, tamaño y estadísticas de columnas.

**Ejemplo de Interacción**:

**Usted**: "Obtén estadísticas para la tabla productos."

**IA**: "Aquí están las estadísticas para la tabla productos:
- Total de filas: 1,245
- Tamaño de la tabla: 2.3 MB
- Estadísticas de columnas:
  * product_id: 1,245 valores únicos
  * categoría: 8 categorías distintas
  * precio: promedio $45.99, mín $5.99, máx $299.99"

### dbutils-list-constraints

Lista las restricciones para una tabla, como claves primarias, claves foráneas, etc.

**Ejemplo de Interacción**:

**Usted**: "Muestra las restricciones para la tabla pedidos."

**IA**: "La tabla pedidos tiene las siguientes restricciones:
- Clave primaria: order_id
- Clave foránea: customer_id referencia clientes(id)
- Clave foránea: product_id referencia productos(id)
- Restricción de verificación: order_amount > 0"

### dbutils-explain-query

Obtiene el plan de ejecución de la consulta y estimaciones de costo.

**Ejemplo de Interacción**:

**Usted**: "Explica el plan de ejecución para esta consulta: SELECT * FROM pedidos WHERE customer_id = 123"

**IA**: "El plan de ejecución para esta consulta es:
1. Escaneo de índice: usando el índice customer_id_idx
2. Costo estimado: 12.5
3. Filas estimadas: 8
4. Condición de filtro: customer_id = 123"

### dbutils-get-performance

Obtiene métricas de rendimiento de la base de datos.

**Ejemplo de Interacción**:

**Usted**: "Obtén métricas de rendimiento para la base de datos."

**IA**: "Métricas de rendimiento actuales de la base de datos:
- Tiempo de ejecución de consulta: 45ms promedio
- Tasa de aciertos de caché: 87%
- Conexiones activas: 3
- Tasa de error reciente: 0.2%"

### dbutils-analyze-query

Analiza el rendimiento de consultas SQL y proporciona sugerencias de optimización.

**Ejemplo de Interacción**:

**Usted**: "Analiza esta consulta: SELECT * FROM pedidos JOIN clientes ON pedidos.customer_id = clientes.id WHERE order_date > '2023-01-01'"

**IA**: "Resultados del análisis de consulta:
1. Problema de rendimiento: Usar SELECT * recupera columnas innecesarias
2. Índice faltante: No hay índice en la columna order_date
3. Sugerencias de optimización:
   - Seleccione solo las columnas necesarias
   - Agregue un índice en la columna order_date
   - Considere agregar una cláusula LIMIT para restringir el recuento de resultados"

## Escenarios de Uso Comunes

### 1. Exploración de Datos

**Usted**: "Quiero entender la estructura de mi base de datos."

**IA**: "Puedo ayudarte a explorar la estructura de tu base de datos. Déjame listar todas las tablas, y luego puedes elegir una para aprender más sobre su estructura."

**Usted**: "Bien, lista todas las tablas."

**IA**: "Tu base de datos contiene las siguientes tablas:
- clientes
- productos
- pedidos
- inventario
- empleados

¿Sobre qué tabla te gustaría saber más?"

**Usted**: "Cuéntame sobre la estructura de la tabla clientes."

**IA**: "La tabla clientes tiene la siguiente estructura:
- id (entero, clave primaria)
- nombre (varchar(100), no nulo)
- email (varchar(100), único, no nulo)
- fecha_registro (fecha, no nulo)
- ultimo_login (timestamp)
- estado (enum: 'activo', 'inactivo', 'suspendido')"

### 2. Análisis de Datos

**Usted**: "Analiza las tendencias de ventas durante los últimos 6 meses."

**IA**: "Analizaré las tendencias de ventas durante los últimos 6 meses. Déjame ejecutar algunas consultas..."

[La IA ejecuta múltiples consultas, analizando datos de ventas]

**IA**: "Basado en el análisis de los últimos 6 meses:
1. Ventas totales: $1,245,678, un aumento del 15% respecto a los 6 meses anteriores
2. Producto más vendido: Producto X, representando el 23% de las ventas totales
3. Períodos pico de ventas: viernes y sábados, representando el 45% de las ventas totales
4. Tasa de retención de clientes: 78%, un aumento del 5% respecto a los 6 meses anteriores"

### 3. Análisis entre Bases de Datos

**Usted**: "Compara la estructura de la tabla usuarios entre las bases de datos de producción y prueba."

**IA**: "Compararé la estructura de la tabla usuarios entre las dos bases de datos..."

[La IA consulta ambas bases de datos para las estructuras de tabla]

**IA**: "Diferencias en la estructura de la tabla usuarios entre las bases de datos de producción y prueba:
1. Producción tiene una columna adicional 'last_login_ip' (varchar(45))
2. La columna 'email' de la base de datos de prueba no tiene una restricción única
3. Producción tiene un índice adicional: idx_user_status
4. La base de datos de prueba carece de la restricción de clave foránea: fk_user_role"

## Mejores Prácticas

### Optimización de Consultas

1. **Limitar el Tamaño del Conjunto de Resultados**: Use cláusulas LIMIT para restringir el número de filas devueltas
2. **Seleccionar Solo Columnas Necesarias**: Evite usar SELECT *
3. **Usar Columnas Indexadas**: Use columnas con índices en cláusulas WHERE
4. **Evitar Cálculos Complejos**: Mueva cálculos complejos a la capa de aplicación

### Recomendaciones de Seguridad

1. **Usar Cuentas de Solo Lectura**: Cree cuentas de base de datos dedicadas de solo lectura para acceso de IA
2. **Limitar el Acceso a Tablas**: Otorgue acceso solo a las tablas necesarias
3. **Usar SSL/TLS**: Habilite el cifrado para conexiones remotas de base de datos
4. **Rotar Contraseñas Regularmente**: Cambie las contraseñas de la base de datos periódicamente

### Optimización de Rendimiento

1. **Configuración del Pool de Conexiones**: Ajuste el tamaño del pool de conexiones según su uso
2. **Configuración de Tiempo de Espera de Consulta**: Establezca duraciones razonables de tiempo de espera de consulta
3. **Caché de Resultados**: Considere el almacenamiento en caché para datos consultados frecuentemente
4. **Monitorear el Rendimiento**: Verifique regularmente las métricas de rendimiento para identificar posibles problemas

## Solución de Problemas

Si encuentra problemas durante el uso, consulte la sección de solución de problemas en la [Guía de Instalación](installation.md) o consulte la [Documentación Técnica](technical/architecture.md) para obtener información más detallada.
