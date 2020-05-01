# -*- coding: utf-8 -*-
"""
Various pieces of analysis for the Reading Buses datasets

@author: Alex White
"""

import timeit
import pandas as pd
import sys
import matplotlib.pyplot as plt
import matplotlib

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
track_service      = '15'
date_start         = '2019-01-01'
date_end           = '2019-03-31'
subset_tracking    = ['LocationCode', 'LiveJourneyId', 'JourneyId', 'ScheduledStartTime', 'JourneyPattern',
                      'Sequence', 'ScheduledArrivalTime', 'ArrivalTime']
subset_geometry    = ["location_code", "bay_no", "description", "latitude", "longitude", "route_code", "operator_code",
                      "routes", "bearing", "group_name"]
                   

#%%Set up grid of dates to examine
desired_dates = pd.date_range(date_start, date_end)
desired_dates = [d.strftime('%Y-%m-%d') for d in desired_dates]



#%% Obtain network geometry        
#df_geometry = cleanse_geometry(url_geometry, subset_geometry, only_RGB, only_valid_latlong)



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



#%% Obtain routes
#df_services = parse_url(url_services, [], False)
#if only_RGB:
#    df_services = df_services.loc[df_services['operator_code'] == 'RGB'].reset_index(drop=True)



#%% Obtain tracking information for a given service
#Space to store dataframes for each day
list_tracking = [None]*len(desired_dates)

for i, track_date in enumerate(desired_dates):
    url_tracking = '{}/trackingHistory?key={}&service={}&date={}&vehicle=&location='.format(api_base, api_key, track_service, track_date)

    df_tracking = parse_url(url_tracking, subset_tracking)
    
    #The day of interest - for later segmentation
    df_tracking['calendar_day'] = track_date
    
    list_tracking[i] = df_tracking

#Flatten into a final dataframe.     
df_final = pd.concat(list_tracking)



#%% Cleanse
df_final['Sequence']              = df_final['Sequence'].astype(int) 
df_final['ScheduledStartTime']    = df_final['ScheduledStartTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S', errors='coerce'))
df_final['ScheduledArrivalTime']  = df_final['ScheduledArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S', errors='coerce'))
df_final['ArrivalTime']           = df_final['ArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))

#Time differences in decimal seconds
df_final['arrival_delta']   = (df_final['ArrivalTime'] - df_final['ScheduledArrivalTime']).astype('timedelta64[s]')  



#%% Stats and plotting
temporal_variance = df_final.groupby(['calendar_day', 'LocationCode']).agg({'arrival_delta':'mean'}).rename({'arrival_delta':'mean'}, axis=1).reset_index()
journey_breakdown = temporal_variance.groupby('LocationCode')

fig, ax = plt.subplots()
for j in journey_breakdown:
    j[1].sort_values(by='calendar_day', inplace=True)
    
    x = j[1]['calendar_day'].apply(lambda x: pd.to_datetime(x))
    x  = matplotlib.dates.date2num(x)
    
    ax.plot_date(x, j[1]['mean'].values, label=j[0], marker='None', linestyle='-', alpha=0.25, c='tomato')
ax.set_xlabel('Day index')
ax.set_ylabel('std of arrival delta / seconds')
ax.set_xticks(desired_dates)
ax.set_xticklabels(desired_dates)
plt.xticks(rotation=90)
#plt.tight_layout()
    
    