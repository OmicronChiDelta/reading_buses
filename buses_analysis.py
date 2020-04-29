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

from buses_utils import recover_geometry

api_key = 'D24LEmypWC'
url_geometry = 'https://rtl2.ods-live.co.uk//api/busstops?key={}'.format(api_key)

#Obtain network geometry        
df_geometry = recover_geometry(url_geometry)

#Drop records which have nonsense coordinates
df_valid_geom = df_geometry.loc[(df_geometry['longitude'] != 0) & (df_geometry['latitude'] != 0)].reset_index(drop=True)

#Only reading buses:
df_valid_geom = df_valid_geom.loc[df_valid_geom['operator_code'] == 'RGB'].reset_index(drop=True)

#Show network geometry
fig, ax = plt.subplots()
group_geometry = df_valid_geom.groupby('group_name')
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
    