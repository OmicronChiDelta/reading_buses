# -*- coding: utf-8 -*-
"""
Various pieces of analysis for the Reading Buses datasets

@author: Alex White
"""

import timeit
import pandas as pd
import sys
import matplotlib.pyplot as plt

utils_dir = 'C:\\Users\\Alex White\\Documents\GitHub\reading_buses'
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

from buses_utils import cleanse_geometry, parse_url



#%% Parameters
api_base           = 'https://rtl2.ods-live.co.uk//api'
api_key            = 'D24LEmypWC'
url_geometry       = '{}/busstops?key={}'.format(api_base, api_key)
url_services       = '{}/services?key={}'.format(api_base, api_key)
only_RGB           = True
only_valid_latlong = True
do_tracking_subset = True
track_service      = '17'
date_start         = '2019-01-01'
date_end           = '2019-01-31'
tracking_subset    = ['LineRef', 'LocationCode', 'LiveJourneyId', 'JourneyId', 'ScheduledStartTime', 'JourneyPattern',
                      'Sequence', 'ScheduledArrivalTime', 'ArrivalTime', 'ScheduledHeadway', 'ActualHeadway']



#%%Set up grid of dates to examine
desired_dates = pd.date_range(date_start, date_end)
desired_dates = [d.strftime('%Y-%m-%d') for d in desired_dates]



#%% Obtain network geometry        
#df_geometry = cleanse_geometry(url_geometry, only_RGB, only_valid_latlong)



#%% Obtain routes
#df_services = parse_url(url_services, [], False)
#if only_RGB:
#    df_services = df_services.loc[df_services['operator_code'] == 'RGB'].reset_index(drop=True)



#%% Obtain tracking information for a given service
df_final = pd.DataFrame()

start_time = timeit.default_timer() #start clock
for track_date in desired_dates:
    url_tracking = '{}/trackingHistory?key={}&service={}&date={}&vehicle=&location='.format(api_base, api_key, track_service, track_date)

    df_tracking = parse_url(url_tracking, tracking_subset, do_tracking_subset)    
    #The day of interest - for later segmentation
    df_tracking['calendar_day'] = track_date
    
    df_final = df_final.append(df_tracking[['calendar_day', 'ScheduledStartTime', 'JourneyId', 'Sequence', 'LocationCode', 'arrival_delta']])
elapsed = timeit.default_timer() - start_time #stop clock

#%% Cleanse
df_final['Sequence']              = df_final['Sequence'].astype(int) 
df_final['ScheduledStartTime']    = df_final['ScheduledStartTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S', errors='coerce'))
df_final['ScheduledArrivalTime']  = df_final['ScheduledArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S', errors='coerce'))
df_final['ArrivalTime']           = df_final['ArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))

#Time differences in decimal seconds
df_final['arrival_delta']   = (df_final['ArrivalTime'] - df_final['ScheduledArrivalTime']).astype('timedelta64[s]')  



#%% Visualise network geometry
#fig, ax = plt.subplots()
#group_geometry = df_geometry.groupby('group_name')
#for g in group_geometry:
#    ax.scatter(g[1]['longitude'].values, 
#               g[1]['latitude'].values,
#               marker='o',
#               s=20,
#               edgecolor='k',
#               alpha=0.5,
#               label=g[0])
#ax.set_xlabel('Longitude / degrees')
#ax.set_ylabel('Latitude / degrees')
#ax.set_title('Reading Buses network geometry')
#plt.legend()
    