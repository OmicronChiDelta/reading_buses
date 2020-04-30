# -*- coding: utf-8 -*-
"""
Various pieces of analysis for the Reading Buses datasets

@author: Alex White
"""

import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt

utils_dir = 'C:\\Users\\Alex White\\Documents\GitHub\reading_buses'
if utils_dir not in sys.path:
    sys.path.append(utils_dir)

from buses_utils import cleanse_geometry, parse_url



#%% Parameters
api_base = 'https://rtl2.ods-live.co.uk//api'
api_key = 'D24LEmypWC'
url_geometry = '{}/busstops?key={}'.format(api_base, api_key)
url_services = '{}/services?key={}'.format(api_base, api_key)
only_RGB = True
only_valid_latlong = True
tracking_subset = ['LineRef', 'VehicleCode', 'DriverCode', 'LocationCode', 'LiveJourneyId', 'JourneyId', 'ScheduledStartTime',
                   'JourneyPattern', 'Sequence', 'ScheduledArrivalTime', 'ScheduledDepartureTime', 
                   'ArrivalTime', 'DepartureTime', 'ScheduledHeadway', 'ActualHeadway']



#%% Obtain network geometry        
df_geometry = cleanse_geometry(url_geometry, only_RGB, only_valid_latlong)



#%% Obtain routes
df_services = parse_url(url_services)
if only_RGB:
    df_services = df_services.loc[df_services['operator_code'] == 'RGB'].reset_index(drop=True)



#%% Obtain tracking information for a given service
track_date = '2020-01-01'
track_service = '33'
url_tracking = '{}/trackingHistory?key={}&service={}&date={}&vehicle=&location='.format(api_base, api_key, track_service, track_date)

df_tracking = parse_url(url_tracking, tracking_subset)

#Cleanse types
df_tracking['ScheduledStartTime']     = df_tracking['ScheduledStartTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S', errors='coerce'))
df_tracking['ScheduledArrivalTime']   = df_tracking['ScheduledArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S', errors='coerce'))
df_tracking['ScheduledDepartureTime'] = df_tracking['ScheduledDepartureTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))
df_tracking['ArrivalTime']            = df_tracking['ArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))
df_tracking['DepartureTime']          = df_tracking['DepartureTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))
df_tracking['Sequence']               = df_tracking['Sequence'].astype(int) 



#%% Time differences in decimal seconds
df_tracking['dwell']           = (df_tracking['DepartureTime'] - df_tracking['ArrivalTime']).astype('timedelta64[s]')  
df_tracking['arrival_delta']   = (df_tracking['ArrivalTime'] - df_tracking['ScheduledArrivalTime']).astype('timedelta64[s]')  
df_tracking['departure_delta'] = (df_tracking['DepartureTime'] - df_tracking['ScheduledDepartureTime']).astype('timedelta64[s]')  



#%% On average, how do the deltas change along a given journey?
agg_journey = df_tracking.groupby(['JourneyPattern', 'Sequence']).agg({'dwell':'mean', 'arrival_delta':'mean', 'departure_delta':'mean'}).reset_index()
agg_journey.dropna(inplace=True)
agg_journey.sort_values(by=['JourneyPattern', 'Sequence'], inplace=True)



#%% On average, how do the deltas for a given journey change over the day?
agg_time = df_tracking.groupby(['JourneyPattern', 'ScheduledStartTime']).agg({'dwell':'mean', 'arrival_delta':'mean', 'departure_delta':'mean'}).reset_index()
agg_time.dropna(inplace=True)
agg_time.sort_values(by=['JourneyPattern', 'ScheduledStartTime'], inplace=True)



#%% Visualise time series for dwell vs. progress along each journey
journey_agg = agg_time.groupby('JourneyPattern')
fig, ax = plt.subplots()
for i in journey_agg:
    ax.plot(i[1]['dwell'].values, label=i[0])
ax.set_xlabel('Time index')
ax.set_ylabel('Mean dwell time / seconds')
plt.legend()



#%% Visualise time series for dwell vs. progress along each journey
time_agg = agg_journey.groupby('JourneyPattern')
fig, ax = plt.subplots()
for i in journey_agg:
    x = list(i[1]['Sequence'].values)
    ax.plot([100*(j/np.max(x)) for j in x], i[1]['dwell'].values, label=i[0])
ax.set_xlabel('% progress through journey')
ax.set_ylabel('Mean dwell time / seconds')
plt.legend()



#%% Visualise network geometry
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
    