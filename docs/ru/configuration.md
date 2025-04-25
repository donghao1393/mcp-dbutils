# Руководство по конфигурации

*[English](../en/configuration.md) | [中文](../zh/configuration.md) | [Français](../fr/configuration.md) | [Español](../es/configuration.md) | [العربية](../ar/configuration.md) | Русский*

Этот документ предоставляет различные примеры конфигурации для MCP Database Utilities, от базовых конфигураций до продвинутых сценариев, помогая вам правильно настроить и оптимизировать ваши подключения к базам данных.

## Базовая конфигурация

### Базовая конфигурация SQLite

SQLite — это легкая файловая база данных с очень простой конфигурацией:

```yaml
connections:
  my-sqlite:
    type: sqlite
    path: /path/to/database.db
    # Опционально: пароль шифрования базы данных
    password: optional_encryption_password
```

### Базовая конфигурация PostgreSQL

Стандартная конфигурация подключения PostgreSQL:

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

### Базовая конфигурация MySQL

Стандартная конфигурация подключения MySQL:

```yaml
connections:
  my-mysql:
    type: mysql
    host: localhost
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
    charset: utf8mb4  # Рекомендуется для полной поддержки Unicode
```

## Конфигурация нескольких баз данных

Вы можете определить несколько подключений к базам данных в одном файле конфигурации:

```yaml
connections:
  # База данных SQLite для разработки
  dev-db:
    type: sqlite
    path: /path/to/dev.db

  # База данных PostgreSQL для тестирования
  test-db:
    type: postgres
    host: test-postgres.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # База данных MySQL для продакшена
  prod-db:
    type: mysql
    host: prod-mysql.example.com
    port: 3306
    database: prod_db
    user: prod_user
    password: prod_pass
    charset: utf8mb4
```

## Продвинутая конфигурация

### Конфигурация в стиле URL

Помимо использования стандартных свойств конфигурации, вы также можете использовать URL-адреса баз данных для частичной конфигурации. Лучшая практика — поместить структуру подключения к базе данных в URL, но хранить конфиденциальную информацию и специфические параметры отдельно:

**Конфигурация URL PostgreSQL (Рекомендуемый подход)**:

```yaml
connections:
  # Использование URL для PostgreSQL (лучшая практика)
  postgres-url:
    type: postgres
    url: postgresql://host:5432/dbname
    user: postgres_user
    password: postgres_password
    # Другие параметры настраиваются здесь
```

**Конфигурация URL MySQL (Рекомендуемый подход)**:

```yaml
connections:
  # Использование URL для MySQL (лучшая практика)
  mysql-url:
    type: mysql
    url: mysql://host:3306/dbname
    user: mysql_user
    password: mysql_password
    charset: utf8mb4
```

**Устаревший стиль конфигурации URL** (не рекомендуется для продакшена):

Хотя следующий подход работает, он не рекомендуется для продакшен-сред из-за риска ошибок при разборе специальных символов:

```yaml
connections:
  legacy-url:
    type: postgres
    url: postgresql://user:password@host:5432/dbname?param1=value1
    # Примечание: Не рекомендуется включать учетные данные в URL
```

**Когда использовать URL vs Стандартную конфигурацию**:
- Конфигурация URL подходит для:
  - Когда у вас уже есть строка подключения к базе данных
  - Необходимость включить специфические параметры подключения в URL
  - Миграция с других систем со строками подключения
- Стандартная конфигурация подходит для:
  - Более четкая структура конфигурации
  - Необходимость управлять каждым свойством конфигурации отдельно
  - Легче изменять отдельные параметры без влияния на общее подключение
  - Лучшая безопасность и поддерживаемость

В любом случае, вы должны избегать включения конфиденциальной информации (такой как имена пользователей, пароли) в URL и вместо этого предоставлять их отдельно в параметрах конфигурации.

### Безопасные соединения SSL/TLS

#### Конфигурация SSL PostgreSQL

**Использование параметров URL для SSL**:

```yaml
connections:
  pg-ssl-url:
    type: postgres
    url: postgresql://postgres.example.com:5432/secure_db?sslmode=verify-full&sslcert=/path/to/cert.pem&sslkey=/path/to/key.pem&sslrootcert=/path/to/root.crt
    user: secure_user
    password: secure_pass
```

**Использование выделенного раздела конфигурации SSL**:

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
      mode: verify-full  # Наиболее безопасный режим проверки
      cert: /path/to/client-cert.pem  # Сертификат клиента
      key: /path/to/client-key.pem    # Приватный ключ клиента
      root: /path/to/root.crt         # Сертификат CA
```

**Объяснение режима SSL PostgreSQL**:
- `disable`: SSL не используется вообще (не рекомендуется для продакшена)
- `require`: Использовать SSL, но не проверять сертификат (только шифрование, без аутентификации)
- `verify-ca`: Проверить, что сертификат сервера подписан доверенным CA
- `verify-full`: Проверить сертификат сервера и соответствие имени хоста (наиболее безопасный вариант)

#### Конфигурация SSL MySQL

**Использование параметров URL для SSL**:

```yaml
connections:
  mysql-ssl-url:
    type: mysql
    url: mysql://mysql.example.com:3306/secure_db?ssl-mode=verify_identity&ssl-ca=/path/to/ca.pem&ssl-cert=/path/to/client-cert.pem&ssl-key=/path/to/client-key.pem
    user: secure_user
    password: secure_pass
