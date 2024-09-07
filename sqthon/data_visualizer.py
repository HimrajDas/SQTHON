import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from typing import Literal, Tuple, Any, Optional
from textwrap import wrap

# TODO: Exception Handling.
# TODO: add multicolored-line from matplotlib.

        
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

    
        # plt.title(title)
        # plt.xticks(rotation=45, ha='right', va='top', rotation_mode='anchor')
        # plt.xlabel(x)
        # plt.ylabel(y)
        # plt.tight_layout()
        # plt.subplots_adjust(bottom=0.2)
        # plt.show()


class DataVisualizer:
    @staticmethod
    def plot(
        data: pd.DataFrame,
        plot_type: Literal["scatter", "line", "bar", "hist", "box", "violin", "heatmap", "pairplot", "jointplot", "kde", "swarm", "lmplot"],
        x: Optional[str] = None,
        y: Optional[str] = None,
        title: str = "",
        figsize: Tuple[float, float] = (10, 6),
        theme: Optional[str] = None,
        palette: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """
        Create various types of plots based on the provided data.

        Args:
            data (pd.DataFrame): The dataset to visualize.
            plot_type (str): The type of plot to create.
            x (str, optional): The column name for x-axis.
            y (str, optional): The column name for y-axis.
            title (str): The title of the plot.
            figsize (Tuple[float, float]): The size of the figure in inches.
            theme (str, optional): The seaborn theme to use.
            palette (str, optional): The color palette to use.
            **kwargs: Additional keyword arguments for the specific plot type.

        Returns:
            None
        """
        if theme:
            sns.set_theme(theme)

        if palette:
            sns.set_palette(palette)

        fig, ax = plt.subplots(figsize=figsize)

        if plot_type == "scatter":
            sns.scatterplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "line":
            sns.lineplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "bar":
            sns.barplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "hist":
            sns.histplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "box":
            sns.boxplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "violin":
            sns.violinplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "heatmap":
            sns.heatmap(data=data, ax=ax, annot=kwargs.pop('annot', True), **kwargs)
        elif plot_type == "pairplot":
            sns.pairplot(data=data, **kwargs)
            plt.suptitle(title, y=1.02)
            return
        elif plot_type == "jointplot":
            sns.jointplot(data=data, x=x, y=y, **kwargs)
            plt.suptitle(title, y=1.02)
            return
        elif plot_type == "kde":
            sns.kdeplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "swarm":
            sns.swarmplot(data=data, x=x, y=y, ax=ax, **kwargs)
        elif plot_type == "lmplot":
            sns.lmplot(data=data, x=x, y=y, **kwargs)
            plt.title(title)
            return
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")

        plt.title(title)
        if x:
            plt.xlabel(x)
        if y:
            plt.ylabel(y)

        # Rotate x-axis labels if they're too long
        if x and len(data[x].unique()) > 10:
            plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        plt.show()

    @staticmethod
    def multi_plot(
        data: pd.DataFrame,
        plot_specs: list,
        title: str = "",
        figsize: Tuple[float, float] = (15, 10),
        theme: Optional[str] = None,
        palette: Optional[str] = None
    ) -> None:
        """
        Create multiple plots in a single figure.

        Args:
            data (pd.DataFrame): The dataset to visualize.
            plot_specs (list): A list of dictionaries, each specifying a subplot.
                Each dict should contain 'type', 'x', 'y', and any additional kwargs.
            title (str): The main title of the figure.
            figsize (Tuple[float, float]): The size of the figure in inches.
            theme (str, optional): The seaborn theme to use.
            palette (str, optional): The color palette to use.

        Returns:
            None
        """
        if theme:
            sns.set_theme(theme)

        if palette:
            sns.set_palette(palette)

        n_plots = len(plot_specs)
        rows = (n_plots + 1) // 2  # Calculate number of rows (2 plots per row)
        fig, axes = plt.subplots(rows, 2, figsize=figsize)
        axes = axes.flatten()  # Flatten axes array for easy indexing

        for i, plot_spec in enumerate(plot_specs):
            plot_type = plot_spec.pop('type')
            x = plot_spec.pop('x', None)
            y = plot_spec.pop('y', None)
            
            if plot_type == "scatter":
                sns.scatterplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            elif plot_type == "line":
                sns.lineplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            elif plot_type == "bar":
                sns.barplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            elif plot_type == "hist":
                sns.histplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            elif plot_type == "box":
                sns.boxplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            elif plot_type == "violin":
                sns.violinplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            elif plot_type == "kde":
                sns.kdeplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            elif plot_type == "swarm":
                sns.swarmplot(data=data, x=x, y=y, ax=axes[i], **plot_spec)
            else:
                raise ValueError(f"Unsupported plot type in multi_plot: {plot_type}")

            axes[i].set_title(plot_spec.get('subtitle', ''))
            if x:
                axes[i].set_xlabel(x)
            if y:
                axes[i].set_ylabel(y)

        # Remove any unused subplots
        for i in range(n_plots, len(axes)):
            fig.delaxes(axes[i])

        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        plt.show()