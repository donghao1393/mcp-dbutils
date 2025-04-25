# Guía de Configuración

*[English](../en/configuration.md) | [中文](../zh/configuration.md) | [Français](../fr/configuration.md) | Español | [العربية](../ar/configuration.md) | [Русский](../ru/configuration.md)*

Este documento proporciona varios ejemplos de configuración para MCP Database Utilities, desde configuraciones básicas hasta escenarios avanzados, ayudándole a configurar y optimizar correctamente sus conexiones de base de datos.

## Configuración Básica

### Configuración Básica de SQLite

SQLite es una base de datos ligera basada en archivos con una configuración muy simple:

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
    # Opcional: contraseña de cifrado de la base de datos
    password: optional_encryption_password
```

### Configuración Básica de PostgreSQL

Configuración de conexión estándar de PostgreSQL:

```yaml
connections:
  my-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

### Configuración Básica de MySQL

Configuración de conexión estándar de MySQL:

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

## Configuración de Múltiples Bases de Datos

Puede definir múltiples conexiones de base de datos en el mismo archivo de configuración:

```yaml
connections:
  # Base de datos SQLite de desarrollo
  dev-db:
    type: sqlite
    path: /path/to/dev.db

  # Base de datos PostgreSQL de prueba
  test-db:
    type: postgres
    host: test-postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # Base de datos MySQL de producción
  prod-db:
    type: mysql
    host: prod-mysql.example.com
    port: 3306
    database: prod_db
    user: prod_user
    password: prod_pass
    charset: utf8mb4
```

## Configuración Avanzada

### Configuración de Estilo URL

Además de usar propiedades de configuración estándar, también puede usar URLs de base de datos para configuración parcial. La mejor práctica es poner la estructura de conexión de la base de datos en la URL, pero mantener la información sensible y los parámetros específicos separados:

**Configuración URL de PostgreSQL (Enfoque Recomendado)**:

```yaml
connections:
  # Usando URL para PostgreSQL (mejor práctica)
  postgres-url:
    type: postgres
    url: postgresql://host:5432/dbname
    user: postgres_user
    password: postgres_password
    # Otros parámetros configurados aquí
```

**Configuración URL de MySQL (Enfoque Recomendado)**:

```yaml
connections:
  # Usando URL para MySQL (mejor práctica)
  mysql-url:
    type: mysql
    url: mysql://host:3306/dbname
    user: mysql_user
    password: mysql_password
    charset: utf8mb4
```

**Estilo de Configuración URL Heredado** (no recomendado para producción):

Aunque el siguiente enfoque funciona, no se recomienda para entornos de producción debido al riesgo de errores de análisis de caracteres especiales:

```yaml
connections:
  legacy-url:
    type: postgres
    url: postgresql://user:password@host:5432/dbname?param1=value1
    # Nota: No se recomienda incluir credenciales en la URL
```

**Cuándo Usar URL vs Configuración Estándar**:
- La configuración URL es adecuada para:
  - Cuando ya tiene una cadena de conexión de base de datos
  - Necesita incluir parámetros de conexión específicos en la URL
  - Migración desde otros sistemas con cadenas de conexión
- La configuración estándar es adecuada para:
  - Estructura de configuración más clara
  - Necesidad de gestionar cada propiedad de configuración por separado
  - Más fácil de modificar parámetros individuales sin afectar la conexión general
  - Mejor seguridad y mantenibilidad

En cualquier caso, debe evitar incluir información sensible (como nombres de usuario, contraseñas) en la URL y en su lugar proporcionarlos por separado en los parámetros de configuración.

### Conexiones Seguras SSL/TLS

#### Configuración SSL de PostgreSQL

**Usando Parámetros URL para SSL**:

```yaml
connections:
  pg-ssl-url:
    type: postgres
    url: postgresql://postgres.example.com:5432/secure_db?sslmode=verify-full&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem&sslrootcert=/path/to/root.crt
    user: secure_user
    password: secure_pass
```

**Usando Sección de Configuración SSL Dedicada**:

```yaml
connections:
  pg-ssl-full:
    type: postgres
    host: secure-postgres.example.com
    port: 5432
    dbname: secure_db
    user: secure_user
    password: secure_pass
    ssl:
      mode: verify-full  # Modo de verificación más seguro
      cert: /path/to/client-cert.pem  # Certificado de cliente
      key: /path/to/client-key.pem    # Clave privada de cliente
      root: /path/to/root.crt         # Certificado CA
```

**Explicación del Modo SSL de PostgreSQL**:
- `disable`: No se usa SSL en absoluto (no recomendado para producción)
- `require`: Usar SSL pero no verificar certificado (solo cifrado, sin autenticación)
- `verify-ca`: Verificar que el certificado del servidor esté firmado por una CA de confianza
- `verify-full`: Verificar certificado del servidor y coincidencia de nombre de host (opción más segura)

#### Configuración SSL de MySQL

**Usando Parámetros URL para SSL**:

