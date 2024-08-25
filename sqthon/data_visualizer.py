import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from typing import Literal, Tuple, Any, Optional
from textwrap import wrap

# TODO: Exception Handling.
# TODO: add multicolored-line from matplotlib.
class DataVisualizer:
    @staticmethod
    def plot(
        data: pd.DataFrame,
        plot_type: Literal["scatter", "line", "bar", "hist_plot", "catplot", "heatmap", "pairplot"],
        x: str,
        y: str,
        title: str,
        figsize: Tuple[float, float] = (6, 6),
        theme: Optional[str] = None,
        **kwargs: Any) -> None:
        """Visualization for the dataframe."""
        if theme:
            sns.set_theme(theme)

        fig, ax = plt.subplots(figsize=figsize)

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

        
        # plt.title(title)
        
        # # Wrap x-axis labels
        # labels = ['\n'.join(wrap(label.get_text(), 15)) for label in ax.get_xticklabels()]
        # ax.set_xticklabels(labels)
        
        # plt.xticks(rotation=0, ha='center')
        # plt.xlabel(x)
        # plt.ylabel(y)
        
        # plt.tight_layout()
        # plt.subplots_adjust(bottom=0.2)  # Adjust bottom margin to accommodate wrapped labels
        # plt.show()

        
        plt.title(title)
        plt.xticks(rotation=45, ha='right', va='top', rotation_mode='anchor')
        plt.xlabel(x)
        plt.ylabel(y)
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.2)
        plt.show()