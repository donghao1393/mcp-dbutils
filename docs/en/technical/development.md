# Development Guide

*English | [中文](../../zh/technical/development.md) | [Français](../../fr/technical/development.md) | [Español](../../es/technical/development.md) | [العربية](../../ar/technical/development.md) | [Русский](../../ru/technical/development.md)*

This document provides detailed information about the development process, code standards, and best practices for contributing to the MCP Database Utilities project.

## Code Quality

### Quality Gates
We use SonarCloud to maintain high code quality standards. All pull requests must pass the following quality gates:

- Code Coverage: ≥ 80%
- Code Quality:
  * No blocking or critical issues
  * Fewer than 10 major issues
  * Code duplication < 3%
- Security:
  * No security vulnerabilities
  * No security hotspots

### Automated Checks
Our CI/CD pipeline automatically performs:
1. Complete test suite execution
2. Code coverage analysis
3. SonarCloud static code analysis
4. Quality gate validation

Pull requests that don't meet these standards will automatically be blocked from merging.

### Code Style

We use Ruff for code style checking and formatting to ensure code quality and consistency.

#### Basic Rules

1. **Line Length**: Maximum 88 characters
2. **Indentation**: 4 spaces (no tabs)
3. **Quotes**: Double quotes for strings
4. **Naming Conventions**:
   - Class names: CamelCase (e.g., `DatabaseHandler`)
   - Functions and variables: snake_case (e.g., `execute_query`)
   - Constants: UPPERCASE with underscores (e.g., `MAX_CONNECTIONS`)
   - Private methods and attributes: Single underscore prefix (e.g., `_connect`)

#### Import Rules

1. Import order:
   - Standard library
   - Third-party libraries
   - Local application/library

2. One blank line between each import group

#### Code Organization

1. Two blank lines between class definitions
2. One blank line between method definitions
3. Related code should be grouped together

#### Ruff Rule Sets

This project uses the following Ruff rule sets:

- `E`: pycodestyle errors
- `F`: pyflakes
- `I`: isort
- `N`: pep8-naming
- `UP`: pyupgrade
- `B`: flake8-bugbear
- `C4`: flake8-comprehensions
- `SIM`: flake8-simplify
- `T20`: flake8-print

### Local Development

#### Installing Tools

```bash
# Install Ruff
uv pip install ruff

# Install pre-commit
uv pip install pre-commit
pre-commit install
```

#### Code Checking

```bash
# Check the entire project
ruff check .

# Automatically fix issues
ruff check --fix .
```

#### Code Formatting

```bash
# Check formatting
ruff format --check .

# Automatically format code
ruff format .
```

#### Using pre-commit

The project has pre-commit hooks configured to automatically run Ruff checks and formatting when committing code.

```bash
# Run pre-commit manually
pre-commit run --all-files
```

#### Testing and Coverage

```bash
# Run tests with coverage
pytest --cov=src/mcp_dbutils --cov-report=xml:coverage.xml tests/
```

#### Other Development Tools

1. Use SonarLint in your IDE to catch issues early
2. View SonarCloud analysis in PR comments

### Common Issues

#### How to Ignore Specific Rules?

Use comments to ignore specific rules for a line:

```python
# Ignore the entire line
some_code_here  # noqa

# Ignore a specific rule
some_code_here  # noqa: E501

# Ignore multiple rules
some_code_here  # noqa: E501, F401
```

#### How to Ignore Rules at Project Level?

Add to the `[tool.ruff]` section in `pyproject.toml`:

```toml
ignore = ["E501"]
```

#### How to Handle Third-Party Import Issues?

If you have issues with third-party import ordering, configure in `pyproject.toml`:

```toml
[tool.ruff.isort]
known-third-party = ["third_party_lib"]
```

### CI/CD Integration

GitHub Actions automatically runs Ruff checks and formatting on every push and PR to ensure code compliance.

#### Automated Workflow

Each PR triggers the following automated checks:

1. **Code Style Verification**: Uses Ruff to verify code adheres to project style guidelines
2. **Unit Tests**: Runs all tests to ensure functionality works as expected
3. **Code Coverage**: Ensures test coverage meets requirements
4. **SonarCloud Analysis**: Performs in-depth code quality and security analysis

#### How to View CI Results

1. Check the "Checks" tab on the GitHub PR page
2. Click on specific checks to view detailed information
3. For SonarCloud analysis, click the link to view the full report

## Version Updates

MCP Database Utilities is regularly updated with new features, performance improvements, and bug fixes. In most cases, the update process is managed automatically by your MCP client, requiring no manual intervention.

### Getting the Latest Version

- **Using MCP Clients**: Most MCP clients (like Claude Desktop, Cursor, etc.) will automatically update to the latest version

- **Manually Checking for Updates**:
  - Visit the [GitHub repository](https://github.com/donghao1393/mcp-dbutils) to see the latest version
  - Read the [release notes](https://github.com/donghao1393/mcp-dbutils/releases) to learn about new features and changes

- **Issue Reporting**:
  - If you encounter issues after updating, please [submit an issue](https://github.com/donghao1393/mcp-dbutils/issues)