```yaml
connections:
  mysql-ssl-url:
    type: mysql
    url: mysql://mysql.example.com:3306/secure_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem&ssl-cert=/path/to/client-cert.pem&ssl-key=/path/to/client-key.pem
    user: secure_user
    password: secure_pass
```

**Usando Sección de Configuración SSL Dedicada**:

```yaml
connections:
  mysql-ssl-full:
    type: mysql
    host: secure-mysql.example.com
    port: 3306
    database: secure_db
    user: secure_user
    password: secure_pass
    charset: utf8mb4
    ssl:
      mode: verify_identity  # Modo de verificación más seguro
      ca: /path/to/ca.pem         # Certificado CA
      cert: /path/to/client-cert.pem  # Certificado de cliente
      key: /path/to/client-key.pem    # Clave privada de cliente
```

**Explicación del Modo SSL de MySQL**:
- `disabled`: No se usa SSL (no recomendado para producción)
- `preferred`: Usar SSL si está disponible, de lo contrario usar conexión no cifrada
- `required`: Se debe usar SSL, pero no verificar el certificado del servidor
- `verify_ca`: Verificar que el certificado del servidor esté firmado por una CA de confianza
- `verify_identity`: Verificar certificado del servidor y coincidencia de nombre de host (opción más segura)

### Configuración Avanzada de SQLite

**Usando Parámetros URI**:

```yaml
connections:
  sqlite-advanced:
    type: sqlite
    path: /path/to/db.sqlite?mode=ro&cache=shared&immutable=1
```

**Parámetros URI Comunes de SQLite**:
- `mode=ro`: Modo de solo lectura (opción segura)
- `cache=shared`: Modo de caché compartida, mejora el rendimiento multi-hilo
- `immutable=1`: Marcar la base de datos como inmutable, mejora el rendimiento
- `nolock=1`: Deshabilitar el bloqueo de archivos (usar solo cuando esté seguro de que no existen otras conexiones)

## Configuración Especial para Entorno Docker

Cuando se ejecuta en un contenedor Docker, conectarse a bases de datos en el host requiere una configuración especial:

### Conectando a PostgreSQL/MySQL en el Host

**En macOS/Windows**:
Use el nombre de host especial `host.docker.internal` para acceder al host Docker:

```yaml
connections:
  docker-postgres:
    type: postgres
    host: host.docker.internal  # Nombre DNS especial que apunta al host Docker
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**En Linux**:
Use la IP del puente Docker o use el modo de red host:

```yaml
connections:
  docker-mysql:
    type: mysql
    host: 172.17.0.1  # IP del puente Docker predeterminada, apunta al host
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

O use `--network="host"` al iniciar el contenedor Docker, luego use `localhost` como nombre de host.

### Mapeo de SQLite

Para SQLite, necesita mapear el archivo de base de datos en el contenedor:

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/database.db:/app/database.db \
  mcp/dbutils --config /app/config.yaml
```

Luego apunte a la ruta mapeada en su configuración:

```yaml
connections:
  docker-sqlite:
    type: sqlite
    path: /app/database.db  # Ruta dentro del contenedor, no la ruta del host
```

## Escenarios de Configuración Comunes

### Gestión Multi-Entorno

Una buena práctica es usar convenciones de nomenclatura claras para diferentes entornos:

```yaml
connections:
  # Entorno de desarrollo
  dev-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: dev_db
    user: dev_user
    password: dev_pass

  # Entorno de prueba
  test-postgres:
    type: postgres
    host: test-server.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # Entorno de producción
  prod-postgres:
    type: postgres
    host: prod-db.example.com
    port: 5432
    dbname: prod_db
    user: prod_user
    password: prod_pass
    ssl:
      mode: verify-full
      cert: /path/to/cert.pem
      key: /path/to/key.pem
      root: /path/to/root.crt
```

### Configuración Específica para Solo Lectura y Analítica

Para escenarios de análisis de datos, se recomienda usar cuentas de solo lectura y configuración optimizada:

```yaml
connections:
  analytics-mysql:
    type: mysql
    host: analytics-db.example.com
    port: 3306
    database: analytics
    user: analytics_readonly  # Usar cuenta con permisos de solo lectura
    password: readonly_pass
    charset: utf8mb4
    # Establecer tiempo de espera más largo adecuado para análisis de datos
```

## Consejos de Solución de Problemas

Si su configuración de conexión no funciona, intente:

1. **Verificar Conexión Básica**: Use el cliente nativo de la base de datos para verificar que la conexión funciona
2. **Verificar Conectividad de Red**: Asegúrese de que los puertos de red estén abiertos, los firewalls permitan el acceso
3. **Verificar Credenciales**: Confirme que el nombre de usuario y la contraseña sean correctos
4. **Problemas de Ruta**: Para SQLite, asegúrese de que la ruta exista y tenga permisos de lectura
5. **Errores SSL**: Verifique las rutas y permisos de certificados, verifique que los certificados no estén vencidos
