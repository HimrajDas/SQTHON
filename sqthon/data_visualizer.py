import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from typing import Literal, Tuple, Any

# TODO: Exception Handling.
class DataVisualizer:
    @staticmethod
    def plot(
        data: pd.DataFrame,
        plot_type: Literal["scatter", "line", "bar", "hist_plot", "catplot", "heatmap", "pairplot"],
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
        elif plot_type == "hist_plot":
            sns.histplot(data=data, x=x, y=y, **kwargs)
        elif plot_type == "catplot":
            sns.catplot(data=data, x=x, y=y, **kwargs)
        elif plot_type == "heatmap":
            sns.heatmap(data=data, annot=True, **kwargs)
        elif plot_type == "pairplot":
            sns.pairplot(data=data, **kwargs)
        elif plot_type == "joinplot":
            sns.jointplot(data=data, x=x, y=y, kind="scatter", **kwargs)

        
        plt.title(title)
        plt.xticks(rotation=45)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.tight_layout()
        plt.show()