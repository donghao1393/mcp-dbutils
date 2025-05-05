"""Test SQL parsing functions in base.py"""
import pytest

from mcp_dbutils.base import ConfigurationError, ConnectionServer


class TestSQLParsing:
    """Test SQL parsing functions"""

    def test_get_sql_type(self):
        """Test _get_sql_type method"""
        server = ConnectionServer("config.yaml")

        # Test SELECT statement
        assert server._get_sql_type("SELECT * FROM users") == "SELECT"
        assert server._get_sql_type("  SELECT  * FROM users") == "SELECT"
        assert server._get_sql_type("select * from users") == "SELECT"

        # Test INSERT statement
        assert server._get_sql_type("INSERT INTO users VALUES (1, 'test')") == "INSERT"
        assert server._get_sql_type("insert into users values (1, 'test')") == "INSERT"

        # Test UPDATE statement
        assert server._get_sql_type("UPDATE users SET name = 'test' WHERE id = 1") == "UPDATE"
        assert server._get_sql_type("update users set name = 'test' where id = 1") == "UPDATE"

        # Test DELETE statement
        assert server._get_sql_type("DELETE FROM users WHERE id = 1") == "DELETE"
        assert server._get_sql_type("delete from users where id = 1") == "DELETE"

        # Test CREATE statement
        assert server._get_sql_type("CREATE TABLE users (id INT, name TEXT)") == "CREATE"
        assert server._get_sql_type("create table users (id int, name text)") == "CREATE"

        # Test ALTER statement
        assert server._get_sql_type("ALTER TABLE users ADD COLUMN email TEXT") == "ALTER"
        assert server._get_sql_type("alter table users add column email text") == "ALTER"

        # Test DROP statement
        assert server._get_sql_type("DROP TABLE users") == "DROP"
        assert server._get_sql_type("drop table users") == "DROP"

        # Test TRUNCATE statement
        assert server._get_sql_type("TRUNCATE TABLE users") == "TRUNCATE"
        assert server._get_sql_type("truncate table users") == "TRUNCATE"

        # Test transaction statements
        assert server._get_sql_type("BEGIN TRANSACTION") == "TRANSACTION_START"
        assert server._get_sql_type("START TRANSACTION") == "TRANSACTION_START"
        assert server._get_sql_type("COMMIT") == "TRANSACTION_COMMIT"
        assert server._get_sql_type("ROLLBACK") == "TRANSACTION_ROLLBACK"

        # Test unknown statement
        assert server._get_sql_type("UNKNOWN STATEMENT") == "UNKNOWN"
        assert server._get_sql_type("") == "UNKNOWN"

    def test_extract_table_name(self):
        """Test _extract_table_name method"""
        server = ConnectionServer("config.yaml")

        # Test INSERT statement
        assert server._extract_table_name("INSERT INTO users VALUES (1, 'test')").lower() == "users"
        assert server._extract_table_name("INSERT INTO public.users VALUES (1, 'test')").lower() == "public.users"

        # Test UPDATE statement
        assert server._extract_table_name("UPDATE users SET name = 'test' WHERE id = 1").lower() == "users"
        assert server._extract_table_name("UPDATE public.users SET name = 'test' WHERE id = 1").lower() == "public.users"

        # Test DELETE statement
        assert server._extract_table_name("DELETE FROM users WHERE id = 1").lower() == "users"
        assert server._extract_table_name("DELETE FROM public.users WHERE id = 1").lower() == "public.users"

        # Test with quoted table name
        assert server._extract_table_name('INSERT INTO "users" VALUES (1, \'test\')').lower() == "users"
        assert server._extract_table_name("INSERT INTO `users` VALUES (1, 'test')").lower() == "users"
        assert server._extract_table_name("INSERT INTO [users] VALUES (1, 'test')").lower() == "users"

        # Test unknown statement
        assert server._extract_table_name("UNKNOWN STATEMENT") == "unknown_table"

    def test_extract_table_name_complex(self):
        """Test _extract_table_name method with complex SQL statements"""
        server = ConnectionServer("config.yaml")

        # Test INSERT with column names
        assert server._extract_table_name("INSERT INTO users (id, name) VALUES (1, 'test')").lower() == "users"

        # Test INSERT with multiple rows
        assert server._extract_table_name("""
        INSERT INTO users (id, name) VALUES
        (1, 'test1'),
        (2, 'test2'),
        (3, 'test3')
        """).lower() == "users"

        # Test INSERT ... SELECT
        assert server._extract_table_name("""
        INSERT INTO users (id, name, email)
        SELECT id, name, email
        FROM temp_users
        WHERE active = 1
        """).lower() == "users"

        # Test UPDATE with multiple columns
        assert server._extract_table_name("""
        UPDATE users
        SET name = 'test',
            email = 'test@example.com',
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN (1, 2, 3)
        """).lower() == "users"

        # Test DELETE with subquery
        assert server._extract_table_name("""
        DELETE FROM users
        WHERE id IN (
            SELECT user_id
            FROM inactive_users
            WHERE last_login < '2020-01-01'
        )
        """).lower() == "users"

        # Test with comments and whitespace
        assert server._extract_table_name("INSERT INTO users -- comment\nVALUES (1, 'test')").lower() == "users"
        assert server._extract_table_name("INSERT INTO\nusers\nVALUES (1, 'test')").lower() == "users"
        assert server._extract_table_name("UPDATE users -- comment\nSET name = 'test'").lower() == "users"
        assert server._extract_table_name("DELETE FROM users -- comment\nWHERE id = 1").lower() == "users"

    def test_extract_table_name_edge_cases(self):
        """Test _extract_table_name method with edge cases"""
        server = ConnectionServer("config.yaml")

        # Test table names with special characters
        assert server._extract_table_name("INSERT INTO table$123 VALUES (1)").lower() == "table$123"
        assert server._extract_table_name("INSERT INTO table_name VALUES (1)").lower() == "table_name"
        assert server._extract_table_name("INSERT INTO table-name VALUES (1)").lower() == "table-name"

        # Test table names with numbers
        assert server._extract_table_name("INSERT INTO table123 VALUES (1)").lower() == "table123"
        assert server._extract_table_name("INSERT INTO 123table VALUES (1)").lower() == "123table"

        # Test table names that are SQL keywords
        assert server._extract_table_name("INSERT INTO table VALUES (1)").lower() == "table"
        assert server._extract_table_name("INSERT INTO select VALUES (1)").lower() == "select"
        assert server._extract_table_name("INSERT INTO from VALUES (1)").lower() == "from"

        # Test long table names
        long_table_name = "very_long_table_name_with_more_than_thirty_characters"
        assert server._extract_table_name(f"INSERT INTO {long_table_name} VALUES (1)").lower() == long_table_name.lower()

        # Test with table aliases
        assert server._extract_table_name("UPDATE users u SET u.name = 'test'").lower() == "users"
        assert server._extract_table_name("DELETE FROM users AS u WHERE u.id = 1").lower() == "users"
