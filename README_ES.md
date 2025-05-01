# MCP Database Utilities

<!-- Insignias de estado del proyecto -->
[![Estado de compilación](https://img.shields.io/github/workflow/status/donghao1393/mcp-dbutils/Quality%20Assurance?label=tests)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Cobertura](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/donghao1393/bdd0a63ec2a816539ff8c136ceb41e48/raw/coverage.json)](https://github.com/donghao1393/mcp-dbutils/actions)
[![Estado de Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=donghao1393_mcp-dbutils&metric=alert_status)](https://sonarcloud.io/dashboard?id=donghao1393_mcp-dbutils)

<!-- Insignias de versión e instalación -->
[![Versión de PyPI](https://img.shields.io/pypi/v/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![Descargas de PyPI](https://img.shields.io/pypi/dm/mcp-dbutils)](https://pypi.org/project/mcp-dbutils/)
[![Smithery](https://smithery.ai/badge/@donghao1393/mcp-dbutils)](https://smithery.ai/server/@donghao1393/mcp-dbutils)

<!-- Insignias de especificaciones técnicas -->
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Licencia](https://img.shields.io/github/license/donghao1393/mcp-dbutils)](LICENSE)
[![Estrellas de GitHub](https://img.shields.io/github/stars/donghao1393/mcp-dbutils?style=social)](https://github.com/donghao1393/mcp-dbutils/stargazers)

[English](README_EN.md) | [中文](README.md) | [Français](README_FR.md) | [العربية](README_AR.md) | [Русский](README_RU.md) | [Documentación](#documentación)

## Introducción

MCP Database Utilities es un servicio MCP todo en uno que permite a tu IA realizar análisis de datos accediendo a diversos tipos de bases de datos (SQLite, MySQL, PostgreSQL y más) con una configuración de conexión unificada de manera segura.

Piensa en ello como un puente seguro entre los sistemas de IA y tus bases de datos, permitiendo a la IA leer y analizar tus datos sin acceso directo a la base de datos o arriesgarse a modificaciones de datos.

### Características clave

- **Seguridad primero**: Operaciones estrictamente de solo lectura, sin acceso directo a la base de datos, conexiones aisladas, conectividad bajo demanda, tiempos de espera automáticos
- **Protecciones de privacidad**: Procesamiento local, exposición mínima de datos, protección de credenciales, enmascaramiento de datos sensibles
- **Soporte para múltiples bases de datos**: Conéctate a SQLite, MySQL, PostgreSQL con la misma interfaz
- **Configuración simple**: Un solo archivo YAML para todas tus conexiones de base de datos
- **Capacidades avanzadas**: Exploración de tablas, análisis de esquemas y ejecución de consultas

> 🔒 **Nota de seguridad**: MCP Database Utilities está construido con una arquitectura de seguridad primero, lo que lo hace ideal para empresas, startups e individuos que valoran la protección de datos. Aprende más sobre nuestra [arquitectura de seguridad](docs/es/technical/security.md).

## Inicio rápido

Ofrecemos múltiples métodos de instalación, incluyendo uvx, Docker y Smithery. Para pasos detallados de instalación y configuración, consulta la [Guía de instalación](docs/es/installation.md).

### Pasos básicos

1. **Instalar**: Elige tu método de instalación preferido ([instrucciones detalladas](docs/es/installation.md))
2. **Configurar**: Crea un archivo YAML con la información de conexión de tu base de datos ([guía de configuración](docs/es/configuration.md))
3. **Conectar**: Añade la configuración a tu cliente de IA
4. **Usar**: Comienza a interactuar con tus bases de datos ([guía de uso](docs/es/usage.md))

## Ejemplos de interacciones

**Tú**: "¿Puedes listar todas las tablas en mi base de datos my-postgres?"

**IA**: "Verificaré eso para ti. Aquí están las tablas en tu base de datos my-postgres:
- clientes
- productos
- pedidos
- inventario
- empleados"

**Tú**: "¿Cómo es la tabla de clientes?"

**IA**: "La tabla de clientes tiene la siguiente estructura:
- id (entero, clave primaria)
- nombre (texto)
- email (texto)
- fecha_registro (fecha)
- ultima_compra (fecha)
- total_gastado (numérico)"

**Tú**: "¿Cuántos clientes realizaron compras en el último mes?"

**IA**: "Déjame ejecutar una consulta para averiguarlo... Según los datos, 128 clientes realizaron compras en el último mes. El valor total de estas compras fue de $25,437.82."

## Herramientas disponibles

MCP Database Utilities proporciona varias herramientas que tu IA puede usar:

- **dbutils-list-connections**: Lista todas las conexiones de base de datos disponibles con información detallada, incluyendo tipo de base de datos, host, puerto y nombre de base de datos, mientras oculta información sensible como contraseñas.
- **dbutils-list-tables**: Lista todas las tablas en la conexión de base de datos especificada con nombres de tablas, URIs y descripciones disponibles, agrupadas por tipo de base de datos para fácil identificación.
- **dbutils-run-query**: Ejecuta consultas SQL de solo lectura (solo SELECT) con soporte para consultas complejas, incluyendo JOINs, GROUP BY y funciones de agregación, devolviendo resultados estructurados con nombres de columnas y filas de datos.
- **dbutils-describe-table**: Proporciona información detallada sobre la estructura de una tabla, incluyendo nombres de columnas, tipos de datos, nulabilidad, valores predeterminados y comentarios en un formato fácil de leer.
- **dbutils-get-ddl**: Recupera la declaración DDL (Lenguaje de Definición de Datos) completa para crear la tabla especificada, incluyendo todas las definiciones de columnas, restricciones e índices.
- **dbutils-list-indexes**: Lista todos los índices en la tabla especificada, incluyendo nombres de índices, tipos (único/no único), métodos de índice y columnas incluidas, agrupados por nombre de índice.
- **dbutils-get-stats**: Recupera información estadística sobre la tabla, incluyendo recuento estimado de filas, longitud promedio de fila, tamaño de datos y tamaño de índice.
- **dbutils-list-constraints**: Lista todas las restricciones en la tabla, incluyendo claves primarias, claves foráneas, restricciones únicas y restricciones de verificación, con tablas y columnas referenciadas para claves foráneas.
- **dbutils-explain-query**: Proporciona el plan de ejecución para una consulta SQL, mostrando cómo el motor de base de datos procesará la consulta, incluyendo métodos de acceso, tipos de unión y costos estimados.
- **dbutils-get-performance**: Recupera métricas de rendimiento para la conexión de base de datos, incluyendo recuento de consultas, tiempo promedio de ejecución, uso de memoria y estadísticas de errores.
- **dbutils-analyze-query**: Analiza las características de rendimiento de una consulta SQL, proporcionando plan de ejecución, tiempo real de ejecución y recomendaciones específicas de optimización.

Para descripciones detalladas y ejemplos de uso de estas herramientas, consulta la [Guía de Uso](docs/es/usage.md).

## Documentación

### Primeros pasos
- [Guía de instalación](docs/es/installation.md) - Pasos detallados de instalación e instrucciones de configuración
- [Guía de instalación específica de plataforma](docs/es/installation-platform-specific.md) - Instrucciones de instalación para diferentes sistemas operativos
- [Guía de configuración](docs/es/configuration.md) - Ejemplos de configuración de conexión de base de datos y mejores prácticas
- [Guía de uso](docs/es/usage.md) - Flujo de trabajo básico y escenarios de uso comunes

### Documentación técnica
- [Diseño de arquitectura](docs/es/technical/architecture.md) - Arquitectura del sistema y componentes
- [Arquitectura de seguridad](docs/es/technical/security.md) - Características de seguridad y mecanismos de protección
- [Guía de desarrollo](docs/es/technical/development.md) - Calidad del código y flujo de trabajo de desarrollo
- [Guía de pruebas](docs/es/technical/testing.md) - Marco de pruebas y mejores prácticas
- [Integración con SonarCloud](docs/es/technical/sonarcloud-integration.md) - Guía de integración de SonarCloud y IA

### Documentación de ejemplos
- [Ejemplos de SQLite](docs/es/examples/sqlite-examples.md) - Ejemplos de operaciones de base de datos SQLite
- [Ejemplos de PostgreSQL](docs/es/examples/postgresql-examples.md) - Ejemplos de operaciones de base de datos PostgreSQL
- [Ejemplos de MySQL](docs/es/examples/mysql-examples.md) - Ejemplos de operaciones de base de datos MySQL
- [Interacciones avanzadas con LLM](docs/es/examples/advanced-llm-interactions.md) - Ejemplos de interacciones avanzadas con varios LLM

### Soporte y comentarios
- [Issues de GitHub](https://github.com/donghao1393/mcp-dbutils/issues) - Reporta problemas o solicita características
- [Smithery](https://smithery.ai/server/@donghao1393/mcp-dbutils) - Instalación y actualizaciones simplificadas

## Historial de estrellas

[![Gráfico de historial de estrellas](https://starchart.cc/donghao1393/mcp-dbutils.svg?variant=adaptive)](https://starchart.cc/donghao1393/mcp-dbutils)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
