# -*- coding: utf-8 -*-
"""
Functions to assist in analysing Reading Buses open source datasets

@author: Alex White
"""

import pandas as pd
import urllib
import re
import numpy as np

def recover_geometry(url_geometry):
    '''
    Function to parse the network geometry dumped via the API.
    Input:
        url_geometry: string specifying the url to open, containing the geometry info
    Returns:
        df_geometry: a pandas dataframe containing various fields, including the Lat/Long
        of stops, the route to which they belong etc. 
    '''
    
    dump_geometry = urllib.request.urlopen(url_geometry).read()
    string_geometry = dump_geometry.decode('utf-8')

    regex_record = '\{(.*?)\},'
    records = re.findall(regex_record, string_geometry)
    
    regex_field = '^.*?:|,.*?:'
    regex_data  = ':.*?,|:.*?$'
    
    #One-off inspection to get the fields:
    fields = re.findall(regex_field, records[0])
    fields = [f.replace(':', '').replace('"', '').replace(',', '') for f in fields]
    
    #Set up space to save time
    df_geometry = pd.DataFrame(columns=fields, data=[['' for i in fields] for j in records])
    
    #Insert all data into frame
    for i, r in enumerate(records):    
        data  = re.findall(regex_data, r)
        data  = [d.replace(':', '').replace('"', '').replace(',', '') for d in data]
    
        for j, f in enumerate(fields):
            df_geometry.at[i, f] = data[j] 
            
    #Coerce latitude and longitude to floats
    df_geometry['longitude'] = df_geometry['longitude'].astype(float) 
    df_geometry['latitude'] = df_geometry['latitude'].astype(float) 
    return df_geometry