# -*- coding: utf-8 -*-
"""
Functions to assist in analysing Reading Buses open source datasets

@author: Alex White
"""

import pandas as pd
import urllib
import re
import matplotlib.pyplot as plt
from matplotlib import cm


def visualise_route(df_tracker, service, track_journey, df_geometry):
    '''
    Function to colour code a route taken by a bus to visualise progress through it.
    Base geometry has no indication of how a route is traversed, only that certain stations
    are served by the route
    Input:
        service: string, indicating which bus "number" to visualise
        route: string, the path through the service's stops which is being followed
        df_geometry: dataframe, containing lat/longs, stoop id etc.        
    Output:
        fig: matplotlib figure object 
        ax: matplotlib axes object
    '''
    
    #Pick out the journey of interest
    df_journey = df_tracker.loc[df_tracker['JourneyPattern'] == track_journey][['JourneyPattern', 'Sequence', 'LocationCode']].reset_index(drop=True)
    df_journey.drop_duplicates(inplace=True)

    #Assign lat/long to each sequence value
    df_vis = df_journey.merge(df_geometry[['location_code', 'latitude', 'longitude']], how='left', left_on='LocationCode', right_on='location_code')
    df_vis.drop_duplicates(inplace=True)
    df_vis.sort_values(by='Sequence', ascending=True)
    df_vis['Sequence'] = df_vis['Sequence'].astype(int)
    
    #Red is the start, green is the end
    cmap = cm.get_cmap('RdYlGn')
    
    fig, ax = plt.subplots()
    
    #Show the basic route
    ax.plot(df_vis['longitude'].values, 
            df_vis['latitude'].values, 
            ls='-', 
            c='k',
            alpha=0.25,
            zorder=0)
    
    #Use colour to indicate progress
    stop_ax = ax.scatter(df_vis['longitude'].values, 
               df_vis['latitude'].values, 
               c=df_vis['Sequence'].values, 
               cmap=cmap, 
               marker='o',
               s=50,
               edgecolor='k',
               zorder=1)
    
    #Add colour bar
    cbar = plt.colorbar(stop_ax, ticks=[df_vis['Sequence'].min(), df_vis['Sequence'].max()])
    cbar.ax.set_yticklabels(['Start', 'End'])
    
    #Label up
    ax.set_xlabel('Longitude / degrees')
    ax.set_ylabel('Latitude / degrees')
    ax.set_title('Service: {} Journey Pattern: {}'.format(service, track_journey))
    plt.tight_layout()
    
    return fig, ax


def parse_url(url, field_subset):
    '''
    Function to obtain a dataframe of data from Reading Buses API dumps
    Input:
        url: a url, structured according to the API schema
        field_subset: an optional list containing a subset of fields to extract
    Returns:
        df_op: The dataframe of data contained in the raw dump file
    '''
    #Get data from the web
    dump = urllib.request.urlopen(url).read()
    string_dump = dump.decode('utf-8')
    
    df_op = pd.DataFrame(columns=field_subset)
    
    for f in field_subset:
        #Search directly for the fields of interest
        regex_data = '\"{}\":.*?,|\"{}\":.*?'.format(f, f) + '}'
        data = re.findall(regex_data, string_dump)
        
        #Remove rubbish
        data  = [d.replace(f, '').replace(':', '').replace('"', '').replace(',', '').replace('}', '') for d in data]
        
        #Push into data frame. This only works because the data is so clean. Previous line-by-line is more general. 
        df_op[f] = data
    return df_op



def cleanse_geometry(url_geometry, field_subset, only_RGB=True, only_true_coords=True):
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
    df_geometry = parse_url(url_geometry, field_subset)
            
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