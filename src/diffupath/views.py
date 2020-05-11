# -*- coding: utf-8 -*-

"""Visualization methods."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from diffupath.cross_validation import get_normalized_p_values

from matplotlib_venn import venn3


def show_box_plot(
        data_dict,
        x_label='',
        y_label='',
        color_palette=None
):
    """Plot boxplot."""
    if color_palette is None:
        color_palette = ['royalblue', 'forestgreen', 'khaki', 'lightcoral', 'yellow', 'green']

    bplots = []

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
        axs[i].set_title(dataset_label)

        bplots.append(bplot)

    # fill with colors
    for bplot in bplots:
        for i, (patch, color) in enumerate(zip(bplot['boxes'], color_palette)):
            patch.set_facecolor(color_palette[i])

    # adding horizontal grid lines
    for i, ax in enumerate(axs):
        ax.yaxis.grid(True)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    plt.show()


def fdr_barchart_three_plot(
        metrics,
        p_values_func,
        title='Statistic Test',
        legend=None
):
    if legend is None:
        if isinstance(metrics, dict):
            legend = list(metrics.keys())
        else:
            legend = ('Dataset 1', 'Dataset 2', 'Dataset 3')

    if isinstance(metrics, dict):
        metrics = list(metrics.values())

    plt.rcParams.update({'font.size': 17})

    normalized_p_values = []

    for metric in metrics:
        p_values = p_values_func(metric)
        normalized_p_values.append(list(get_normalized_p_values(p_values).values()))
        x = list(p_values.keys())

    ind = np.arange(len(x))  # the x locations for the groups
    width = 0.27  # the width of the bars

    fig = plt.figure()
    ax = fig.add_subplot(111)

    fig.set_size_inches(14.5, 7.5)

    rects1 = ax.bar(ind, normalized_p_values[0], width, color='forestgreen')
    rects2 = ax.bar(ind + width, normalized_p_values[1], width, color='tomato')
    rects3 = ax.bar(ind + width * 2, normalized_p_values[2], width, color='steelblue')

    ax.set_ylabel("normalized FDR -log10(p-value)")
    plt.xlabel(title)

    ax.set_xticks(ind + width)
    ax.set_xticklabels(x, ha='left', rotation=-45)
    ax.legend((rects1[0], rects2[0], rects3[0]), legend)

    ax.plot([-0.2, 6], [-np.math.log10(0.05), -np.math.log10(0.05)], "k--")

    plt.show()


def show_venn_diagram(
        intersections,
        set_labels=('KEGG', 'Reactome', 'WikiPathways')
):
    """Show venn diagram."""
    intersections_len = [len(intersection) for name, intersection in intersections.items()]

    plt.figure(figsize=(17, 8))
    _ = venn3(subsets=intersections_len, set_labels=set_labels)

    plt.show()


def show_heatmap(
        entity_number,
        entity_count,
        databases,
        entity_types,
        title="DiffuPath Mapping"
):
    fig, ax = plt.subplots(figsize=(15, 7))

    im, cbar = _generate_heatmap(entity_number, databases, entity_types, ax=ax,
                                 cmap="YlGn", cbarlabel="percentage [0-1]")
    _ = _annotate_heatmap(im, entity_count=entity_count, valfmt="{x:1} ")

    fig.tight_layout()
    ax.set_title(title)

    plt.show()


def _generate_heatmap(
        data,
        row_labels,
        col_labels,
        ax=None,
        cbar_kw={},
        cbarlabel="",
        title="",
        **kwargs
):
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
        **textkw
):
    """Annotate a heatmap. Further parameters can be passed as textkw.

    :param im: The AxesImage to be labeled.
    :param data: Data used to annotate. If None, the image's data is used.
    :param valfmt: The sep of the annotations inside the heatmap. This should either use the string sep method.
    :param textcolors: A list or array of two color specifications.
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
