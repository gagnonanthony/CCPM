# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.pyplot import get_cmap
from matplotlib.colors import rgb2hex
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
import numpy as np
import pandas as pd
from pandas.plotting import parallel_coordinates
import scipy.cluster.hierarchy as shc
import seaborn as sns
from statannotations.Annotator import Annotator


def plot_clustering_results(lst, title, metric, output, errorbar=None,
                            annotation=None):
    """
    Function to plot goodness of fit indicators resulting from a clustering
    model. Resulting plot will be saved in the output folder specified in
    function's arguments.

    Args:
        lst (List):                 List of values to plot.
        title (str):                Title of the plot.
        metric (str):               Metric name.
        output (str):               Output filename.
        errorbar (List):            List of values to plot as errorbar
                                    (CI, SD, etc.).
        annotation (str, optional): Annotation to add directly on the plot.
                                    Defaults to None.
    """

    # Plotting data.
    fig = plt.figure(figsize=(10, 7))
    axes = fig.add_subplot(111)

    with plt.rc_context(
        {"font.size": 10, "font.weight": "bold", "axes.titleweight": "bold"}
    ):
        axes.plot(range(2, len(lst) + 2), lst)

        # Add error bar if provided.
        if errorbar is not None:
            assert len(errorbar) == len(
                lst
            ), "Values to plot and error bars are not of the same length "
            "[{} and {}]".format(len(lst), len(errorbar))

            axes.errorbar(
                range(2, len(errorbar) + 2),
                lst,
                yerr=errorbar,
                ecolor="black",
                elinewidth=1,
                fmt="o",
                color="black",
                barsabove=True,
            )

        # Set parameters.
        plt.xticks(range(2, len(lst) + 2))
        plt.title(f"{title}")
        plt.xlabel("Number of clusters")
        plt.ylabel(f"{metric}")
        axes.spines[["top", "right"]].set_visible(False)
        axes.spines["bottom"].set(linewidth=1.5)
        axes.spines["left"].set(linewidth=1.5)

        # Annotating
        if annotation is not None:
            if axes.get_ylim()[0] < 0:
                y_pos = axes.get_ylim()[0] * 0.95
            else:
                y_pos = axes.get_ylim()[1] * 0.95

            plt.text(x=axes.get_xlim()[1] * 0.5, y=y_pos, s=f"{annotation}")

        plt.savefig(f"{output}")
        plt.close()


def plot_dendrogram(X, output, title="Dendrograms", annotation=None):
    """
    Function to plot a dendrogram plot showing hierarchical clustering. Useful
    to visually determine the appropriate number of clusters.
    Adapted from:
    https://towardsdatascience.com/cheat-sheet-to-implementing-7-methods-for-selecting-optimal-number-of-clusters-in-python-898241e1d6ad

    Args:
        X (DataFrame):                  Data on which clustering will be
                                        performed.
        output (str):                   Output filename and path.
        title (str, optional):          Title for the plot. Defaults to
                                        'Dendrograms'.
        annotation (str, optional):     Annotation to add directly on the plot.
                                        Defaults to None.
    """

    fig = plt.figure(figsize=(10, 7))
    axes = fig.add_subplot(111)

    with plt.rc_context(
        {"font.size": 10, "font.weight": "bold", "axes.titleweight": "bold"}
    ):
        axes.set_title(f"{title}")

        shc.dendrogram(shc.linkage(X, method="ward"))

        if annotation is not None:
            plt.text(
                x=fig.axes[0].get_xlim()[1] * 0.10,
                y=fig.axes[0].get_ylim()[1] * 0.85,
                s=f"{annotation}",
            )

        axes.set_xticks([])
        axes.set_yticks([])
        axes.spines[["top", "right", "left"]].set_visible(False)
        axes.spines["bottom"].set(linewidth=1.5)

        plt.savefig(f"{output}")
        plt.close()


def sort_int_labels_legend(ax, title=None):
    """
    Function automatically reorder numerically labels with matching handles in
    matplotlib legend.

    Args:
        ax:                     Matplotlib Axes.
        title (str, optional):  Title of the legend.

    Returns:
        ax.legend:              Axes legend object.
    """

    # Fetching handles and tags from matplotlib axes.
    handles, tags = ax.get_legend_handles_labels()

    # Converting tags to int if they are not already.
    if type(tags[0]) is str:
        tags = [int(float(x)) for x in tags]

    # Sorting tags and make handles follow the same ordering.
    tag, handle = zip(*sorted(zip(tags, handles)))

    if title is not None:
        return ax.legend(handle, tag, title=title)

    else:
        return ax.legend(handle, tag)


