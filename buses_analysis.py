# -*- coding: utf-8 -*-
"""
Various pieces of analysis for the Reading Buses datasets

@author: Alex White
"""
import sys

utils_dir = 'C:\\Users\\Alex White\\Documents\GitHub\reading_buses'
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

from buses_utils import recover_geometry

api_key = 'D24LEmypWC'
url_geometry = 'https://rtl2.ods-live.co.uk//api/busstops?key={}'.format(api_key)

#Obtain network geometry        
df_geometry = recover_geometry(url_geometry)


