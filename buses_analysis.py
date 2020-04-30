# -*- coding: utf-8 -*-
"""
Various pieces of analysis for the Reading Buses datasets

@author: Alex White
"""

import sys
import matplotlib.pyplot as plt

utils_dir = 'C:\\Users\\Alex White\\Documents\GitHub\reading_buses'
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

from buses_utils import cleanse_geometry, parse_url



#%% Parameters
api_key = 'D24LEmypWC'
url_geometry = 'https://rtl2.ods-live.co.uk//api/busstops?key={}'.format(api_key)
url_services = 'https://rtl2.ods-live.co.uk//api/services?key={}'.format(api_key)
only_RGB = True
only_valid_latlong = True



#%% Obtain network geometry        
df_geometry = cleanse_geometry(url_geometry, only_RGB, only_valid_latlong)



#%% Obtain routes
df_routes = parse_url(url_services)
if only_RGB:
    df_routes = df_routes.loc[df_routes['operator_code'] == 'RGB'].reset_index(drop=True)



#%% Show network geometry
fig, ax = plt.subplots()
group_geometry = df_geometry.groupby('group_name')
for g in group_geometry:
    ax.scatter(g[1]['longitude'].values, 
               g[1]['latitude'].values,
               marker='o',
               s=20,
               edgecolor='k',
               alpha=0.5,
               label=g[0])
ax.set_xlabel('Longitude / degrees')
ax.set_ylabel('Latitude / degrees')
ax.set_title('Reading Buses network geometry')
plt.legend()
    