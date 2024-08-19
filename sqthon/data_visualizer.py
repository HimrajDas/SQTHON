import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from typing import Literal, Tuple, Any
class DataVisualizer:
    @staticmethod
    def plot(
        data: pd.DataFrame,
        plot_type: Literal["scatter", "bar", "line"],
        x: str,
        y: str,
        title: str,
        figsize: Tuple[float, float] = (6, 6),
        **kwargs: Any) -> None:
        """Visualization for the dataframe."""
        plt.figure(figsize=figsize)
        if plot_type == "scatter":
            sns.scatterplot(data=data, x=x, y=y, **kwargs)
        elif plot_type == "line":
            sns.lineplot(data=data, x=x, y=y, **kwargs)
        elif plot_type == "bar":
            sns.barplot(data=data, x=x, y=y, **kwargs)

        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.tight_layout()
        plt.show()
