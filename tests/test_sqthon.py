import unittest
from sqthon import Sqthon

class TestSqthon(unittest.TestCase):
    def setUp(self):
        """Set up a sqthon instance before each test."""
        self.sqthon = Sqthon("postgresql", "psycopg2", "sqlbook")


    def test_run_query_without_visualization(self):
        """Test that the run query method works without visualization"""
        query = """SELECT 1 as test_column"""
        result = self.sqthon.run_query(query=query)
        self.assertEqual(result.iloc[0]['test_column'], 1)

    def test_run_query_with_visualization(self):
        """Test that the run query method works with visualization."""
        query = """SELECT 1 as test_column"""
        result = self.sqthon.run_query(query=query, visualize=True, plot_type="scatter", x="test_column", y="test_column", title="test_plot")
        self.assertEqual(result.iloc[0]['test_column'], 1)



if __name__ == "__main__":
    unittest.main()



