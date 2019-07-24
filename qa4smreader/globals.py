# -*- coding: utf-8 -*-
import cartopy.crs as ccrs

"""
Global variables collected from different sources.
"""

# === from qa4sm.validator.validation.graphics ===

_metric_value_ranges = { #from /qa4sm/validator/validation/graphics.py
    'R': [-1, 1], #TODO should we include negative correlation?
    'p_R': [0, 1], #probability that observed corellation is statistical fluctuation #TODO should we pin the upper value to 1 (extremely unlikely to happen)
    'rho': [-1, 1], #TODO should we include negative correlation?
    'p_rho': [0, 1], #probability that observed corellation is statistical fluctuation (probability of null hypothesis: there is no correlation) #TODO should we pin the upper value to 1 (extremely unlikely to happen)
    'rmsd': [0, None],
    'bias': [None, None],
    'n_obs': [0, None],
    'ubRMSD': [0, None],
    'RSS': [0, None],
    'mse' : [0, None], #[0, None] #mse only positive (https://en.wikipedia.org/wiki/Mean_squared_error)
    'mse_corr' : [0, None], #[0, None] #mse_corr only positive
    'mse_bias' : [0, None], #[0, None] #mse_bias only positive
    'mse_var' : [0, None], #[0, None] #mse_var only positive
}

# label format for all metrics
_metric_description = { #from /qa4sm/validator/validation/graphics.py
    'R': '',
    'p_R': '',
    'rho': '',
    'p_rho': '',
    'rmsd': r' in ${}$',
    'bias': r' in ${}$',
    'n_obs': '',
    'ubRMSD': r' in ${}$',
    'RSS': r' in $({})^2$',
    'mse' : '',
    'mse_corr' : '',
    'mse_bias' : '',
    'mse_var' : '',
}

# colormaps used for plotting metrics
# TODO: use colormap objects here instead of names
# more on colormaps: https://matplotlib.org/users/colormaps.html | https://morphocode.com/the-use-of-color-in-maps/
# colorcet: http://colorcet.pyviz.org/user_guide/Continuous.html

_cclasses = {
        'div_better' : 'RdYlBu', # diverging: 1 good, 0 special, -1 bad (pearson's R, spearman's rho') 'cet_coolwarm_r', 'cet_CET_D8_r'],
        'div_neutr' : 'RdYlGn', # diverging: zero good, +/- neutral: (bias):  'Spectral', 'cet_CET_D3', 'cet_gwv', 'cet_bwy', 'cet_bjy'],
        'seq_worse' : 'cet_CET_L4_r', # sequential: increasing value bad (p_R, p_rho, rmsd, ubRMSD, RSS, ):
        'seq_better' : 'cet_CET_L4' # sequential: increasing value good (n_obs):
            }

_colormaps = { #from /qa4sm/validator/validation/graphics.py
    'R': _cclasses['div_better'],
    'p_R': _cclasses['seq_worse'],
    'rho': _cclasses['div_better'],
    'p_rho': _cclasses['seq_worse'],
    'rmsd': _cclasses['seq_worse'],
    'bias': _cclasses['div_neutr'],
    'n_obs': _cclasses['seq_better'],
    'ubRMSD': _cclasses['seq_worse'],
    'mse' : _cclasses['seq_worse'],
    'mse_corr' : _cclasses['seq_worse'],
    'mse_bias' : _cclasses['seq_worse'],
    'mse_var' : _cclasses['seq_worse'],
}

# units for all datasets
_metric_units = { #from /qa4sm/validator/validation/graphics.py
    'ISMN': r'm^3 m^{-3}',
    'C3S': r'm^3 m^{-3}',
    'GLDAS': r'm^3 m^{-3}',
    'ASCAT': r'percentage of saturation',
    'SMAP': r'm^3 m^{-3}',
    'ERA5': r'm^3 m^{-3}'
}

# === from qa4sm.validator.validation.globals ===

# label name for all metrics
_metric_name = { #from /qa4sm/validator/validation/globals.py
    'R' : 'Pearson\'s r',
    'p_R' : 'Pearson\'s r p-value',
    'rho' : 'Spearman\'s rho',
    'p_rho' : 'Spearman\'s rho p-value',
    'rmsd' : 'Root-mean-square deviation',
    'bias' : 'Bias (difference of means)',
    'n_obs' : '# observations',
    'ubRMSD' : 'Unbiased root-mean-square deviation',
    'RSS' : 'Residual sum of squares',
    'mse' : 'Mean square error',
    'mse_corr' : 'Mean square error correlation',
    'mse_bias' : 'Mean square error bias',
    'mse_var' : 'Mean square error variance',
    }

# === plot defaults ===
matplotlib_ppi = 72
index_names = ['lat','lon']
dpi = 100
max_title_len = 50 #maximum length of plot title in chars. if longer, it will be broken in multiple lines.
title_pad = 12.0 # default padding is matplotlib.rcParams['axes.titlepad'] = 6.0
data_crs = ccrs.PlateCarree()

# === map plot defaults ===
scattered_datasets = ['ISMN'] #dataset names which require scatterplots (data is scattered in lat/lon)
map_figsize = [11.32,6.10]
naturalearth_resolution = '110m' #choose from '10m', '50m' and '110m'
crs = ccrs.PlateCarree()
markersize = 4 # diameter in points.
map_pad = 0.15 # padding relative to map height.
grid_intervals = [0.5,1,2,5,10,30] #grid delta to choose from (plotter will try to make 5 gridlines in the smaller dimension)

# === boxplot defaults ===
boxplot_printnumbers = True
boxplot_figsize = [6.30,4.68]

# === watermark defaults ===
watermark = u'made with QA4SM (qa4sm.eodc.eu)'
watermark_pos = 'top'
watermark_fontsize = 10 #in points
watermark_pad = 5 #in points (matplotlib uses 72ppi)

import qa4smreader.usecases as usecases #for debugging
if __name__ == '__main__':
    usecases.usecase()