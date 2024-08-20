import unittest
from sqthon import DatabaseConnector

class TestDatabaseConnector(unittest.TestCase):
    def setUp(self):
        """Set up a DatabaseConnector instance before each test."""
        self.connector = DatabaseConnector("mysql", "pymysql", "sqlbook")
    
    def test_engine_creation(self):
        """Test that sqlalchemy engine get created correctly."""
        self.assertIsNotNone(self.connector.engine)


if __name__ == "__main__":
    unittest.main()