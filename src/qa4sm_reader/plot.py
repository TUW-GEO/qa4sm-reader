# -*- coding: utf-8 -*-
import os
import re

import seaborn as sns
from matplotlib import pyplot as plt

from qa4sm_reader import globals
from qa4sm_reader.dfplot import get_value_range, init_plot, get_plot_extent, geotraj_to_geo2d, _make_cbar, _make_title, \
    style_map, make_watermark, _get_globmeta
from qa4sm_reader.ncplot import get_metrics


def mapplot(df, var, meta, title=None, label=None, plot_extent=None,
            colormap=None, figsize=globals.map_figsize, dpi=globals.dpi,
            projection=None, watermark_pos=globals.watermark_pos,
            add_title=True, add_cbar=True,
            **style_kwargs):
    """
    Create an overview map from df using df[var] as color.
    Plots a scatterplot for ISMN and a image plot for other input data.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'lat', 'lon' and 'var' Series.
    var : str
        variable to be plotted.
    meta : dict
        dictionary of metadata. See interface.get_meta().
    title : str, optional
        Title of the plot. If None, a title is autogenerated from metadata.
        The default is None.
    label : str, optional
        Label of the colorbar. If None, a label is autogenerated from metadata.
        The default is None.
    plot_extent : tuple
        (x_min, x_max, y_min, y_max) in Data coordinates. The default is None.
    colormap : str, optional
        colormap to be used.
        If None, defaults to globals._colormaps.
        The default is None.
    figsize : tuple, optional
        Figure size in inches. The default is globals.map_figsize.
    dpi : int, optional
        Resolution for raster graphic output. The default is globals.dpi.
    projection : cartopy.crs, optional
        Projection to be used. If none, defaults to globals.map_projection.
        The default is None.
    watermark_pos : str, optional
        Placement of watermark. 'top' | 'bottom' | None.
        If None, no watermark gets placed.
        The default is globals.watermark_pos.
    add_title : bool, optional
        The default is True.
    add_cbar : bool, optional
        Add a colorbar. The default is True.
    **style_kwargs :
        Keyword arguments for plotter.style_map().

    Returns
    -------
    fig : matplotlib.figure

    ax : matplotlib.axes
        axes containing the plot without colorbar, watermark etc.
    """
    # === value range ===
    v_min, v_max = get_value_range(df[var], meta['metric'])

    # === init plot ===
    fig, ax, cax = init_plot(figsize, dpi, add_cbar, projection)

    if not colormap:
        colormap = globals._colormaps[meta['metric']]
    cmap = plt.cm.get_cmap(colormap)

    # === scatter or mapplot ===
    if (meta['ds'] in globals.scattered_datasets or
            meta['ref'] in globals.scattered_datasets):  # === scatterplot ===
        # === coordiniate range ===
        if not plot_extent:
            plot_extent = get_plot_extent(df)

        # === marker size ===
        markersize = globals.markersize ** 2  # in points**2

        # === plot ===
        lat, lon = globals.index_names
        im = ax.scatter(df[lon], df[lat], c=df[var],
                        cmap=cmap, s=markersize, vmin=v_min, vmax=v_max, edgecolors='black',
                        linewidths=0.1, zorder=2, transform=globals.data_crs)
    else:  # === mapplot ===
        # === coordiniate range ===
        if not plot_extent:
            plot_extent = get_plot_extent(df, grid=True)

        # === prepare data ===
        zz, zz_extent = geotraj_to_geo2d(df, var)

        # === plot ===
        im = ax.imshow(zz, cmap=cmap, vmin=v_min, vmax=v_max,
                       interpolation='nearest', origin='lower',
                       extent=zz_extent,
                       transform=globals.data_crs, zorder=2)

    # === add colorbar ===
    if add_cbar:
        _make_cbar(fig, im, cax, df[var], v_min, v_max, meta, label)

    # === style ===
    if add_title:
        _make_title(ax, meta, title)
    style_map(ax, plot_extent, **style_kwargs)

    # === layout ===
    fig.canvas.draw()  # very slow. necessary bcs of a bug in cartopy: https://github.com/SciTools/cartopy/issues/1207
    plt.tight_layout()  # pad=1)  # pad=0.5,h_pad=1,w_pad=1,rect=(0, 0, 1, 1))

    # === watermark ===
    if watermark_pos:
        make_watermark(fig, watermark_pos)

    return fig, ax