```

**Использование выделенного раздела конфигурации SSL**:

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
      mode: verify_identity  # Наиболее безопасный режим проверки
      ca: /path/to/ca.pem         # Сертификат CA
      cert: /path/to/client-cert.pem  # Сертификат клиента
      key: /path/to/client-key.pem    # Приватный ключ клиента
```

**Объяснение режима SSL MySQL**:
- `disabled`: SSL не используется (не рекомендуется для продакшена)
- `preferred`: Использовать SSL, если доступно, иначе использовать незашифрованное соединение
- `required`: SSL должен использоваться, но не проверять сертификат сервера
- `verify_ca`: Проверить, что сертификат сервера подписан доверенным CA
- `verify_identity`: Проверить сертификат сервера и соответствие имени хоста (наиболее безопасный вариант)

### Продвинутая конфигурация SQLite

**Использование параметров URI**:

```yaml
connections:
  sqlite-advanced:
    type: sqlite
    path: /path/to/db.sqlite?mode=ro&cache=shared&immutable=1
```

**Распространенные параметры URI SQLite**:
- `mode=ro`: Режим только для чтения (безопасный вариант)
- `cache=shared`: Режим общего кэша, улучшает производительность многопоточности
- `immutable=1`: Пометить базу данных как неизменяемую, улучшает производительность
- `nolock=1`: Отключить блокировку файлов (использовать только когда уверены, что нет других соединений)

## Специальная конфигурация для среды Docker

При запуске в контейнере Docker, подключение к базам данных на хосте требует специальной конфигурации:

### Подключение к PostgreSQL/MySQL на хосте

**На macOS/Windows**:
Используйте специальное имя хоста `host.docker.internal` для доступа к хосту Docker:

```yaml
connections:
  docker-postgres:
    type: postgres
    host: host.docker.internal  # Специальное DNS-имя, указывающее на хост Docker
    port: 5432
    dbname: my_database
    user: postgres_user
    password: postgres_password
```

**На Linux**:
Используйте IP-адрес моста Docker или используйте режим сети хоста:

```yaml
connections:
  docker-mysql:
    type: mysql
    host: 172.17.0.1  # IP-адрес моста Docker по умолчанию, указывает на хост
    port: 3306
    database: my_database
    user: mysql_user
    password: mysql_password
```

Или используйте `--network="host"` при запуске контейнера Docker, затем используйте `localhost` в качестве имени хоста.

### Монтирование SQLite

Для SQLite вам нужно смонтировать файл базы данных в контейнер:

```bash
docker run -i --rm \
  -v /path/to/config.yaml:/app/config.yaml \
  -v /path/to/database.db:/app/database.db \
  mcp/dbutils --config /app/config.yaml
```

Затем укажите смонтированный путь в вашей конфигурации:

```yaml
connections:
  docker-sqlite:
    type: sqlite
    path: /app/database.db  # Путь внутри контейнера, а не путь хоста
```

## Распространенные сценарии конфигурации

### Управление несколькими средами

Хорошая практика — использовать четкие соглашения об именовании для разных сред:

```yaml
connections:
  # Среда разработки
  dev-postgres:
    type: postgres
    host: localhost
    port: 5432
    dbname: dev_db
    user: dev_user
    password: dev_pass

  # Тестовая среда
  test-postgres:
    type: postgres
    host: test-server.example.com
    port: 5432
    dbname: test_db
    user: test_user
    password: test_pass

  # Продакшен-среда
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

### Специфическая конфигурация для только чтения и аналитики

Для сценариев анализа данных рекомендуется использовать учетные записи только для чтения и оптимизированную конфигурацию:

```yaml
connections:
  analytics-mysql:
    type: mysql
    host: analytics-db.example.com
    port: 3306
    database: analytics
    user: analytics_readonly  # Использовать учетную запись с разрешениями только для чтения
    password: readonly_pass
    charset: utf8mb4
    # Установить более длительный тайм-аут, подходящий для анализа данных
```

## Советы по устранению неполадок

Если ваша конфигурация подключения не работает, попробуйте:

1. **Проверить базовое соединение**: Используйте нативный клиент базы данных, чтобы проверить, что соединение работает
2. **Проверить сетевую связь**: Убедитесь, что сетевые порты открыты, брандмауэры разрешают доступ
3. **Проверить учетные данные**: Подтвердите, что имя пользователя и пароль верны
4. **Проблемы с путем**: Для SQLite убедитесь, что путь существует и имеет разрешения на чтение
5. **Ошибки SSL**: Проверьте пути и разрешения сертификатов, убедитесь, что сертификаты не просрочены
