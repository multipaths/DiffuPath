# -*- coding: utf-8 -*-

"""Visualization methods."""
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .statistic_tests import get_normalized_p_values

from matplotlib_venn import venn3

from typing import List, Dict, Union, Optional, Tuple, Set, Callable

"""Process/mapping input data plots"""


def show_heatmap(
        entity_number: np.ndarray,
        entity_count: List[List[int]],
        row_labels: List[int],
        col_labels: List[int],
        title: str = "DiffuPath Mapping") -> None:
    """Render a heatmap from a numpy array and two lists of labels.

    :param entity_number: A 2D numpy array of shape (N,M).
    :param entity_count: Value in data units according to which the colors from textcolors are applied.
    :param row_labels: A list or array of length N with the labels for the rows.
    :param col_labels: A list or array of length N with the labels for the columns.
    :param title: Main title for the heatmap.
    """
    fig, ax = plt.subplots(figsize=(15, 7))

    im, cbar = _generate_heatmap(entity_number, row_labels, col_labels, ax=ax,
                                 cmap="YlGn", cbarlabel="percentage [0-1]")
    _ = _annotate_heatmap(im, entity_count=entity_count, valfmt="{x:1} ")

    fig.tight_layout()
    ax.set_title(title)

    plt.show()


def _generate_heatmap(
        data: np.ndarray,
        row_labels: List[int],
        col_labels: List[int],
        ax=None,
        cbar_kw: Optional[dict] = {},
        cbarlabel: Optional[str] = "",
        title: str = "",
        **kwargs):
    """Create a heatmap from a numpy array and two lists of labels.

    Optional parameters: ax: A matplotlib.axes.Axes instance to which the heatmap is plotted. If not provided, use
    current axes or create a new one. cbar_kw: A dictionary with arguments to :meth:`matplotlib.Figure.colorbar`.
    cbarlabel: The label for the colorbar.

    :param data: A 2D numpy array of shape (N,M)
    :param row_labels: A list or array of length N with the labels for the rows
    :param col_labels: A list or array of length N with the labels for the columns
    :param ax: axis
    :param cbar_kw: kwars for cbar
    :param cbarlabel: label
    :param title: title
    """
    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1] + 1) - .5, minor=True)
    ax.set_yticks(np.arange(data.shape[0] + 1) - .5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    ax.set_title(title)

    return im, cbar


def _annotate_heatmap(
        im,
        data=None,
        valfmt="{x:.2f}",
        textcolors=["black", "white"],
        entity_count=None,
        threshold=None,
        **textkw):
    """Annotate a heatmap. Further parameters can be passed as textkw.

    :param im: The AxesImage to be labeled.
    :param data: Data used to annotate. If None, the image's data is used.
    :param valfmt: The sep of the annotations inside the heatmap. This should either use the string sep method.
    :param textcolors: A list or array of two color specifications.
    :param entity_count: Value in data units according to which the colors from textcolors are applied.
    :param threshold: Value in data units according to which the colors from textcolors are applied.
    """
    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max()) / 2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[im.norm(data[i, j]) > threshold])
            text = im.axes.text(j, i, valfmt(entity_count[i, j], None), **kw)
            texts.append(text)

    return texts


def show_venn_diagram(
        intersections: Dict[str, Union[List, set]],
        set_labels=None):
    """Render Venn Diagram to explore the intersection between different sets of labels.

    :param intersections: A dictionary, with set-title as keys and set-labels list as values.
    :param set_labels: A list or array of length N with the labels for the rows
    """
    if set_labels is None:
        set_labels = list(intersections.keys())

    intersections_len = [len(intersection) for name, intersection in intersections.items()]

    plt.figure(figsize=(17, 8))
    _ = venn3(subsets=intersections_len, set_labels=set_labels)

    plt.show()


def show_distribution(
        values_type_dict: Dict[str, Dict[str, int]],
        title="Input measures distribution",
        subtitle="distribution"):
    """Render a Heatmap from a numpy array and two lists of labels.

    :param values_type_dict: A 2D numpy array of shape (N,M)
    :param title: A list or array of length N with the labels for the rows
    :param subtitle: A list or array of length N with the labels for the columns
    """
    plt.rcParams.update({'font.size': 13, 'font.weight': 'normal', 'ytick.labelsize': 'x-small'})

    fig, (axs) = plt.subplots(1, len(values_type_dict), figsize=(17, 6))
    fig.suptitle(title)

    for i, (dataset_label, dataset) in enumerate(values_type_dict.items()):
        # rectangular box plot
        _ = sns.distplot(a=np.asarray(list(dataset.values())), ax=axs[i]).set_title(f'{subtitle} {dataset_label}')