def boxplot(df, varmeta, title=None, label=None, print_stat=globals.boxplot_printnumbers,
            watermark_pos=globals.watermark_pos, figsize=None,
            dpi=globals.dpi, add_title=True, title_pad=globals.title_pad):
    """
    Create a boxplot from the variables in df.
    The box shows the quartiles of the dataset while the whiskers extend
    to show the rest of the distribution, except for points that are
    determined to be “outliers” using a method that is a function of
    the inter-quartile range.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'lat', 'lon' and (multiple) 'var' Series.
    varmeta : dict
        dictionary of metadata for each var. See interface.get_varmeta().
    title : str, optional
        Title of the plot. If None, a title is autogenerated from metadata.
        The default is None.
    label : str, optional
        Label of the y axis, describing the metric. If None, a label is autogenerated from metadata.
        The default is None.
    print_stat : bool, optional
        Wheter to print median, standard derivation and n_obs .
        The default is globals.boxplot_printnumbers.
    watermark_pos : str, optional
        Placement of watermark. 'top' | 'bottom' | None.
        If None, no watermark gets placed.
        The default is globals.watermark_pos.
    figsize : tuple, optional
        Figure size in inches. The default is globals.map_figsize.
    dpi : int, optional
        Resolution for raster graphic output. The default is globals.dpi.
    add_title : bool, optional
        The default is True.
    title_pad : float, optional
        pad the title by title_pad pt. The default is globals.title_pad.

    Returns
    -------
    fig : TYPE
        DESCRIPTION.
    ax : TYPE
        DESCRIPTION.

    """
    # === select only relevant variables, creating a view of the passed DataFrame.
    # This preserves also renaming the columns of the original DataFrame.
    df = df[varmeta]

    # === rename columns = label of boxes ===
    if print_stat:
        df.columns = ['{0}\n({1})\nmedian: {2:.3g}\nstd. dev.: {3:.3g}\nN obs.: {4:d}'.format(
            varmeta[var]['short_to_pretty'],
            varmeta[var]['ds_version_pretty_name'],
            df[var].median(),
            df[var].std(),
            df[var].count()) for var in varmeta]
    else:
        df.columns = ['{}\n{}'.format(
            varmeta[var]['short_to_pretty'],
            varmeta[var]['ds_version_pretty_name']) for var in varmeta]

    # === plot ===
    if not figsize:
        # figsize = globals.boxplot_figsize
        figsize = [globals.boxplot_width*(1+len(df.columns)), globals.boxplot_height]
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    sns.set_style("whitegrid")  # TODO: Bug. does not work for the first plot (test_boxplot_ISMN_default()) for some strange reason!!!
    ax = sns.boxplot(data=df, ax=ax, width=0.15, showfliers=False, color='white')
    sns.despine()  # remove ugly spines (=border around plot) right and top.

    # === style ===
    globmeta = _get_globmeta(varmeta)
    metric = globmeta['metric']
    ax.set_ylim(get_value_range(df, metric))
    if not label:
        label = (globals._metric_name[metric] +
                 globals._metric_description[metric].format(globals._metric_units[globmeta['ref']]))
    ax.set_ylabel(label, weight='normal')  # TODO: Bug: If a circumflex ('^') is in the string, it becomes bold.)

    # === generate title with automatic line break ===
    if add_title:
        if not title:
            max_title_len = globals.boxplot_title_len * len(df.columns)
            if globmeta['metric'] == 'n_obs':  # special case n_obs.
                title = list()  # each list element is a line in the plot title
                title.append(
                    'Number of spacial and temporal matches between {} ({})'.format(globmeta['ref_pretty_name'],
                                                                                    globmeta['ref_version_pretty_name']))
                for name in varmeta['n_obs']['short_to_pretty']:  # TODO: have a look at parawrap (https://www.tutorialspoint.com/python/python_text_wrapping) or textwrap (https://www.geeksforgeeks.org/textwrap-text-wrapping-filling-python/)
                    to_append = '{}, '.format(name)
                    if len(title[-1] + to_append) <= max_title_len:  # line not to long: add to current line
                        title[-1] += to_append
                    else:  # add to next line
                        title.append(to_append)
            else:
                title = list()  # each list element is a line in the plot title
                title.append(
                    'Comparing {} ({}) to '.format(globmeta['ref_pretty_name'], globmeta['ref_version_pretty_name']))
                for var in varmeta:
                    to_append = '{}, '.format(varmeta[var]['short_to_pretty'])
                    if len(title[-1] + to_append) <= max_title_len:  # line not to long: add to current line
                        title[-1] += to_append
                    else:  # add to next line
                        title.append(to_append)
            title = '\n'.join(title)[:-2]  # join lines together and remove last ', '
            title = ' and '.join(title.rsplit(', ', 1))  # replace last ', ' with ' and '
        ax.set_title(title, pad=title_pad)

    # === watermark ===
    plt.tight_layout()
    if watermark_pos:
        make_watermark(fig, watermark_pos)
    return fig, ax


