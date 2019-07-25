# -*- coding: utf-8 -*-
"""
Contains an interface for opening QA4SM output files (*.nc), 
loading certain parts as pandas.DataFrame 
and producing plots using the dfplot module in this package.
Internally, xarray is used to open the NetCDF files.
"""
from qa4smreader import dfplot
from qa4smreader import globals
import xarray as xr
import matplotlib.pyplot as plt
import re
import os

import warnings

# === File level ===

def get_metrics(filepath):
    "Returns a list of metrics available in the current filepath"
    with xr.open_dataset(filepath) as ds:
        metrics = _get_metrics(ds)
        try:
            #metrics.remove('n_obs') #TODO: deal with n_obs
            metrics.remove('tau') #TODO: deal with tau: contains only nan, thus axes limits are nan and matplotlib throws an error.
            metrics.remove('p_tau')#line 115, in boxplot
            #ax.set_ylim(get_value_range(df, metric))
            #ValueError: Axis limits cannot be NaN or 
        except:
            pass
    return metrics

def _get_metrics(ds):
    varmeta = _get_varmeta(ds)
    metrics=list()
    for var in varmeta:
            if varmeta[var]['metric'] not in metrics: metrics.append(varmeta[var]['metric'])
    return metrics

def plot_all(filepath, metrics=None, extent=None, out_dir=None, out_type=None , boxplot_kwargs=dict(), mapplot_kwargs=dict()):
    """
    Creates boxplots for all metrics and map plots for all variables. Saves the output in a folder-structure.
    
    Parameters
    ----------
    filepath : str
        Path to the *.nc file to be processed.
    metric : str of list of str
        metric to be plotted.
        alternatively a list of variables can be given.
    extent : list
        [x_min,x_max,y_min,y_max] to create a subset of the data
    out_dir : [ None | str ], optional
        Parrent directory where to generate the folder structure for all plots.
        If None, defaults to the input filepath.
        The default is None.
    out_type : [ str | list | None ], optional
        The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
        If list, a plot is saved for each type.
        If None, no file is saved.
        The default is png.
    **plot_kwargs : dict, optional
        Additional keyword arguments that are passed to dfplot.
    """
    if type(out_type) is not list: out_type = [out_type]

    # === Metadata ===
    metrics=get_metrics(filepath)

    for metric in metrics:
        # === load data and metadata ===
        df, varmeta = load(filepath,metric,extent)

        # === make directory ===
        curr_dir = os.path.join(out_dir,metric)
        if not os.path.exists(curr_dir):
            os.makedirs(curr_dir)

        # === boxplot ===
        fig,ax = dfplot.boxplot(df, varmeta, **boxplot_kwargs)
        # === save ===
        out_name = 'boxplot_' + '__'.join([var for var in varmeta]) #TODO: write a function that produces meaningful names.
        for ending in out_type:
            fname = os.path.join(curr_dir,'{}.{}'.format(out_name,ending))
            plt.savefig(fname,dpi='figure')
            plt.close()

        # === mapplot ===
        for var in varmeta:
            if ( varmeta[var]['ds'] in globals.scattered_datasets or varmeta[var]['ref'] in globals.scattered_datasets ): #do scatterplot
                fig,ax = dfplot.scatterplot(df, var = var, meta = varmeta[var], **mapplot_kwargs)
            else:
                fig,ax = dfplot.mapplot(df, var = var, meta = varmeta[var], **mapplot_kwargs)
            # === save ===
            out_name = 'mapplot_' + var
            for ending in out_type:
                fname = os.path.join(curr_dir,'{}.{}'.format(out_name,ending))
                plt.savefig(fname,dpi='figure')
                plt.close()

