# -*- coding: utf-8 -*-
"""
Various pieces of analysis for the Reading Buses datasets

@author: Alex White
"""

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
tracking_subset = ['LineRef', 'VehicleCode', 'DriverCode', 'LocationCode', 'LiveJourneyId', 'JourneyId',
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

df_tracking = parse_url(url_tracking)
df_tracking = df_tracking[tracking_subset]

#Ensure datetimes
df_tracking['ScheduledArrivalTime']   = df_tracking['ScheduledArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S', errors='coerce'))
df_tracking['ScheduledDepartureTime'] = df_tracking['ScheduledDepartureTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))
df_tracking['ArrivalTime']            = df_tracking['ArrivalTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))
df_tracking['DepartureTime']          = df_tracking['DepartureTime'].apply(lambda x: pd.to_datetime(x, format='%Y-%m-%d %H%M%S',  errors='coerce'))



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
    