def plot_parallel_plot(
    X, labels, output, mean_values=False, cmap='magma',
    title="Parallel Coordinates plot."
):
    """
    Function to plot a parallel coordinates plot to visualize differences
    between clusters. Useful to highlight significant changes between clusters
    and interpret them.
    Adapted from:
    https://towardsdatascience.com/the-art-of-effective-visualization-of-multi-dimensional-data-6c7202990c57

    Args:
        X (pd.DataFrame):                   Input dataset of shape (S, F).
        labels (Array):                     Array of hard membership value.
                                            (S, ).
        output (str):                       Filename of the png file.
        cmap (str, optional):               Colormap to use for the plot.
                                            Defaults to 'magma'. See
                                            https://matplotlib.org/stable/tutorials/colors/colormaps.html
        title (str, optional):              Title of the plot.
                                            Defaults to 'Parallel Coordinates
                                            plot.'.
    """

    labels = labels + 1

    columns = list(X.columns)
    columns.append("Clusters")

    df = pd.concat([X, pd.DataFrame(labels, columns=["Clusters"])], axis=1)

    if mean_values:
        # Calculating mean values for each features for each clusters.
        final_df = pd.DataFrame()
        i = 0
        for col in X.columns:
            mean = list()
            for k in np.unique(labels):
                mean.append(df.loc[df["Clusters"] == k, col].mean())
            final_df.insert(i, col, mean)
            i += 1
        final_df.insert(i, "Clusters", np.unique(labels))
    else:
        indexes = np.random.choice(df.shape[0], size=500, replace=False)
        final_df = df.iloc[indexes]

    # Setting color palette.
    cmap = get_cmap(cmap, len(np.unique(labels)))
    colors = [rgb2hex(cmap(i)) for i in range(cmap.N)]

    fig = plt.figure(figsize=(15, 7))
    ax = fig.add_subplot(111)

    with plt.rc_context(
        {"font.size": 10, "font.weight": "bold", "axes.titleweight": "bold"}
    ):
        parallel_coordinates(final_df, "Clusters", ax=ax, color=colors)
        sort_int_labels_legend(ax, title="Cluster #")
        ax.set_title(f"{title}")
        ax.grid(False)
        ax.spines[["left", "right", "top", "bottom"]].set(linewidth=1.5)

        ax.figure.autofmt_xdate()

        plt.savefig(f"{output}")
        plt.close()


def plot_grouped_barplot(X, labels, output, cmap='magma',
                         title="Barplot"):
    """
    Function to plot a barplot for all features in the original dataset
    stratified by clusters. T-test between clusters' mean within a feature is
    also computed and annotated directly on the plot. When plotting a high
    number of clusters, plotting of significant annotation is polluting the
    plot, will be fixed in the future.

    Args:
        X (DataFrame):                      Input dataset of shape (S, F).
        labels (Array):                     Array of hard membership value
                                            (S, ).
        output (str):                       Filename of the png file.
        cmap (str, optional):               Colormap to use for the plot.
                                            Defaults to 'magma'. See
                                            https://matplotlib.org/stable/tutorials/colors/colormaps.html
        title (str, optional):              Title of the plot.
                                            Defaults to 'Barplot'.
    """
    # Make labels start at 1 rather than 0, better for viz.
    labels = labels + 1

    features = list(X.columns)
    features.append("Clusters")

    # Merging the labels with the original dataset.
    df = pd.concat([X, pd.DataFrame(labels, columns=["Clusters"])], axis=1)

    # Melting the dataframe for plotting.
    viz_df = df.melt(id_vars="Clusters")

    # Setting up matplotlib figure.
    fig = plt.figure(figsize=(15, 8))
    axes = fig.add_subplot()

    # Setting parameters for the barplot.
    plotting_parameters = {
        "data": viz_df,
        "x": "variable",
        "y": "value",
        "hue": "Clusters",
        "palette": cmap,
        "saturation": 0.5,
    }

    with plt.rc_context(
        {"font.size": 10, "font.weight": "bold", "axes.titleweight": "bold"}
    ):
        # Plotting barplot using Seaborn.
        sns.barplot(ax=axes, **plotting_parameters)

        # Setting pairs for statistical testing between clusters for each
        # feature.
        clusters = np.unique(labels)
        features = list(X.columns)

        pairs = [
            [(var, cluster1), (var, cluster2)]
            for var in features
            for i, cluster1 in enumerate(clusters)
            for cluster2 in clusters
            if (cluster1 != cluster2) and not (cluster1 > cluster2)
        ]

        # Plotting statistical difference.
        annotator = Annotator(
            axes, pairs, verbose=False, **plotting_parameters
        )
        annotator.configure(
            test="Mann-Whitney", text_format="star", show_test_name=False,
            verbose=0, hide_non_significant=True, comparisons_correction='BH',
            correction_format='replace', line_height=0.005
        )
        annotator.apply_test()
        _, results = annotator.annotate()

        # Customization options.
        axes.spines[["left", "bottom", "top", "right"]].set(linewidth=2)
        axes.legend(title="Cluster #", loc="best", title_fontsize="medium")
        axes.set_title(f"{title}")
        axes.set_ylabel("Scores", fontdict={"fontweight": "bold"})
        axes.set_xlabel("")
        axes.grid(False)

        axes.figure.autofmt_xdate()

        plt.savefig(f"{output}")
        plt.close()