def boxplot(filepath, metric, extent=None, out_dir=None, out_name=None, out_type=None , **plot_kwargs):
    """
    Creates a boxplot, displaying the variables corresponding to given metric.
    Saves a figure and returns Matplotlib fig and ax objects for further processing.
    
    Parameters
    ----------
    filepath : str
        Path to the *.nc file to be processed.
    metric : str of list of str
        metric to be plotted.
        alternatively a list of variables can be given.
    extent : list
        [x_min,x_max,y_min,y_max] to create a subset of the data
    out_dir : [ None | str ], optional
        Path to output generated plot. 
        If None, defaults to, the input filepath.
        The default is None.
    out_name : [ None | str ], optional
        Name of output file. 
        If None, defaults to a name that is generated based on the variables.
        The default is None.
    out_type : [ str | list | None ], optional
        The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
        If list, a plot is saved for each type.
        If None, no file is saved.
        The default is png.
    **plot_kwargs : dict, optional
        Additional keyword arguments that are passed to dfplot.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the axes for further processing.
    ax : matplotlib.axes.Axes or list of Axes objects
        Axes or list of axes containing the plot.

    """
    if type(metric) is str:
        variables = get_var(filepath, metric)
    else:
        variables = metric #metric already contais the variables to be plotted.

    # === Get ready... ===
    with xr.open_dataset(filepath) as ds:
        # === Get Metadata ===
        varmeta = _get_varmeta(ds, variables)
        # === Load data ===
        df = _load_data(ds, variables, extent, globals.index_names)

    # === plot data ===
    fig,ax = dfplot.boxplot(df=df, varmeta = varmeta, **plot_kwargs)

    # === save figure ===
    if out_type:
        if not out_dir: out_dir = os.path.dirname(__file__)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if not out_name: out_name = 'boxplot_' + '__'.join([var for var in variables]) #TODO: write a function that produces meaningful names.
        filename = os.path.join(out_dir,out_name)
        if type(out_type) is not list: out_type = [out_type]
        for ending in out_type:
            plt.savefig('{}.{}'.format(filename, ending), dpi='figure')
        plt.close()
        return
    elif out_name:
        if out_name.find('.') == -1: #append '.png'out_name contains no '.', which is hopefully followed by a meaningful file ending.
            out_name += '.png'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        filename = os.path.join(out_dir,out_name)
        plt.savefig(filename)
        plt.close()
        return
    else:
        return fig,ax

def mapplot(filepath, var, extent=None, out_dir=None, out_name=None, out_type=None, **plot_kwargs):
    """
    Plots data to a map, using the data as color. Plots a scatterplot for ISMN and a image plot for other input data.
    Saves a figure and returns Matplotlib fig and ax objects for further processing.
    
    Parameters
    ----------
    filepath : str
        Path to the *.nc file to be processed.
    var : str
        variable to be plotted.
    extent : list
        [x_min,x_max,y_min,y_max] to create a subset of the data
    out_dir : [ None | str ], optional
        Path to output generated plot. 
        If None, defaults to, the input filepath.
        The default is None.
    out_name : [ None | str ], optional
        Name of output file. 
        If None, defaults to a name that is generated based on the variables.
        The default is None.
    out_type : [ str | list | None ], optional
        The file type, e.g. 'png', 'pdf', 'svg', 'tiff'...
        If list, a plot is saved for each type.
        If None, no file is saved.
        The default is png.
    **plot_kwargs : dict, optional
        Additional keyword arguments that are passed to dfplot.

    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the axes for further processing.
    ax : matplotlib.axes.Axes or list of Axes objects
        Axes or list of axes containing the plot.

    """
    #TODO: do something when var is not a string but a list. (e.g. call list plot function)
    if type(var) == list: var = var[0]
    # === Get ready... ===
    with xr.open_dataset(filepath) as ds:
        # === Get Metadata ===
        meta = _get_meta(ds, var)
        # === Load data ===
        df = _load_data(ds, var, extent, globals.index_names)

    # === plot data ===
    if ( meta['ds'] in globals.scattered_datasets or meta['ref'] in globals.scattered_datasets ): #do scatterplot
        fig,ax = dfplot.scatterplot(df=df, var = var, meta = meta, **plot_kwargs)
    else:
        fig,ax = dfplot.mapplot(df=df, var = var, meta = meta, **plot_kwargs)

    # == save figure ===
    if out_type:
        if not out_dir:
            out_dir = os.path.dirname(__file__)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if not out_name:
            out_name = 'mapplot_' + var
        filename = os.path.join(out_dir,out_name)
        if type(out_type) is not list: out_type = [out_type]
        for ending in out_type:
            plt.savefig('{}.{}'.format(filename, ending), dpi='figure')
    elif out_name:
        if out_name.find('.') == -1: #append '.png'out_name contains no '.', which is hopefully followed by a meaningful file ending.
            out_name += '.png'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        filename = os.path.join(out_dir,out_name)
        plt.savefig(filename, dpi='figure')
    else:
        plt.show()
    plt.close()
    #return fig,ax

def load(filepath, metric, extent=None, index_names=globals.index_names):
    "returns DataFrame and varmeta"
    with xr.open_dataset(filepath) as ds:
        variables = _get_var(ds, metric)
        varmeta = _get_varmeta(ds, variables)
        df = _load_data(ds, variables, extent, index_names)
    return df, varmeta

def get_var(filepath, metric):
    "Searches the dataset in filepath for variables that contain a certain metric and returns a list of strings."
    with xr.open_dataset(filepath) as ds:
        variables = _get_var(ds,metric)
    return variables

def _get_var(ds, metric):
    "Searches the dataset for variables that contain a certain metric and returns a list of strings."
    if metric == 'n_obs': #n_obs is a special case, that does not match the usual pattern with *_between*
        return [metric]
    else:
        return [var for var in ds.data_vars if re.search(r'^{}_between'.format(metric), var, re.I)]