def plot_all(filepath, metrics=None, extent=None, out_dir=None, out_type='png', boxplot_kwargs=dict(),
             mapplot_kwargs=dict()):
    """
    Creates boxplots for all metrics and map plots for all variables. Saves the output in a folder-structure.

    Parameters
    ----------
    filepath : str
        Path to the *.nc file to be processed.
    metrics : set or list
        metrics to be plotted.
    extent : list
        [x_min,x_max,y_min,y_max] to create a subset of the data
    out_dir : [ None | str ], optional
        Parrent directory where to generate the folder structure for all plots.
        If None, defaults to the current working directory.
        The default is None.
    out_type : [ str | list | None ], optional
        The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
        If list, a plot is saved for each type.
        If None, no file is saved.
        The default is png.
    **plot_kwargs : dict, optional
        Additional keyword arguments that are passed to dfplot.
    """
    fnames = list()  # list to store all filenames.

    if not out_dir:
        out_dir = os.path.join(os.getcwd(), os.path.basename(filepath))

    # === Metadata ===
    if not metrics:
        metrics = get_metrics(filepath)

    for metric in metrics:
        # === load data and metadata ===
        df, varmeta = load(filepath, metric, extent)

        # === boxplot ===
        fig, ax = qa4sm_reader.plot.boxplot(df, varmeta, **boxplot_kwargs)

        # === save ===
        curr_dir = os.path.join(out_dir, metric)
        out_name = 'boxplot_{}'.format(metric)
        curr_dir, out_name, out_type = _get_dir_name_type(curr_dir, out_name, out_type)
        if not os.path.exists(curr_dir):
            os.makedirs(curr_dir)
        for ending in out_type:
            fname = os.path.join(curr_dir, out_name+ending)
            plt.savefig(fname, dpi='figure')
            fnames.append(fname)

        plt.close()

        # === mapplot ===
        for var in varmeta:
            meta = varmeta[var]
            # === plot ===
            fig, ax = qa4sm_reader.plot.mapplot(df, var=var, meta=meta, **mapplot_kwargs)

            # === save ===
            ds_match = re.match(r'.*_between_(([0-9]+)-(.*)_([0-9]+)-(.*))', var)
            if ds_match:
                pair_name = ds_match.group(1)
            else:
                pair_name = var  # e.g. n_obs

            if metric == pair_name:  # e.g. n_obs
                out_name = 'overview_{}'.format(metric)
            else:
                out_name = 'overview_{}_{}'.format(pair_name, metric)

            for ending in out_type:
                fname = os.path.join(curr_dir, out_name+ending)
                plt.savefig(fname, dpi='figure')
                fnames.append(fname)

            plt.close()

    return fnames