def radar_plot(X, labels, output, frame='circle', title="Radar plot",
               cmap='magma'):
    """
    Function to plot a radar plot for all features in the original dataset
    stratified by clusters. T-test between clusters' mean within a feature is
    also computed and annotated directly on the plot. When plotting a high
    number of clusters, plotting of significant annotation is polluting the
    plot, will be fixed in the future.

    Args:
        X (DataFrame):                      Input dataset of shape (S, F).
        labels (Array):                     Array of hard membership value
                                            (S, ).
        output (str):                       Filename of the png file.
        frame (str, optional):              Shape of the radar plot. Defaults
                                            to 'circle'. Choices are 'circle'
                                            or 'polygon'.
        title (str, optional):              Title of the plot.
                                            Defaults to 'Radar plot'.
        cmap (str, optional):               Colormap to use for the plot.
                                            Defaults to 'magma'. See
                                            https://matplotlib.org/stable/tutorials/colors/colormaps.html
    """
    # Setting color palette.
    cmap = get_cmap(cmap, len(np.unique(labels)))
    colors = [rgb2hex(cmap(i)) for i in range(cmap.N)]

    # Make labels start at 1 rather than 0, better for viz.
    labels = labels + 1

    # Computing mean values for each features for each clusters.
    mean_df = pd.DataFrame()
    i = 0
    for col in X.columns:
        mean = list()
        for k in np.unique(labels):
            mean.append(X.loc[labels == k, col].mean())
        mean_df.insert(i, col, mean)
        i += 1
    mean_df.insert(i, "Clusters", np.unique(labels))

    # Set radar plot parameters.
    theta = create_radar_plot(len(X.columns), frame=frame)

    with plt.rc_context(
        {"font.size": 12, "font.weight": "bold", "axes.titleweight": "bold",
         "font.family": "Sans Serif"}
    ):
        fig, ax = plt.subplots(1, 1, figsize=(12, 12),
                               subplot_kw=dict(projection='radar'))
        fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.5)

        ax.grid(which='major', axis='x')

        for idx, cluster in enumerate(np.unique(labels)):
            values = mean_df.iloc[idx].drop('Clusters').values.tolist()
            ax.plot(theta, values, c=colors[idx], linewidth=1.5,
                    label=f'Cluster {cluster}')
            ax.fill(theta, values, facecolor=colors[idx], alpha=0.20,
                    label='_nolegend_')

    # Set legend and variables parameters.
    legend = ax.legend(np.unique(labels), loc=(0.95, 0.9), title='Cluster #',
                       fontsize=12)
    frame = legend.get_frame()
    frame.set_facecolor('lightgray')
    frame.set_edgecolor('gray')
    ax.set_varlabels(X.columns)
    ax.set_rlabel_position(180)

    # Setting title.
    ax.set_title(f"{title}", weight='bold', size=16,
                 horizontalalignment='center')

    # Set the position for the labels.
    for label, angle in zip(ax.get_xticklabels(), theta):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('right')
        else:
            label.set_horizontalalignment('left')

    plt.tight_layout()
    plt.savefig(f"{output}")
    plt.close()


def create_radar_plot(nb_vars, frame='circle'):
    """
    Create a radar chart with `nb_vars` axes.

    Args:
        nb_vars (int):          Number of variables to plot.
        frame (str, optional):  Shape of the radar plot. Defaults to 'circle'.
                                Choices are 'circle' or 'polygon'.

    Returns:
        np.array:               Array of evenly spaced axis angles.
    """

    # Compute evenly spaced axis angles.
    theta = np.linspace(0, 2 * np.pi, nb_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):

        def transform_path_non_affine(self, path):
            if path._interpolation_steps > 1:
                path = path.interpolated(nb_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):

        name = 'radar'
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Rotate plot to place the first axis at the top.
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default.

            Args:
                closed (bool, optional): _description_. Defaults to True.
            """
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """
            Override plot so that line is closed by default.
            """
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), nb_vars,
                                      radius=0.5, edgecolor='k')
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':

                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(nb_vars))
                spine.set_transform(
                    Affine2D().scale(0.5).translate(0.5, 0.5) + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)

    return theta
