import unittest
import pandas as pd
from sqthon.data_visualizer import DataVisualizer

class TestDataVisualizer(unittest.TestCase):
    def setUp(self):
        """Set up a DataVisualizer instance before each test."""
        self.visualizer = DataVisualizer()

    def test_plot(self):
        """Test that the plot method runs without errors."""
        df = pd.DataFrame({
            "x": [1, 2, 3, 4],
            "y": [2, 4, 6, 8]
        })

        self.visualizer.plot(df, plot_type="scatter", x="x", y="y", title="Test for scatter plot")


if __name__ == "__main__":
    unittest.main()
