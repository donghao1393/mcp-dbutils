# Руководство по установке для конкретных платформ

*[English](../en/installation-platform-specific.md) | [中文](../zh/installation-platform-specific.md) | [Français](../fr/installation-platform-specific.md) | [Español](../es/installation-platform-specific.md) | [العربية](../ar/installation-platform-specific.md) | Русский*

Этот документ содержит подробные инструкции по установке MCP Database Utilities на различных операционных системах и средах.

## Установка в Windows

### Предварительные требования

- Python 3.10 или выше
- Права администратора (для некоторых шагов)
- Подключение к интернету (для загрузки пакетов)

### Установка Python

1. Загрузите Python с [python.org](https://www.python.org/downloads/windows/)
2. Запустите установщик и убедитесь, что отмечена опция "Add Python to PATH"
3. Проверьте установку, открыв командную строку и введя:
   ```
   python --version
   ```

### Установка uv

1. Откройте PowerShell от имени администратора
2. Выполните следующую команду:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. Проверьте установку:
   ```
   uv --version
   ```

### Установка MCP Database Utilities

#### Вариант 1: Установка с помощью uvx (Рекомендуется)

```powershell
# Предварительная установка не требуется
# uvx автоматически обрабатывает всё
```

Настройте вашего ИИ-клиента для использования:
```
uvx mcp-dbutils --config C:\путь\к\config.yaml
```

#### Вариант 2: Традиционная установка

```powershell
# Создайте виртуальное окружение (опционально, но рекомендуется)
python -m venv venv
.\venv\Scripts\activate

# Установите с помощью uv
uv pip install mcp-dbutils
```

#### Вариант 3: Установка с помощью Smithery

```powershell
# Убедитесь, что у вас установлен Node.js
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Установка в macOS

### Предварительные требования

- Python 3.10 или выше
- Homebrew (рекомендуется)
- Подключение к интернету (для загрузки пакетов)

### Установка Python

1. Установите Homebrew, если у вас его еще нет:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Установите Python:
   ```bash
   brew install python@3.10
   ```

3. Проверьте установку:
   ```bash
   python3 --version
   ```

### Установка uv

1. Откройте Terminal
2. Выполните следующую команду:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Проверьте установку:
   ```bash
   uv --version
   ```

### Установка MCP Database Utilities

#### Вариант 1: Установка с помощью uvx (Рекомендуется)

```bash
# Предварительная установка не требуется
# uvx автоматически обрабатывает всё
```

Настройте вашего ИИ-клиента для использования:
```
uvx mcp-dbutils --config /путь/к/config.yaml
```

#### Вариант 2: Традиционная установка

```bash
# Создайте виртуальное окружение (опционально, но рекомендуется)
python3 -m venv venv
source venv/bin/activate

# Установите с помощью uv
uv pip install mcp-dbutils
```

#### Вариант 3: Установка с помощью Smithery

```bash
# Убедитесь, что у вас установлен Node.js
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Установка в Linux

### Предварительные требования

- Python 3.10 или выше
- Права sudo (для некоторых шагов)
- Подключение к интернету (для загрузки пакетов)

### Установка Python

#### В Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev
```

#### В Fedora:

```bash
sudo dnf install python3.10 python3.10-devel
```

#### В Arch Linux:

```bash
sudo pacman -S python
```

### Установка uv

1. Откройте Terminal
2. Выполните следующую команду:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Проверьте установку:
   ```bash
   uv --version
   ```

### Установка MCP Database Utilities

#### Вариант 1: Установка с помощью uvx (Рекомендуется)

```bash
# Предварительная установка не требуется
# uvx автоматически обрабатывает всё
```

Настройте вашего ИИ-клиента для использования:
```
uvx mcp-dbutils --config /путь/к/config.yaml
```

#### Вариант 2: Традиционная установка

```bash
# Создайте виртуальное окружение (опционально, но рекомендуется)
python3 -m venv venv
source venv/bin/activate

# Установите с помощью uv
uv pip install mcp-dbutils
```

#### Вариант 3: Установка с помощью Smithery

```bash
# Убедитесь, что у вас установлен Node.js
npx -y @smithery/cli install @donghao1393/mcp-dbutils --client claude
```

## Установка в Docker-контейнере

### Предварительные требования

- Установленный и работающий Docker
- Подключение к интернету (для загрузки Docker-образа)

### Использование официального Docker-образа

1. Загрузите Docker-образ:
   ```bash
   docker pull mcp/dbutils
   ```

2. Запустите контейнер с вашим файлом конфигурации:
   ```bash
   docker run -i --rm -v /путь/к/config.yaml:/app/config.yaml mcp/dbutils --config /app/config.yaml
   ```

### Создание пользовательского Docker-образа

Если вам нужно настроить Docker-образ, вы можете создать свой собственный Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir mcp-dbutils

ENTRYPOINT ["mcp-dbutils"]
CMD ["--help"]
```

Соберите и запустите ваш пользовательский образ:

```bash
docker build -t custom-mcp-dbutils .
docker run -i --rm -v /путь/к/config.yaml:/app/config.yaml custom-mcp-dbutils --config /app/config.yaml
```

## Офлайн-установка

Для сред без доступа к интернету вы можете подготовить офлайн-установку:

### Шаг 1: Загрузка пакетов (на машине с интернетом)

```bash
# Создайте директорию для пакетов
mkdir mcp-dbutils-offline
cd mcp-dbutils-offline

# Загрузите пакеты с зависимостями
uv pip download mcp-dbutils -d ./packages
```

### Шаг 2: Перенос на офлайн-машину

Перенесите директорию `mcp-dbutils-offline` на офлайн-машину с помощью USB-накопителя или другого носителя.

### Шаг 3: Установка на офлайн-машине

```bash
# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # В Linux/macOS
# или
.\venv\Scripts\activate  # В Windows

# Установите из загруженных пакетов
uv pip install --no-index --find-links=./packages mcp-dbutils
```

## Устранение неполадок

### Проблема: "Command not found" после установки

**Решение**:
- Убедитесь, что директория установки находится в вашем PATH
- В Windows попробуйте перезапустить командную строку или PowerShell
- В Linux/macOS выполните `source ~/.bashrc` или `source ~/.zshrc`

### Проблема: Ошибки зависимостей

**Решение**:
- Убедитесь, что у вас Python 3.10 или выше
- Попробуйте установить с флагом `--verbose` для просмотра подробных ошибок:
  ```
  uv pip install --verbose mcp-dbutils
  ```

### Проблема: Ошибки прав доступа

**Решение**:
- В Windows запустите PowerShell от имени администратора
- В Linux/macOS используйте `sudo` при необходимости или установите в виртуальное окружение

### Проблема: Ошибки с Docker

**Решение**:
- Проверьте, что Docker запущен: `docker info`
- Убедитесь, что пути монтирования правильные и доступны
- В Linux возможно потребуется добавить вашего пользователя в группу docker:
  ```
  sudo usermod -aG docker $USER
  ```
  (Выйдите из системы и войдите снова, чтобы изменения вступили в силу)

## Дополнительные ресурсы

- [Документация Python](https://docs.python.org/)
- [Документация Docker](https://docs.docker.com/)
- [Документация uv](https://github.com/astral-sh/uv)
- [Документация Smithery](https://smithery.ai/docs)
