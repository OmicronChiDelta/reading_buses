# -*- coding: utf-8 -*-
"""
Functions to assist in analysing Reading Buses open source datasets

@author: Alex White
"""

import pandas as pd
import urllib
import re
import numpy as np

#def recover_times(url_times):
#    '''
#    Function to return timing information for a given service on a given day.
#    '''
#    return df_times


def parse_url(url, field_subset):
    '''
    Function to obtain a dataframe of data from Reading Buses API dumps
    Input:
        url: a url, structured according to the API schema
        field_subset: an optional list containing a subset of fields to extract
    Returns:
        df_op: The dataframe of data contained in the raw dump file
    '''
    dump = urllib.request.urlopen(url).read()
    string_dump = dump.decode('utf-8')

    regex_record = '\{(.*?)\},'
    records = re.findall(regex_record, string_dump)
    
    regex_field = '^.*?:|,.*?:'
    regex_data  = ':.*?,|:.*?$'
    
    #One-off inspection to get the fields:
    fields = re.findall(regex_field, records[0])
    fields = [f.replace(':', '').replace('"', '').replace(',', '') for f in fields]
    
    if field_subset != 'ALL':
        desired_indices = [fields.index(i) for i in field_subset]
        fields = field_subset
    
    #Set up space to save time
    df_op = pd.DataFrame(columns=fields, data=[['' for i in fields] for j in records])
    
    #Insert all data into frame
    for i, r in enumerate(records):    
        data  = re.findall(regex_data, r)
        data  = [d.replace(':', '').replace('"', '').replace(',', '') for d in data]
        
        #Save time by stripping out only the data we want
        if field_subset != 'ALL':
            data  = [data[i] for i in desired_indices]
        
        for j, f in enumerate(fields):
            df_op.at[i, f] = data[j] 
    return df_op


def cleanse_geometry(url_geometry, only_RGB=True, only_true_coords=True):
    '''
    Function cleanse aspects of the geometry data from the Reading Buses API
    Input:
        url_geometry: string specifying the url to open, containing the geometry info
        only_RGB: boolean, retain only Reading Buses records if True
        only_true_coords: boolean, get rid of (0, 0) lat/longs if True
    Returns:
        df_geometry: a pandas dataframe containing various fields, including the Lat/Long
        of stops, the route to which they belong etc. 
    '''
    #Obtain data
    df_geometry = parse_url(url_geometry, 'ALL')
            
    #Coerce latitude and longitude to floats
    df_geometry['longitude'] = df_geometry['longitude'].astype(float) 
    df_geometry['latitude'] = df_geometry['latitude'].astype(float) 
    
    #Unpack routes at locations where >1 route passes
    split_routes = pd.DataFrame(df_geometry['routes'].str.split('\\\/').tolist(), index=df_geometry.index).stack()
    split_routes = split_routes.reset_index().drop('level_1', axis=1)
    split_routes.rename({'level_0':'record', 0:'unpacked_route'}, axis=1, inplace=True)
                        
    #Merge the unpacked routes back in
    df_geometry = df_geometry.reset_index().rename({'index':'record'}, axis=1)
    df_geometry = df_geometry.merge(split_routes, how='left', on='record') 
    
    #Choose Reading Buses only
    if only_RGB:
        df_geometry = df_geometry.loc[df_geometry['operator_code'] == 'RGB'].reset_index(drop=True)
    
    #Choose "sensible" records only
    if only_true_coords:
        df_geometry= df_geometry.loc[(df_geometry['longitude'] != 0) & (df_geometry['latitude'] != 0)].reset_index(drop=True)
        
    return df_geometry