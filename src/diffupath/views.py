# -*- coding: utf-8 -*-

"""Visualization methods."""

import chart_studio.plotly as py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objs as go
from matplotlib_venn import venn3


def heatmap(
        data, row_labels, col_labels, ax=None, cbar_kw=None, cbarlabel="", title="", **kwargs
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


def annotate_heatmap(
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


def show_heatmap(count, percentage, databases, entity_types):
    """Show heatmap"""
    fig, ax = plt.subplots(figsize=(15, 7))

    im, cbar = heatmap(percentage, databases, entity_types, ax=ax,
                       cmap="YlGn", cbarlabel="percentage [0-1]")
    texts = annotate_heatmap(im, entity_count=count, valfmt="{x:1} ")

    fig.tight_layout()
    ax.set_title("Dataset 1 DiffuPath Mapping")

    plt.show()


def box_plot_from_dict(d, title='Box plot', x_title='x', y_title='y'):
    """Plot boxplot."""
    data = [go.Box(
        y=v,
        name=k
    ) for k, v in d.items()
    ]

    layout = go.Layout(
        title=go.layout.Title(
            text=title,
            xref='paper'
        ),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text=x_title
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text=y_title
            )
        )
    )

    fig = go.Figure(data=data, layout=layout)

    return py.iplot(fig)


def box_plot_from_two_dimension_dict(d, y_label='y'):
    """Boxplot two dimensions."""
    x = [k2 for k1, v1 in d.items() for k2, v2 in v1.items() for i in range(len(v2))]

    color_palete = ['#FF4136', '#3d9970', '#344f9e', '#bfc464']
    color_dict = {}
    i = 0

    for k, v in d.items():
        color_dict[k] = color_palete[i]
        i += 1

    data = [go.Box(
        y=[i for k2, v2 in v1.items() for i in v2],
        x=x,
        name=k1,
        marker=dict(
            color=color_dict[k1]
        )
    ) for k1, v1 in d.items()]

    layout = go.Layout(
        yaxis=dict(
            title=y_label,
            zeroline=False
        ),
        boxmode='group'
    )
    fig = go.Figure(data=data, layout=layout)

    return py.iplot(fig)


def show_venn_diagram(intersections, set_labels=('KEGG', 'Reactome', 'WikiPathways')):
    """Show venn diagram."""
    intersections_len = [len(intersection) for name, intersection in intersections.items()]

    plt.figure(figsize=(17, 8))
    v = venn3(subsets=intersections_len, set_labels=set_labels)

    plt.show()
