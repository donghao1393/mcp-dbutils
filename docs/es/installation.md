# Guía de Instalación

*[English](../en/installation.md) | [中文](../zh/installation.md) | [Français](../fr/installation.md) | Español | [العربية](../ar/installation.md) | [Русский](../ru/installation.md)*

Este documento proporciona pasos simples y fáciles de seguir para instalar y configurar MCP Database Utilities, permitiendo que su asistente de IA acceda y analice sus bases de datos de manera segura.

## ¿Qué es MCP?

MCP (Model Context Protocol) es un protocolo que permite a las aplicaciones de IA (como Claude) utilizar herramientas externas. MCP Database Utilities es una de estas herramientas que permite a la IA leer el contenido de su base de datos sin modificar ningún dato.

## Antes de Comenzar

Antes de iniciar la instalación, asegúrese de tener:

- Una aplicación de IA compatible con MCP (como Claude Desktop, Cursor, etc.)
- Al menos una base de datos a la que desea que la IA acceda (SQLite, MySQL o PostgreSQL)

## Elija su Método de Instalación

Ofrecemos cuatro métodos de instalación simples. Elija el que mejor funcione para usted:

| Método de Instalación | Mejor Para | Ventajas |
|---------|---------|------|
| **Opción A: Usando uvx** | La mayoría de usuarios | Simple y rápido, recomendado |
| **Opción B: Usando Docker** | Usuarios que prefieren aplicaciones en contenedores | Entorno aislado |
| **Opción C: Usando Smithery** | Usuarios de Claude Desktop | Instalación con un clic, más fácil |
| **Opción D: Instalación Offline** | Usuarios en entornos sin internet | No se necesita conexión de red |

## Opción A: Usando uvx (Recomendado)

### Paso 1: Instalar la herramienta uv

**En Mac o Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**En Windows**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Después de la instalación, verifique que funcione escribiendo este comando en su terminal:
```bash
uv --version
```
Debería ver algo como `uv 0.5.5` en la salida.

### Paso 2: Crear un archivo de configuración de base de datos

1. Cree un archivo llamado `config.yaml` en su computadora
2. Copie el siguiente contenido en el archivo (elija el que coincida con su tipo de base de datos):

**Ejemplo de Base de Datos SQLite**:
```yaml
connections:
  my_sqlite:
    type: sqlite
    path: C:/path/to/your/database.db
```

**Ejemplo de Base de Datos PostgreSQL**:
```yaml
connections:
  my_postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**Ejemplo de Base de Datos MySQL**:
```yaml
connections:
  my_mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

> Por favor, reemplace la información de ejemplo con los detalles reales de su base de datos. Para más opciones de configuración, consulte la [Guía de Configuración](configuration.md).

### Paso 3: Configurar su aplicación de IA

#### Configuración de Claude Desktop

1. Abra la aplicación Claude Desktop
2. Haga clic en el ícono de configuración en la parte inferior izquierda
3. Seleccione "MCP Servers"
4. Haga clic en "Add Server"
5. Agregue la siguiente configuración:

```json
"dbutils": {
  "command": "uvx",
  "args": [
    "mcp-dbutils",
    "--config",
    "C:/Users/SuNombreDeUsuario/config.yaml"
  ]
}
```

> Importante: Reemplace `C:/Users/SuNombreDeUsuario/config.yaml` con la ruta real al archivo de configuración que creó en el Paso 2.

#### Configuración de Cursor

1. Abra la aplicación Cursor
2. Vaya a "Settings" → "MCP"
3. Haga clic en "Add MCP Server"
4. Complete la siguiente información:
   - Name: `Database Utility MCP`
   - Type: `Command` (predeterminado)
   - Command: `uvx mcp-dbutils --config C:/Users/SuNombreDeUsuario/config.yaml`

> Importante: Reemplace `C:/Users/SuNombreDeUsuario/config.yaml` con la ruta real al archivo de configuración que creó en el Paso 2.

## Opción B: Usando Docker

### Paso 1: Instalar Docker