"""Validation metrics plots."""


def show_box_plot(
        data_dict: Dict[str, Dict[str, List]],
        x_label: str = '',
        y_label: str = '',
        y_lim: int = None,
        color_palette: List = None):
    """Render a bloxpot, showing the fractioned distribution for a ONE-dimensional stratified data set of frequencies.

    :param data_dict: Stratified dataset of frequencies to be plotted.
    :param x_label: Abscissa axis title.
    :param y_label: Ordinates axis title.
    :param y_lim: Range of the ordinates axis to be shwon.
    :param color_palette: List of alternative palette colors.
    """
    if y_lim is None:
        y_lim = [0, 1]
    if color_palette is None:
        color_palette = ['royalblue', 'forestgreen', 'khaki', 'lightcoral', 'yellow', 'green']

    bplots = []

    plt.rcParams.update({'font.size': 15, 'font.weight': 'normal', 'ytick.labelsize': 'x-small'})

    fig, axs = plt.subplots(nrows=1,
                            ncols=len(data_dict),
                            figsize=(18, 6)
                            )
    if not isinstance(axs, np.ndarray):
        axs = [axs]

    for i, (dataset_label, dataset) in enumerate(data_dict.items()):
        # rectangular box plot
        bplot = axs[i].boxplot(list(dataset.values()),
                               vert=True,  # vertical box alignment
                               patch_artist=True,  # fill with color
                               labels=list(dataset.keys())
                               )  # will be used to label x-ticks
        axs[i].set_title(dataset_label, fontweight="bold")

        bplots.append(bplot)

    # fill with colors
    for bplot in bplots:
        for i, (patch, color) in enumerate(zip(bplot['boxes'], color_palette)):
            patch.set_facecolor(color_palette[i])

    # adding horizontal grid lines
    for i, ax in enumerate(axs):
        ax.yaxis.grid(True)
        ax.set_ylim(y_lim)

        ax.yaxis.grid(True)

        ax.set_xlabel(x_label, fontweight="bold")
        ax.set_ylabel(y_label, fontweight="bold")

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), rotation=-25, ha="left",
                 rotation_mode="anchor")

    plt.show()


def show_sb_box_plot(
        data_dict: Dict[str, Dict[str, Union[List, set]]],
        x_label: Optional[str] = '',
        y_label: Optional[str] = '',
        y_lim: Optional[Union[int, Tuple]] = None,
        color_palette: Optional[List] = None):
    """Render a (seaborn) bloxpot, showing the distribution for a TWO-dimensional stratified data set of frequencies.

    :param data_dict: Stratified dataset of frequencies to be plotted.
    :param x_label: Abscissa axis title.
    :param y_label: Ordinates axis title.
    :param y_lim: Range of the ordinates axis to be shown.
    :param color_palette: List of palette colors. By default ['royalblue', 'forestgreen', 'khaki', 'lightcoral', 'yellow', 'green'].
    """
    if y_lim is None:
        y_lim = [0, 1]
    if color_palette is None:
        color_palette = ['royalblue', 'forestgreen', 'khaki', 'lightcoral', 'yellow', 'green']

    plt.rcParams.update({'font.size': 15, 'font.weight': 'normal', 'ytick.labelsize': 'x-small'})

    fig, (axs) = plt.subplots(1, len(data_dict), figsize=(17, 6))

    if not isinstance(axs, np.ndarray):
        axs = [axs]

    for i, (dataset_label, dataset) in enumerate(data_dict.items()):
        # rectangular box plot

        _ = sns.boxplot(x="k3",
                        y="score",
                        ax=axs[i],
                        hue="k2",
                        data=dataset,
                        palette=color_palette
                        )

        if i == 2:
            axs[i].legend(prop={'size': 16, 'weight': 'bold'})
        else:
            axs[i].get_legend().remove()

        if i != 0:
            axs[i].set_ylabel('')

        fig.subplots_adjust(top=0.93)

        axs[i].set_title(dataset_label, fontsize=17, fontweight="bold")

    # adding horizontal grid lines
    for i, ax in enumerate(axs):
        ax.yaxis.grid(True)
        ax.set_ylim(y_lim)

        ax.yaxis.grid(True)

        if i == 0:
            ax.set_ylabel(y_label, fontweight="bold")
        ax.set_xlabel(x_label, fontweight="bold")

        # Rotate the tick labels and set their alignment.
        plt.setp(ax.get_xticklabels(), size=12, rotation=-25, ha="left",
                 rotation_mode="anchor")

    plt.show()


