# Development Guide

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
We use Ruff for code style checking and formatting:

All code must follow our style guide:
- Line length: 88 characters
- Indentation: 4 spaces
- Quotes: Double quotes
- Naming: PEP8 conventions

For detailed guidelines, see [STYLE_GUIDE.md](../../../docs/STYLE_GUIDE.md).

### Local Development
To check code quality locally:
1. Run tests with coverage:
   ```bash
   pytest --cov=src/mcp_dbutils --cov-report=xml:coverage.xml tests/
   ```
2. Use SonarLint in your IDE to catch issues early
3. View SonarCloud analysis in PR comments
4. Run Ruff for code style checking:
   ```bash
   # Install Ruff
   uv pip install ruff

   # Check code style
   ruff check .

   # Format code
   ruff format .
   ```
5. Use pre-commit hooks for automatic checks:
   ```bash
   # Install pre-commit
   uv pip install pre-commit
   pre-commit install
   ```

## Version Updates

MCP Database Utilities is regularly updated with new features, performance improvements, and bug fixes. In most cases, the update process is managed automatically by your MCP client, requiring no manual intervention.

### Getting the Latest Version

- **Using MCP Clients**: Most MCP clients (like Claude Desktop, Cursor, etc.) will automatically update to the latest version

- **Manually Checking for Updates**:
  - Visit the [GitHub repository](https://github.com/donghao1393/mcp-dbutils) to see the latest version
  - Read the [release notes](https://github.com/donghao1393/mcp-dbutils/releases) to learn about new features and changes

- **Issue Reporting**:
  - If you encounter issues after updating, please [submit an issue](https://github.com/donghao1393/mcp-dbutils/issues)