def load_data(filepath, variables, extent=None, index_names=globals.index_names):
    """
    converts xarray.DataSet to pandas.DataFrame, reading only relevant variables and multiindex
    """
    with xr.open_dataset(filepath) as ds:
        df = _load_data(ds, variables, extent, index_names)
    return df

def _load_data(ds, variables, extent, index_names):
    """
    converts xarray.DataSet to pandas.DataFrame, reading only relevant variables and multiindex
    """
    if type(variables) is str: variables = [variables] #convert to list of string
    try:
        df = ds[index_names + variables].to_dataframe()
    except KeyError as e:
        raise Exception('The given variabes '+ ', '.join(variables) + ' do not match the names in the input data.' + str(e))
    df.dropna(axis='index',subset=variables, inplace=True)
    if extent: # === geographical subset ===
        lat,lon = globals.index_names
        df=df[ (df.lon>=extent[0]) & (df.lon<=extent[1]) & (df.lat>=extent[2]) & (df.lat<=extent[3]) ]
    return df

def get_meta(filepath,var):
    """
    parses the var name and gets metadata from tha *.nc dataset.
    checks consistency between the dataset and the variable name.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_meta(ds,var)

def _get_meta(ds,var):
    """
    parses the var name and gets metadata from tha *.nc dataset.
    checks consistency between the dataset and the variable name.
    """
    def _get_pretty_name(ds, name, number):
        """ 
        Returns pretty_name, version and version_pretty_name.
        First tries to find info from ds.attrs.
        Then falls back to globals.
        Then falls back to using name as pretty name.
        """
        try:
            pretty_name = ds.attrs['val_dc_pretty_name' + str(number-1)]
        except KeyError:
            try:
                pretty_name = globals._dataset_pretty_names[name]
            except KeyError:
                pretty_name = name
        try:
            version = ds.attrs['val_dc_version' + str(number-1)]
            try:
                version_pretty_name = ds.attrs['val_dc_version_pretty_name' + str(number-1)]
            except KeyError:
                try:
                    version_pretty_name = globals._dataset_version_pretty_names[version]
                except KeyError:
                    version_pretty_name = version
        except KeyError:
            version = 'unknown'
            version_pretty_name = 'unknown version'
        return pretty_name, version, version_pretty_name

    # === consistency with dataset ===
    if not var in ds.data_vars:
        raise Exception('The given var \'{}\' is not contained in the dataset.'.format(var))
    # === parse var ===
    meta = dict()
    try:
        pattern = re.compile(r"""(\D+)_between_(\d+)-(\S+)_(\d+)-(?P<dataset>\S+)""") #'ubRMSD_between_4-ISMN_3-ESA_CCI_SM_combined'
        match = pattern.match(var)
        meta['metric'] = match.group(1)
        meta['ref_no'] = int(match.group(2))
        meta['ref'] = match.group(3)
        meta['ds_no'] = int(match.group(4))
        meta['ds'] = match.group(5)
    except AttributeError:
        if var == 'n_obs': #catch error occuring when var is 'n_obs'
            meta['metric'] = 'n_obs'
            meta['ref_no'] = 1 #TODO: find a way to not hard-code this!
            meta['ref'] = 'GLDAS'
            meta['ds_no'] = 1
            meta['ds'] = 'GLDAS'
        else:
            raise Exception('The given var \'{}\' does not match the regex pattern.'.format(var))
    # === get pretty names ===
    for i in ('ds','ref'):
        name = meta[i]
        number = meta[i+'_no']
        pretty_name,version,version_pretty_name = _get_pretty_name(ds,name,number)
        meta[i+'_pretty_name'] = pretty_name
        meta[i+'_version'] = version
        meta[i+'_version_pretty_name'] = version_pretty_name
    return meta

def get_varmeta(filepath, variables=None):
    """
    get meta for all variables and return a nested dict.
    """
    with xr.open_dataset(filepath) as ds:
        return _get_varmeta(ds,variables)

def _get_varmeta(ds,variables=None):
    """
    get meta for all variables and return a nested dict.
    """
    if not variables: #take all variables.
        variables=list(ds.data_vars)
        for index in (*globals.index_names, 'gpi'): #remove lat, lon, gpi
            try:
                variables.remove(index)
            except ValueError:
                warnings.warn('{} is not in variables.'.format(index))
    return {var:_get_meta(ds,var) for var in variables}


# testfile = '5-ISMN.soil moisture_with_1-C3S.sm_with_2-SMAP.soil_moisture_with_3-ASCAT.sm_with_4-SMOS.Soil_Moisture.nc'
# filepath = os.path.join('tests', 'test_data', testfile)
# plot_all(filepath)