Si no tiene Docker instalado, descárguelo e instálelo desde [docker.com](https://www.docker.com/products/docker-desktop/).

### Paso 2: Crear un archivo de configuración de base de datos

Igual que el Paso 2 en la Opción A, cree un archivo `config.yaml`.

### Paso 3: Configurar su aplicación de IA

#### Configuración de Claude Desktop

1. Abra la aplicación Claude Desktop
2. Haga clic en el ícono de configuración en la parte inferior izquierda
3. Seleccione "MCP Servers"
4. Haga clic en "Add Server"
5. Agregue la siguiente configuración:

```json
"dbutils": {
  "command": "docker",
  "args": [
    "run",
    "-i",
    "--rm",
    "-v",
    "C:/Users/SuNombreDeUsuario/config.yaml:/app/config.yaml",
    "mcp/dbutils",
    "--config",
    "/app/config.yaml"
  ]
}
```

> Importante: Reemplace `C:/Users/SuNombreDeUsuario/config.yaml` con la ruta real al archivo de configuración que creó en el Paso 2.

#### Configuración de Cursor

1. Abra la aplicación Cursor
2. Vaya a "Settings" → "MCP"
3. Haga clic en "Add MCP Server"
4. Complete la siguiente información:
   - Name: `Database Utility MCP`
   - Type: `Command` (predeterminado)
   - Command: `docker run -i --rm -v C:/Users/SuNombreDeUsuario/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml`

> Importante: Reemplace `C:/Users/SuNombreDeUsuario/config.yaml` con la ruta real al archivo de configuración que creó en el Paso 2.

## Opción C: Usando Smithery (Un Clic para Claude)

Si usa Claude Desktop, este es el método de instalación más simple:

1. Asegúrese de tener Node.js instalado
2. Abra una terminal o símbolo del sistema
3. Ejecute el siguiente comando:

```bash
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

4. Siga las instrucciones en pantalla para completar la instalación

Este método maneja automáticamente toda la configuración, por lo que no necesita editar manualmente ningún archivo.

## Opción D: Instalación Offline

Si necesita usar la herramienta en un entorno sin acceso a Internet, o desea usar una versión específica:

### Paso 1: Obtener el código fuente

En un entorno con acceso a Internet:
1. Descargue el código fuente desde GitHub: `git clone https://github.com/donghao1393/mcp-dbutils.git`
2. O descargue un archivo zip desde la [página de Releases](https://github.com/donghao1393/mcp-dbutils/releases)
3. Copie los archivos descargados a su entorno offline

### Paso 2: Crear un archivo de configuración de base de datos

Igual que el Paso 2 en la Opción A, cree un archivo `config.yaml`.

### Paso 3: Configurar su aplicación de IA

#### Configuración de Claude Desktop

1. Abra la aplicación Claude Desktop
2. Haga clic en el ícono de configuración en la parte inferior izquierda
3. Seleccione "MCP Servers"
4. Haga clic en "Add Server"
5. Agregue la siguiente configuración:

```json
"dbutils": {
  "command": "uv",
  "args": [
    "--directory",
    "C:/Users/SuNombreDeUsuario/mcp-dbutils",
    "run",
    "mcp-dbutils",
    "--config",
    "C:/Users/SuNombreDeUsuario/config.yaml"
  ]
}
```

> Importante: Reemplace las rutas con las rutas reales a su directorio de código fuente y archivo de configuración.

## Verificando su Instalación

Después de completar la instalación, verifiquemos que todo funcione correctamente:

### Probando la Conexión

1. Abra su aplicación de IA (Claude Desktop o Cursor)
2. Pregunte a su IA: **"¿Puedes verificar si puedes conectarte a mi base de datos?"**
3. Si está configurado correctamente, la IA responderá que se ha conectado exitosamente a su base de datos

### Pruebe Comandos Simples

Una vez conectado, puede probar estos comandos simples:

- **"Lista todas las tablas en mi base de datos"**
- **"Describe la estructura de la tabla clientes"**
- **"Consulta los 5 productos más caros en la tabla productos"**

## Solución de Problemas Comunes

### Problema 1: La IA No Puede Encontrar el Comando uvx

**Síntoma**: La IA responde con "comando uvx no encontrado" o error similar

**Solución**:
1. Confirme que uv está instalado correctamente: Ejecute `uv --version` en su terminal
2. Si está instalado pero sigue obteniendo errores, podría ser un problema de variable de entorno:
   - En Windows, verifique si la variable de entorno PATH incluye el directorio de instalación de uv
   - En Mac/Linux, podría necesitar reiniciar su terminal o ejecutar `source ~/.bashrc` o `source ~/.zshrc`

### Problema 2: No Puede Conectarse a la Base de Datos

**Síntoma**: La IA informa que no puede conectarse a su base de datos

**Solución**:
1. **Verifique si su base de datos está ejecutándose**: Asegúrese de que su servidor de base de datos esté iniciado
2. **Verifique la información de conexión**: Revise cuidadosamente el host, puerto, nombre de usuario y contraseña en su config.yaml
3. **Verifique la configuración de red**:
   - Si usa Docker, para bases de datos locales, use `host.docker.internal` como nombre de host
   - Confirme que los firewalls no estén bloqueando la conexión

### Problema 3: Error de Ruta del Archivo de Configuración

**Síntoma**: La IA informa que no puede encontrar el archivo de configuración

**Solución**:
1. **Use rutas absolutas**: Asegúrese de usar rutas absolutas completas en la configuración de su aplicación de IA
2. **Verifique los permisos del archivo**: Asegúrese de que el archivo de configuración sea legible por el usuario actual
3. **Evite caracteres especiales**: No use caracteres especiales o espacios en la ruta, o use comillas si es necesario

### Problema 4: Problemas de Ruta de Base de Datos SQLite

**Síntoma**: La conexión falla cuando usa SQLite

**Solución**:
1. **Verifique la ruta del archivo**: Asegúrese de que el archivo de base de datos SQLite exista y la ruta sea correcta
2. **Verifique los permisos**: Asegúrese de que el archivo de base de datos tenga permisos de lectura
3. **Al usar Docker**: Asegúrese de haber mapeado correctamente la ruta del archivo SQLite

## Actualizando a la Última Versión

Las actualizaciones regulares proporcionan nuevas características y correcciones de seguridad. Elija el método de actualización que coincida con su método de instalación:

### Actualización de Opción A (uvx)

Cuando ejecuta MCP Database Utilities usando el comando `uvx` (por ejemplo, `uvx mcp-dbutils`), automáticamente usa la última versión sin requerir actualizaciones manuales.

Si está usando el método de instalación tradicional (no el comando `uvx`), puede actualizar manualmente con:

```bash
uv pip install -U mcp-dbutils
```

### Actualización de Opción B (Docker)

```bash
docker pull mcp/dbutils:latest
```

### Actualización de Opción C (Smithery)

```bash
npx -y @smithery/cli update @donghao1393/mcp-dbutils
```

### Actualización de Opción D (Offline)

1. Descargue la última versión del código fuente en un entorno con acceso a Internet
2. Reemplace los archivos de código fuente en su entorno offline

## Ejemplos de Interacciones

Después de una instalación exitosa, puede probar estas conversaciones de ejemplo:

**Usted**: ¿Puedes listar todas las tablas en mi base de datos?

**IA**: Voy a revisar su base de datos. Aquí están las tablas en su base de datos:
- clientes
- productos
- pedidos
- inventario

**Usted**: ¿Cómo es la estructura de la tabla clientes?

**IA**: La tabla clientes tiene la siguiente estructura:
- id (entero, clave primaria)
- nombre (texto)
- email (texto)
- fecha_registro (fecha)
- ultima_compra (fecha)

**Usted**: ¿Cuántos clientes realizaron compras en el último mes?

**IA**: Déjame ejecutar una consulta para averiguarlo... Según los datos, 28 clientes realizaron compras en el último mes. El valor total de estas compras fue $15,742.50.