def preprocess_for_sb_ttest(data: Dict[str:Dict[str:Dict[str:List[int]]]]):
    """Preprocess TWO-dimensional stratified datainput for t-test data view, reducing one dimentionality.

    :param data: Stratified dataset of frequencies to be plotted.
    """
    metrics_by_method_df = defaultdict(lambda: defaultdict(lambda: list()))

    for dataset, v1 in data.items():
        for background, v2 in v1.items():
            for database, scores in v2.items():
                metrics_by_method_df[dataset][database + '_on_' + background] = scores

    return metrics_by_method_df


def preprocess_for_sb_boxplot(data: Dict[str:Dict[str:Dict[str:List[int]]]]):
    """Preprocess TWO-dimensional stratified datainput for Seaborn boxplot, converting a multiple-dimensional dictionary to a dataframe.

    :param data: Stratified dataset dictionary of frequencies to be plotted.
    """
    metrics_by_method_df = {}

    for k1, v1 in data.items():
        metrics_by_method_to_df = defaultdict(lambda: list())
        for k2, v2 in v1.items():
            for k3, scores in v2.items():
                for score in scores:
                    metrics_by_method_to_df['k2'].append(k2)
                    metrics_by_method_to_df['k3'].append(k3)

                    metrics_by_method_to_df['score'].append(score)

        metrics_by_method_df[k1] = pd.DataFrame(metrics_by_method_to_df)

    return metrics_by_method_df


def fdr_barchart_three_plot(
        data: Union[Dict[str, Union[str, Union[List[int]]]], List[Union[List[int], Set[int]]]],
        p_values_func: Callable,
        title: Optional[str] = 'Statistic Test',
        x_label: Optional[str] = '',
        y_label: Optional[str] = 'normalized FDR -log10(p-value)',
        k_limit: Optional[int] = 14,
        legend: Optional[List[str]] = None):
    """Render FDR (Fasle Discovery Rate) barchart.

    :param data: Stratified dataset of frequencies to be plotted.
    :param p_values_func: function/method to be applied.
    :param title: Plot title.
    :param x_label: Abscissa axis title.
    :param y_label: Ordinates axis title.
    :param k_limit: Range of the ordinates axis to be shown.
    :param legend: List of labels as 3th-dimension legend. By default ('Dataset 1', 'Dataset 2', 'Dataset 3').
    """
    if legend is None:
        if isinstance(data, dict):
            legend = list(data.keys())
        else:
            legend = ('Dataset 1', 'Dataset 2', 'Dataset 3')

    if isinstance(data, dict):
        data = list(data.values())

    plt.rcParams.update({'font.size': 17})

    normalized_p_values = []

    for metric in data:
        p_values = p_values_func(metric)
        normalized_p_values.append(list(get_normalized_p_values(p_values).values()))
        x = list(p_values.keys())

    ind = np.arange(len(x))  # the x locations for the groups
    width = 0.27  # the width of the bars

    fig = plt.figure()
    ax = fig.add_subplot(111)

    fig.set_size_inches(14.5, 7.5)

    ax.set_title(title, fontweight="bold")

    rects1 = ax.bar(ind, normalized_p_values[0], width, color='forestgreen')
    rects2 = ax.bar(ind + width, normalized_p_values[1], width, color='tomato')
    rects3 = ax.bar(ind + width * 2, normalized_p_values[2], width, color='steelblue')

    ax.set_ylabel(y_label)
    plt.xlabel(x_label)

    ax.set_xticks(ind + width)
    ax.set_xticklabels(x, ha='left', rotation=-45)
    ax.legend((rects1[0], rects2[0], rects3[0]), legend)

    ax.plot([-0.2, k_limit], [-np.math.log10(0.05), -np.math.log10(0.05)], "k--")

    plt.show()
