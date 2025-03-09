# CHANGELOG


## v0.7.0 (2025-03-09)

### Documentation

- Update README with list_tables tool information
  ([`f3a2592`](https://github.com/donghao1393/mcp-dbutils/commit/f3a259200bbf18aaebbf6d4511a18d35246f5044))

### Features

- Add database type prefix to list_tables tool response
  ([#10](https://github.com/donghao1393/mcp-dbutils/pull/10),
  [`e32ce1f`](https://github.com/donghao1393/mcp-dbutils/commit/e32ce1f2502f24d111643d7233f0fdd420238bd7))

添加数据库类型前缀到list_tables工具的返回结果中，使LLM能够知道当前操作的数据库类型， 便于后续操作。格式与错误信息保持一致，使用[数据库类型]前缀。

Fixes #9


## v0.6.0 (2025-03-08)

### Documentation

- Add SQLite JDBC URL configuration documentation
  ([#6](https://github.com/donghao1393/mcp-dbutils/pull/6),
  [`7d7ca8b`](https://github.com/donghao1393/mcp-dbutils/commit/7d7ca8bc7d4047a6c45dc3b8c6106e1fcbdd16d0))

- Add SQLite JDBC URL examples and explanation - Update configuration format description - Keep
  Chinese and English documentation in sync

Part of #4

### Features

- **tool**: Add list_tables tool for database exploration
  ([#8](https://github.com/donghao1393/mcp-dbutils/pull/8),
  [`6808c08`](https://github.com/donghao1393/mcp-dbutils/commit/6808c0868c8959450a9cfdcdf79a0af53bf22933))

* feat(tool): add list_tables tool for database exploration

This commit adds a new list_tables tool that allows LLMs to explore database tables without knowing
  the specific database type, leveraging the existing get_tables abstraction.

Fixes #7

* test(tool): add integration tests for list_tables tool

* test: add integration tests for list_tables tool

This commit: - Adds test for list_tables tool functionality with both PostgreSQL and SQLite - Adds
  test for error cases - Uses proper ClientSession setup for MCP testing

* fix(test): update test assertions for list_tables tool errors

- Fix incorrect error handling assertions - Fix indentation issues in test file - Use try-except
  pattern for error testing

* fix(test): update error handling in list_tables tests

- Use MCP Error type instead of ConfigurationError - Fix indentation issues - Improve error
  assertions

* fix(test): correct McpError import path

* fix(test): use correct import path for McpError

* fix(test): use try-except for error testing instead of pytest.raises

* test: skip unstable error test for list_tables tool


## v0.5.0 (2025-03-02)

### Documentation

- Add JDBC URL configuration documentation
  ([`a1b5f4b`](https://github.com/donghao1393/mcp-dbutils/commit/a1b5f4b424cec0df239bed65705aaac7c3e9072a))

- Add JDBC URL configuration examples to English and Chinese docs - Document secure credential
  handling approach - Update configuration format descriptions

Part of feature #2

### Features

- **config**: Add JDBC URL support for SQLite
  ([#5](https://github.com/donghao1393/mcp-dbutils/pull/5),
  [`9feb1e8`](https://github.com/donghao1393/mcp-dbutils/commit/9feb1e8c7e38a8e4e3c0f63c81a72f4a4edd05b5))

- Add JDBC URL parsing for SQLite configuration - Support SQLite specific URL format and parameters
  - Keep credentials separate from URL - Complete test coverage for new functionality

Part of #4


## v0.4.0 (2025-03-01)

### Features

- **config**: Add JDBC URL support for PostgreSQL
  ([#3](https://github.com/donghao1393/mcp-dbutils/pull/3),
  [`4f148f3`](https://github.com/donghao1393/mcp-dbutils/commit/4f148f31d5dc623b8b39201f0270d8f523e65238))

- Add JDBC URL parsing with strict security measures - Require credentials to be provided separately
  - Implement validation for all required parameters - Add comprehensive test coverage

Closes #2


## v0.3.0 (2025-02-16)

### Bug Fixes

- Fix pkg_meta reference error in DatabaseServer
  ([`9bcc607`](https://github.com/donghao1393/mcp-dbutils/commit/9bcc607378df09fee8ef301c1ce0247f419c2dab))

- Move pkg_meta initialization before its usage - Add comment to clarify the purpose of pkg_meta -
  Fix the variable reference error that caused server startup failure

- Fix prompts/list timeout by using correct decorator pattern
  ([`227f86d`](https://github.com/donghao1393/mcp-dbutils/commit/227f86db4c050439a382118df1bc62944f35aea4))

- Update Server initialization with version - Simplify list_prompts handler to return raw data - Add
  comprehensive error handling in tests - Add debug logging for better traceability

- Unify logger naming across the project
  ([`088e60b`](https://github.com/donghao1393/mcp-dbutils/commit/088e60becb7112dc0a5da256b56d0f79ed1db223))

- Use package metadata for logger names - Add consistent naming hierarchy: - Root: mcp-dbutils -
  Server: mcp-dbutils.server - Handler: mcp-dbutils.handler.<database> - Database:
  mcp-dbutils.db.<type> - Remove hardcoded server names

- Unify prompts handler registration and remove duplicate init options
  ([`6031592`](https://github.com/donghao1393/mcp-dbutils/commit/60315922b052f252005ed77fd3978d8cff085056))

- Use package metadata for server name and version
  ([`7f48a6d`](https://github.com/donghao1393/mcp-dbutils/commit/7f48a6df50830d58c534495fc7bfc9198e9fbcc5))

- Replace hardcoded server name and version with values from pyproject.toml - Add importlib.metadata
  to read package information - Ensure consistent versioning across the project

### Build System

- Simplify semantic-release configuration
  ([`0f37153`](https://github.com/donghao1393/mcp-dbutils/commit/0f37153a0d7205238d0f43c16c97a390a3e368df))

- Remove __version__ variable reference - Change build command to use uv build - Keep version
  management in pyproject.toml only

### Code Style

- Unify log timestamp format with MCP framework
  ([`c341fb1`](https://github.com/donghao1393/mcp-dbutils/commit/c341fb1d05144c5c925fed25bfcd69be55ee7803))

- Use milliseconds precision in log timestamps to match MCP framework
  ([`2aae2fd`](https://github.com/donghao1393/mcp-dbutils/commit/2aae2fd06bf9b505105fd6b0671d70ba7dfef0f5))

### Continuous Integration

- Add automatic release
  ([`b69e242`](https://github.com/donghao1393/mcp-dbutils/commit/b69e2429857824f0807eb76baccbbdf855c89e45))

- Add GitHub Actions workflow for automatic releases - Configure release triggers - Set up
  permissions - Use python-semantic-release action

- Add uv installation to release workflow
  ([`62e0362`](https://github.com/donghao1393/mcp-dbutils/commit/62e036254cc1af6d1a1a3028838652365a528c53))

- Install uv before running semantic-release - Add uv binary to GitHub PATH - Ensure build command
  can be executed

- Improve release workflow
  ([`07128a0`](https://github.com/donghao1393/mcp-dbutils/commit/07128a0ea7687963531e1aada24cc4083540272f))

- Separate version determination and build steps - Use actions/setup-python for Python environment -
  Disable automatic build in semantic-release - Add manual build step using uv - Fix invalid action
  parameters

- Improve release workflow reliability
  ([`4dac367`](https://github.com/donghao1393/mcp-dbutils/commit/4dac36749917b0d3fec94de5bcce1b5b0295e94f))

- Disable build in semantic-release - Add debug command to verify uv installation - Keep using uv
  for package building - Ensure PATH is properly set

- Integrate PyPI publishing into release workflow
  ([`2ebd3f3`](https://github.com/donghao1393/mcp-dbutils/commit/2ebd3f327748fc78dd7e33e366517120260b3d3b))

- Add upload_to_pypi option to semantic-release action - Enable build in semantic-release - Remove
  separate publish workflow - Simplify release process

- Update publish workflow trigger
  ([`26a6d79`](https://github.com/donghao1393/mcp-dbutils/commit/26a6d79eb8940cde6fb61ebe601754a1d8f22f0b))

- Add 'created' event type to release trigger - Support automatic PyPI publishing when
  semantic-release creates a release - Keep 'published' event for manual releases

- Update release workflow for trusted publishing
  ([`8297cb8`](https://github.com/donghao1393/mcp-dbutils/commit/8297cb88b496c55d1f84355ed1a015ebf80a2c42))

- Add PyPI environment configuration - Use correct PyPI publish action version - Configure trusted
  publishing permissions - Add PyPI project URL

### Documentation

- Unify server name in configuration examples
  ([`5380898`](https://github.com/donghao1393/mcp-dbutils/commit/538089864e1cef72b0560ff369f30530f4358944))

- Change server name from 'dbutils' to 'mcp-dbutils' in all examples - Keep consistent with package
  name and version in pyproject.toml - Update both English and Chinese documentation

### Features

- Add database type to error messages
  ([`cf8d53b`](https://github.com/donghao1393/mcp-dbutils/commit/cf8d53baaee247fa6313ab6d0766144f9a3f0024))

- Add database type to query results
  ([`0cebfd9`](https://github.com/donghao1393/mcp-dbutils/commit/0cebfd99ffc9201c82a85d0b8e82ba59fa4a958e))

- Add version info to startup log
  ([`dc06741`](https://github.com/donghao1393/mcp-dbutils/commit/dc06741fce536884c1aeebd19838877c5901a546))


## v0.2.11 (2025-02-15)

### Chores

- Bump version to 0.2.11
  ([`96b023f`](https://github.com/donghao1393/mcp-dbutils/commit/96b023ff6bae3a643401b639c86403e7ac31df07))

### Features

- Implement basic prompts support and list handler
  ([`397e71a`](https://github.com/donghao1393/mcp-dbutils/commit/397e71abca7286626c4eec4482e13ead83871e3a))


## v0.2.10 (2025-02-15)

### Documentation

- Update CHANGELOG for version 0.2.10
  ([`f3a6d4e`](https://github.com/donghao1393/mcp-dbutils/commit/f3a6d4ef0ce8c5fcbb0abf9b0b210447c40ce2c4))

### Features

- Add resource monitoring system
  ([`f3ff859`](https://github.com/donghao1393/mcp-dbutils/commit/f3ff859a57c7bb046725a6ee9dd746e06bb488ff))

- Add ResourceStats for resource usage tracking - Improve database handlers using template method
  pattern - Implement connection lifecycle monitoring - Add error pattern analysis - Output
  monitoring data through stderr

### Testing

- Add tests for resource monitoring system
  ([`ab9a644`](https://github.com/donghao1393/mcp-dbutils/commit/ab9a644bdae750831a9792bda157813eb9ab5ed1))

- Add unit tests for ResourceStats - Add integration tests for monitoring - Adjust base handler for
  better testability


## v0.2.9 (2025-02-15)

### Bug Fixes

- Fix logger function calls
  ([`9b9fe45`](https://github.com/donghao1393/mcp-dbutils/commit/9b9fe45b60c74c7e14d7978b011f5c8b2399892d))

- Update logger calls to match create_logger function interface - Fix debug log calls in get_handler
  method

- Fix logging and variable initialization
  ([`8f68320`](https://github.com/donghao1393/mcp-dbutils/commit/8f68320f13b7e5ca9bf6bb669a0212d0f705367b))

- Rename log to logger in DatabaseServer for consistency - Initialize handler variable before try
  block to avoid UnboundLocalError - Fix logger reference in cleanup code

- Update handlers to use custom exceptions
  ([`02eb55c`](https://github.com/donghao1393/mcp-dbutils/commit/02eb55c8e4305043b09d8dc1ee4ece78a50c187c))

- Update PostgreSQL handler to use DatabaseError - Update SQLite handler to use DatabaseError - Add
  specific error messages for non-SELECT queries - Improve error handling and logging

### Documentation

- Update changelog for v0.2.9
  ([`0ccc28e`](https://github.com/donghao1393/mcp-dbutils/commit/0ccc28e926e54d7fad84f74dce36fcad75bfd7f0))

### Features

- Optimize database type handling and error system
  ([`045b62d`](https://github.com/donghao1393/mcp-dbutils/commit/045b62d9a325304248252a86294766debc97590e))

- Remove redundant type detection based on path/dbname - Use explicit 'type' field from
  configuration - Add custom exception hierarchy - Enhance logging system

### Testing

- Update test cases for custom exceptions
  ([`93ef088`](https://github.com/donghao1393/mcp-dbutils/commit/93ef0889e00b37aaeedc83f4e3ba8debcb897100))

- Update test_postgres.py to use DatabaseError - Update test_sqlite.py to use DatabaseError - Fix
  error message assertions for non-SELECT queries


## v0.2.8 (2025-02-15)

### Bug Fixes

- Properly remove all await on mcp_config
  ([`6153277`](https://github.com/donghao1393/mcp-dbutils/commit/6153277f06f404fbd8b8cd851f54024d706b4c05))

- Remove await on mcp_config in tests
  ([`e917226`](https://github.com/donghao1393/mcp-dbutils/commit/e917226b5dd23c6eb07200912e7d25f6c73135a2))

- Fix type error 'dict' object is not an async iterator - Update both postgres and sqlite tests -
  Remove unnecessary awaits on mcp_config fixture

- Remove custom event_loop fixture
  ([`159f9e9`](https://github.com/donghao1393/mcp-dbutils/commit/159f9e9b86c7979061ffca3cf466ae81f642d67a))

- Remove custom event_loop fixture to use pytest-asyncio's default - Revert pyproject.toml changes
  to minimize modifications - Fix pytest-asyncio deprecation warning

- Use pytest_asyncio.fixture for async fixtures
  ([`ea08512`](https://github.com/donghao1393/mcp-dbutils/commit/ea0851208b5c84331df50c6a1261acc24dbe7070))

- Replace @pytest.fixture with @pytest_asyncio.fixture for async fixtures - Keep original
  @pytest.fixture for non-async event_loop - Fix pytest-asyncio deprecation warnings

### Chores

- Bump version to 0.2.8
  ([`d72cf52`](https://github.com/donghao1393/mcp-dbutils/commit/d72cf5272324cdb5164291b91139e537a07980db))

- Update version in pyproject.toml - Add 0.2.8 changelog entry for test improvements - Document
  pytest-asyncio configuration changes

- Configure pytest-asyncio fixture loop scope
  ([`d8ca223`](https://github.com/donghao1393/mcp-dbutils/commit/d8ca22318609cff81fa2b1bd0a308cf97d3a7558))

- Set asyncio_mode to strict - Set asyncio_default_fixture_loop_scope to function - Fix
  pytest-asyncio configuration warning

- Configure pytest-asyncio mode to auto
  ([`7898f61`](https://github.com/donghao1393/mcp-dbutils/commit/7898f61b960f74c4a3ca42366eb6004a6ca6d070))

- Add pytest config to remove asyncio warning - Set asyncio_mode to auto in tool.pytest.ini_options


## v0.2.7 (2025-02-15)

### Bug Fixes

- Add venv creation in CI workflow
  ([`386faec`](https://github.com/donghao1393/mcp-dbutils/commit/386faec3213a7cd4ce7e14a43225f005f3f28702))

- Update coverage badge configuration
  ([`c6bc9bd`](https://github.com/donghao1393/mcp-dbutils/commit/c6bc9bdee4006fc8dd2d3e4dcf9111ce4ad104b0))

- Update to dynamic-badges-action v1.7.0 - Ensure integer percentage value - Add proper quotes to
  parameters

### Features

- Add coverage badge to README
  ([`20435d8`](https://github.com/donghao1393/mcp-dbutils/commit/20435d87c657413d656cf61abb5e16bcf6fc0300))

- Added coverage badge generation in CI workflow - Added coverage badge to README - Updated
  CHANGELOG.md

- Add Github Actions workflow for automated testing
  ([`355a863`](https://github.com/donghao1393/mcp-dbutils/commit/355a863193ead9d21d928c21453e64c67e71d760))

- Added GitHub Actions workflow for test automation - Added PostgreSQL service in CI environment -
  Added detailed test and coverage reporting - Bump version to 0.2.7


## v0.2.6 (2025-02-12)

### Features

- Add test coverage reporting
  ([`93fe2f7`](https://github.com/donghao1393/mcp-dbutils/commit/93fe2f73dc472c8e8b5e7eb0a1b65879c806aa8a))

- Added pytest-cov for test coverage tracking - Added .coveragerc configuration - HTML coverage
  report generation - Updated .gitignore for coverage files - Updated CHANGELOG.md - Bump version to
  0.2.6


## v0.2.5 (2025-02-12)

### Documentation

- Enhance Docker documentation with database connection details
  ([`af42c97`](https://github.com/donghao1393/mcp-dbutils/commit/af42c97259eb9a5f5f2d135f8bac9690029fa843))

- Add examples for SQLite database file mapping - Document host PostgreSQL connection from container
  - Provide configuration examples for different OS environments - Add notes about
  host.docker.internal and network settings

- Show real-time chart on readme
  ([`704e5fd`](https://github.com/donghao1393/mcp-dbutils/commit/704e5fde808b996f00b51c1f534073e262c94384))

- Update changelog for v0.2.5
  ([`cb71c83`](https://github.com/donghao1393/mcp-dbutils/commit/cb71c831193c7b0758592075271d90ff48b00c94))

### Features

- Add initial automated tests
  ([`935a77b`](https://github.com/donghao1393/mcp-dbutils/commit/935a77b0d5076fe141a92128eeabc249ff3489c8))

- Add integration tests for PostgreSQL and SQLite handlers: * Table listing and schema querying *
  SELECT query execution and result formatting * Non-SELECT query rejection * Error handling for
  invalid queries - Configure test fixtures and environments in conftest.py - Set up pytest
  configurations in pyproject.toml - Update .gitignore to exclude memory-bank folder for cline

Tests verify core functionality while adhering to read-only requirements.


## v0.2.4 (2025-02-09)

### Documentation

- Major documentation improvements and version 0.2.4
  ([`7a9404a`](https://github.com/donghao1393/mcp-dbutils/commit/7a9404ad513d4b1f65f9c74f6a3eac0ea43058c9))

- Unified server configuration name to "dbutils" - Added architecture diagrams in both English and
  Chinese - Enhanced installation instructions with environment variables - Added contributing
  guidelines - Added acknowledgments section - Updated badges and improved formatting - Bump version
  to 0.2.4


## v0.2.3 (2025-02-09)

### Bug Fixes

- Remove uv cache dependency in GitHub Actions
  ([`a68f32e`](https://github.com/donghao1393/mcp-dbutils/commit/a68f32e5515ca6b6253442d74a5b9112e7ebf852))

- Remove cache-dependency-glob parameter - Disable uv cache to avoid dependency on uv.lock file

### Chores

- Bump version to 0.2.3
  ([`771e01e`](https://github.com/donghao1393/mcp-dbutils/commit/771e01efcf8ecb32c85b133836d5f179a0f2ce08))

- Update version in pyproject.toml - Add version 0.2.3 to CHANGELOG.md - Document installation
  guides, internationalization, and CI/CD additions

### Continuous Integration

- Add PyPI publishing workflow
  ([`ae5f334`](https://github.com/donghao1393/mcp-dbutils/commit/ae5f334190091207302a258311172804fd25ac16))

- Create .github/workflows/publish.yml - Configure uv environment using astral-sh/setup-uv@v4 - Set
  up automatic build and PyPI publishing - Enable trusted publishing mechanism

### Documentation

- Add MIT license and update project metadata
  ([`f98e656`](https://github.com/donghao1393/mcp-dbutils/commit/f98e656804d279bb53e193bfa87bfd1cd240e0db))

- Update installation guide and add English README
  ([`a4e60e0`](https://github.com/donghao1393/mcp-dbutils/commit/a4e60e0e792e34a4f327fe8a49e1a24a430b2abb))

- Add installation methods (uvx/pip/docker) - Update configuration examples for each installation
  method - Create English README with badges - Update project name to mcp-dbutils - Add
  cross-references between Chinese and English docs

- Update version to 0.2.2 and add CHANGELOG
  ([`381c69b`](https://github.com/donghao1393/mcp-dbutils/commit/381c69bf31af5f58d96f871de0088214cc77ca48))

- 添加中文readme文档
  ([`a3737b9`](https://github.com/donghao1393/mcp-dbutils/commit/a3737b995857b414c5ba40f1958f2b7b9b2aa65d))

- 添加README_CN.md详细说明项目功能和使用方法 - 重点解释抽象层设计理念和架构 - 包含配置示例和使用示范 - 提供完整的API文档


## v0.2.2 (2025-02-09)

### Bug Fixes

- Add missing Path import in sqlite server
  ([`fb35c1a`](https://github.com/donghao1393/mcp-dbutils/commit/fb35c1a56531456ca27319922b20efe14381b38d))

- Add pathlib import for Path usage in SQLite server - Fix code formatting

- Automatic database type detection from config
  ([`9b69882`](https://github.com/donghao1393/mcp-dbutils/commit/9b698824acc721cd697325ff0c601e11cd68ef33))

- Remove --type argument and detect db type from config - Unify configuration handling for both
  postgres and sqlite - Detect db type based on config parameters - Update SqliteServer to match
  PostgresServer interface

### Features

- Add explicit database type declaration and awareness
  ([`2d47804`](https://github.com/donghao1393/mcp-dbutils/commit/2d47804ca917e2f59b0832a7a6c92789fc97f0b8))

1. Add required 'type' field to configs to explicitly declare database type 2. Standardize field
  naming, rename 'db_path' to 'path' 3. Include database type and config name in query results 4.
  Restructure response format to unify normal results and error messages

This change enables LLMs to be aware of the database type in use, allowing them to auto-correct when
  incorrect SQL syntax is detected.

- Add password support for sqlite databases
  ([`537f1dc`](https://github.com/donghao1393/mcp-dbutils/commit/537f1dc96291ed57dbe7a52c9c7a80a868270152))

- Support password-protected SQLite databases in config - Use URI connection string for SQLite with
  password - Update connection handling and parameter passing - Add password masking in logs

- Remove required --database argument and enhance logging
  ([`9b49ac7`](https://github.com/donghao1393/mcp-dbutils/commit/9b49ac70e88a8c1d0469cdb36ae8608fd01ccaaa))

- Remove mandatory --database argument - Add connection status monitoring for all databases - Add
  automatic retry mechanism with configurable interval - Add MCP_DB_RETRY_INTERVAL environment
  variable (default: 1800s) - Add proper MCP_DEBUG support - Remove duplicated code - Improve
  logging for connection status changes

- Standardize logging
  ([`df264b5`](https://github.com/donghao1393/mcp-dbutils/commit/df264b55aed6341778f860e05072306cbb24388d))

- Use standardized logging mechanism from log.py

- **sqlite**: Add support for dynamic database switching
  ([`3f71de0`](https://github.com/donghao1393/mcp-dbutils/commit/3f71de0d220eca8252f325b264ccaa401fd71646))

- Add config_path parameter to SQLite server initialization - Add optional database parameter to
  query tool - Implement dynamic database switching in call_tool method - Keep interface consistent
  with PostgreSQL server

### Refactoring

- Redesign database server architecture for dynamic database switching
  ([`7f0a7b9`](https://github.com/donghao1393/mcp-dbutils/commit/7f0a7b92561baf357b67aa5596b6842659a934bb))

- Add DatabaseHandler base class for individual database connections - Move database operations from
  server to handlers - Implement on-demand database handler creation and cleanup - Simplify server
  initialization and configuration - Make database parameter required in query tool - Remove the
  remaining mcp_postgres directories and files

- Remove default database connection behavior
  ([`45fe01c`](https://github.com/donghao1393/mcp-dbutils/commit/45fe01c1ae27cde43843e410c45826565a18fe50))

- Remove default database concept from base implementation - Require explicit database specification
  for all operations - Convert PostgreSQL handler from connection pool to per-operation connections
  - Remove immediate connection testing in handlers - Fix resource cleanup in PostgreSQL handler


## v0.2.1 (2025-02-09)

### Bug Fixes

- Correct stdio transport initialization in base class
  ([`e9558c2`](https://github.com/donghao1393/mcp-dbutils/commit/e9558c20523d157461054442f8e3dedfb4cb930e))

- Remove non-existent create_stdio_transport method - Use stdio_server directly from
  mcp.server.stdio

### Features

- Add base classes and shared configurations
  ([`bd82bfc`](https://github.com/donghao1393/mcp-dbutils/commit/bd82bfc1a5145df4664758b87c35ecd917f99f1a))

- Add DatabaseServer abstract base class - Add DatabaseConfig abstract base class - Update main
  entry point to support multiple database types - Implement shared configuration utilities

- Add sqlite database support
  ([`7d0afb3`](https://github.com/donghao1393/mcp-dbutils/commit/7d0afb37d9711c627761699fe04185e1735969b0))

- Add SqliteConfig for SQLite configuration - Add SqliteServer implementation with basic query
  features - Support table schema inspection and listing - Match existing PostgreSQL feature set
  where applicable

### Refactoring

- Update postgres code to use base classes
  ([`51146f4`](https://github.com/donghao1393/mcp-dbutils/commit/51146f4882ff028705565ba8410f4bbd6c61c67e))

- Inherit PostgresConfig from base DatabaseConfig - Implement abstract methods in PostgresServer -
  Move postgres-specific code to postgres module - Update connection and query handling


## v0.2.0 (2025-02-08)

### Refactoring

- Rename project to mcp-dbutils and restructure directories
  ([`ddf3cea`](https://github.com/donghao1393/mcp-dbutils/commit/ddf3cea41d9368eed11cb5b7a3551b1abd058c9e))

- Rename project from mcp-postgres to mcp-dbutils - Update project description to reflect
  multi-database support - Create directories for postgres and sqlite modules - Move existing files
  to new structure


## v0.1.1 (2025-02-08)


## v0.1.0 (2025-02-08)

### Bug Fixes

- Adjust database connection handling
  ([`060354a`](https://github.com/donghao1393/mcp-dbutils/commit/060354a5f681ba67da46488705f877a8ac9fc45f))

- Split connection parameters to fix VPN connection issue - Refactor connection pool creation based
  on working example - Add better error logging for connection failures - Remove trailing spaces

- Correct logger function usage
  ([`cbace7c`](https://github.com/donghao1393/mcp-dbutils/commit/cbace7cf8226d87c36bc5bf3aadda383e0f1abff))

- Fix logger function calls to match the custom logger implementation - Change logger.warning/warn
  to direct function calls with level parameter - Maintain consistent logging format across the
  application

This fixes the AttributeError related to logger function calls

- Correct package installation and command line args
  ([`dfba347`](https://github.com/donghao1393/mcp-dbutils/commit/dfba34759393090c4fa728b4a72ad2d34d18f70c))

- Add proper pyproject.toml configuration - Fix module import path issues - Update argument handling
  in server

- Remove required db-name parameter and add auto-selection
  ([`482cfa3`](https://github.com/donghao1393/mcp-dbutils/commit/482cfa336e31f417187c255ebbcaa45c1a8ba4e9))

- Remove required flag from db-name argument - Add auto-selection of first available database when
  db-name not specified - Keep connection check for all configured databases - Add logging for
  database connection status - Maintain backwards compatibility with manual db selection

### Features

- Add connection check for all configured databases
  ([`162b5ba`](https://github.com/donghao1393/mcp-dbutils/commit/162b5baabe851f690406a60b4f349abb402bfc7d))

- Add connection check for all databases at startup - Continue if some databases fail but at least
  one succeeds - Add detailed connection status logging - Make database name parameter required -
  Improve error messages with connection status details

- Initialize Postgres MCP server
  ([`f91a8bc`](https://github.com/donghao1393/mcp-dbutils/commit/f91a8bc6d16a2d53bdf53ccc05229cade8e9e573))

- Support local host override for VPN environments - Add connection pool management - Implement
  schema inspection and read-only query tools - Add configuration separation for better
  maintainability

- Support multiple database configurations in YAML
  ([`cdeaa02`](https://github.com/donghao1393/mcp-dbutils/commit/cdeaa024eac5469caeb978d0ab455bb264006c4b))

- Restructure YAML format to support multiple database targets - Add database selection by name
  (dev-db, test-db etc) - Support default database configuration - Add validation for database
  configuration selection

### Refactoring

- Combine database tools into single query_db tool
  ([`78437c7`](https://github.com/donghao1393/mcp-dbutils/commit/78437c79ec3f1da65e3e96622f1df02c9b7d56da))

- Merge database profile selection and SQL query into one tool - Add database_profile as required
  parameter for query_db tool - Remove separate profile selection step - Simplify tool interaction
  flow - Add proper error handling and validation

- Combine database tools into single query_db tool
  ([`602cbd8`](https://github.com/donghao1393/mcp-dbutils/commit/602cbd88407d7faf86ec97d18665ee449f500e61))

- Merge database profile selection and SQL query into one tool - Add database_profile as required
  parameter for query_db tool - Remove separate profile selection step - Simplify tool interaction
  flow - Add proper error handling and validation

This change simplifies the tool interface while maintaining explicit database selection requirement.

- Remove default database config
  ([`9ceaa2f`](https://github.com/donghao1393/mcp-dbutils/commit/9ceaa2f7eefceb0b423325f30b6ec181126cd91f))

- Remove default database configuration from YAML - Make database name parameter mandatory - Add
  available database names in error message - Simplify configuration structure

This change enforces explicit database selection for better clarity and prevents accidental use of
  wrong database environments.

- Reorganize project structure
  ([`dc2eace`](https://github.com/donghao1393/mcp-dbutils/commit/dc2eace23b0a5f23227a7d7599d2bec2836a6338))

- Rename package from 'postgres' to 'mcp_postgres' - Add logging support - Improve code organization

- Simplify and improve server code
  ([`c56a0a0`](https://github.com/donghao1393/mcp-dbutils/commit/c56a0a011052d4419e5dd4ed1b9173a37fff35c1))

- Merge duplicate tool handlers into a single unified handler - Add YAML configuration support with
  multiple database profiles - Improve connection management with proper pool handling - Add masked
  logging for sensitive connection information - Refactor command line arguments for better
  usability

- Split database tools and enforce explicit database selection
  ([`2d6bfa3`](https://github.com/donghao1393/mcp-dbutils/commit/2d6bfa3e0779ef42e07dbc8884f2153230ad4f5c))

- Add set_database_profile tool with proper decorator - Split handle_call_tool into separate
  handlers for each tool - Add validation for database selection before SQL execution - Update tool
  handlers to return proper MCP response types - Add current database profile tracking

- Support YAML config for database connection
  ([`35ac49c`](https://github.com/donghao1393/mcp-dbutils/commit/35ac49c7d9a93e0d5bbd9d741a5660cbc73004d0))

- Add YAML config support as an alternative to database URL - Implement PostgresConfig class with
  both YAML and URL parsing - Use anyio for better async compatibility - Keep backward compatibility
  with URL-based configuration - Improve connection parameter handling for special characters
