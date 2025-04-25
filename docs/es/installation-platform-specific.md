# Guía de Instalación Específica por Plataforma

*[English](../en/installation-platform-specific.md) | [中文](../zh/installation-platform-specific.md) | [Français](../fr/installation-platform-specific.md) | Español | [العربية](../ar/installation-platform-specific.md) | [Русский](../ru/installation-platform-specific.md)*

Este documento proporciona instrucciones detalladas de instalación para MCP Database Utilities en diferentes sistemas operativos y entornos.

## Instalación en Windows

### Requisitos Previos

- Python 3.10 o superior
- Acceso de administrador (para algunos pasos)
- Conexión a Internet (para descargar paquetes)

### Instalación de Python

1. Descargue Python desde [python.org](https://www.python.org/downloads/windows/)
2. Ejecute el instalador y asegúrese de marcar la opción "Add Python to PATH"
3. Verifique la instalación abriendo un símbolo del sistema y escribiendo:
   ```
   python --version
   ```

### Instalación de uv

1. Abra PowerShell como administrador
2. Ejecute el siguiente comando:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Verifique la instalación:
   ```
   uv --version
   ```

### Instalación de MCP Database Utilities

#### Opción 1: Instalación con uvx (Recomendada)

```powershell
# No se requiere instalación previa
# uvx maneja todo automáticamente
```

Configure su cliente de IA para usar:
```
uvx mcp-dbutils --config C:\ruta\a\config.yaml
```

#### Opción 2: Instalación Tradicional

```powershell
# Cree un entorno virtual (opcional pero recomendado)
python -m venv venv
.\venv\Scripts\activate

# Instale con uv
uv pip install mcp-dbutils
```

#### Opción 3: Instalación con Smithery

```powershell
# Asegúrese de tener Node.js instalado
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Instalación en macOS

### Requisitos Previos

- Python 3.10 o superior
- Homebrew (recomendado)
- Conexión a Internet (para descargar paquetes)

### Instalación de Python

1. Instale Homebrew si aún no lo tiene:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Instale Python:
   ```bash
   brew install python@3.10
   ```

3. Verifique la instalación:
   ```bash
   python3 --version
   ```

### Instalación de uv

1. Abra Terminal
2. Ejecute el siguiente comando:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Verifique la instalación:
   ```bash
   uv --version
   ```

### Instalación de MCP Database Utilities

#### Opción 1: Instalación con uvx (Recomendada)

```bash
# No se requiere instalación previa
# uvx maneja todo automáticamente
```

Configure su cliente de IA para usar:
```
uvx mcp-dbutils --config /ruta/a/config.yaml
```

#### Opción 2: Instalación Tradicional

```bash
# Cree un entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate

# Instale con uv
uv pip install mcp-dbutils
```

#### Opción 3: Instalación con Smithery

```bash
# Asegúrese de tener Node.js instalado
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Instalación en Linux

### Requisitos Previos

- Python 3.10 o superior
- Privilegios sudo (para algunos pasos)
- Conexión a Internet (para descargar paquetes)

### Instalación de Python

#### En Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

#### En Fedora:

```bash
sudo dnf install python3.10 python3.10-devel
```

#### En Arch Linux:

```bash
sudo pacman -S python
```

### Instalación de uv

1. Abra Terminal
2. Ejecute el siguiente comando:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Verifique la instalación:
   ```bash
   uv --version
   ```

### Instalación de MCP Database Utilities

#### Opción 1: Instalación con uvx (Recomendada)

```bash
# No se requiere instalación previa
# uvx maneja todo automáticamente
```

Configure su cliente de IA para usar:
```
uvx mcp-dbutils --config /ruta/a/config.yaml
```

#### Opción 2: Instalación Tradicional

```bash
# Cree un entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate

# Instale con uv
uv pip install mcp-dbutils
```

#### Opción 3: Instalación con Smithery

```bash
# Asegúrese de tener Node.js instalado
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Instalación en Contenedor Docker

### Requisitos Previos

- Docker instalado y funcionando
- Conexión a Internet (para descargar la imagen Docker)

### Uso de la Imagen Docker Oficial

1. Descargue la imagen Docker:
   ```bash
   docker pull mcp/dbutils
   ```

2. Ejecute el contenedor con su archivo de configuración:
   ```bash
   docker run -i --rm -v /ruta/a/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml
   ```

### Creación de una Imagen Docker Personalizada

Si necesita personalizar la imagen Docker, puede crear su propio Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir mcp-dbutils

ENTRYPOINT ["mcp-dbutils"]
CMD ["--help"]
```

Construya y ejecute su imagen personalizada:

```bash
docker build -t custom-mcp-dbutils .
docker run -i --rm -v /ruta/a/config.yaml:/app/config.yaml custom-mcp-dbutils --config /app/config.yaml
```

## Instalación Sin Conexión

Para entornos sin acceso a Internet, puede preparar una instalación sin conexión:

### Paso 1: Descarga de Paquetes (en una máquina con Internet)

```bash
# Cree un directorio para los paquetes
mkdir mcp-dbutils-offline
cd mcp-dbutils-offline

# Descargue los paquetes con sus dependencias
uv pip download mcp-dbutils -d ./packages
```

### Paso 2: Transferencia a la Máquina Sin Conexión

Transfiera el directorio `mcp-dbutils-offline` a la máquina sin conexión usando una unidad USB u otro medio.

### Paso 3: Instalación en la Máquina Sin Conexión

```bash
# Cree un entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Linux/macOS
# o
.\venv\Scripts\activate  # En Windows

# Instale desde los paquetes descargados
uv pip install --no-index --find-links=./packages mcp-dbutils
```

## Solución de Problemas

### Problema: "Command not found" después de la instalación

**Solución**:
- Asegúrese de que el directorio de instalación esté en su PATH
- En Windows, intente reiniciar el símbolo del sistema o PowerShell
- En Linux/macOS, ejecute `source ~/.bashrc` o `source ~/.zshrc`

### Problema: Errores de Dependencias

**Solución**:
- Asegúrese de tener Python 3.10 o superior
- Intente instalar con `--verbose` para ver errores detallados:
  ```
  uv pip install --verbose mcp-dbutils
  ```

### Problema: Errores de Permisos

**Solución**:
- En Windows, ejecute PowerShell como administrador
- En Linux/macOS, use `sudo` si es necesario o instale en un entorno virtual

### Problema: Errores con Docker

**Solución**:
- Verifique que Docker esté en ejecución: `docker info`
- Asegúrese de que las rutas de montaje sean correctas y accesibles
- En Linux, es posible que necesite agregar su usuario al grupo docker:
  ```
  sudo usermod -aG docker $USER
  ```
  (Cierre sesión y vuelva a iniciar sesión para que los cambios surtan efecto)

## Recursos Adicionales

- [Documentación de Python](https://docs.python.org/)
- [Documentación de Docker](https://docs.docker.com/)
- [Documentación de uv](https://github.com/astral-sh/uv)
- [Documentación de Smithery](https://smithery.ai/docs)
