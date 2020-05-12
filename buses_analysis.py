# -*- coding: utf-8 -*-
"""
Various pieces of analysis for the Reading Buses datasets

@author: Alex White
"""

import pandas as pd
import sys
import matplotlib.pyplot as plt
import os
from matplotlib import cm

#%% ADJUST THIS: ABSOLUTE PATH TO YOUR CLONED COPY
utils_dir = 'C:\\Users\\Alex White\\Documents\\GitHub\\reading_buses'

if utils_dir not in sys.path:
    sys.path.append(utils_dir)

from buses_utils import cleanse_geometry, parse_url, visualise_route



#%% Parameters
api_base            = 'https://rtl2.ods-live.co.uk//api'
api_key             = 'D24LEmypWC'
url_geometry        = '{}/busstops?key={}'.format(api_base, api_key)
url_services        = '{}/services?key={}'.format(api_base, api_key)
only_RGB            = True
only_valid_latlong  = True
do_tracking_subset  = True
save_journey_vis    = True
make_csv            = True
track_service       = '16'
journey_perc_thresh = 10
date_start          = '2020-01-01'
date_end            = '2020-04-01'
extraction_id       = track_service + '_' + date_start.replace('-', '') + '_' + date_end.replace('-', '')
subset_tracking     = ['LocationCode', 'LiveJourneyId', 'JourneyId', 'ScheduledStartTime', 'JourneyPattern',
                       'Sequence', 'ScheduledArrivalTime', 'ArrivalTime']
subset_geometry     = ["location_code", "bay_no", "description", "latitude", "longitude", "route_code", "operator_code",
                       "routes", "bearing", "group_name"]
subset_services     = ["operator_code", "route_code", "group_name", "id"]



#%%Set up grid of dates to examine
desired_dates = pd.date_range(date_start, date_end)
desired_dates = [d.strftime('%Y-%m-%d') for d in desired_dates]



#%% Obtain network geometry        
df_geometry = cleanse_geometry(url_geometry, subset_geometry, only_RGB, only_valid_latlong)



#%% Visualise network geometry
# fig_geo, ax_geo = plt.subplots()
# group_geometry = df_geometry.groupby('group_name')
# for g in group_geometry:
#     ax_geo.scatter(g[1]['longitude'].values, 
#               g[1]['latitude'].values,
#               marker='o',
#               s=20,
#               edgecolor='k',
#               alpha=0.5,
#               label=g[0])
# ax_geo.set_xlabel('Longitude / degrees')
# ax_geo.set_ylabel('Latitude / degrees')
# ax_geo.set_title('Reading Buses network geometry')
# plt.legend()



#%% Obtain Services
# df_services = parse_url(url_services, subset_services)
# if only_RGB:
#     df_services = df_services.loc[df_services['operator_code'] == 'RGB'].reset_index(drop=True)



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

#Some minor recording errors exist where some jounreys have duplication in their sequence
df_final.drop_duplicates(['LiveJourneyId', 'ScheduledStartTime', 'Sequence'], inplace=True)

#Drop any records with no live journey ID
df_final = df_final.loc[df_final['LiveJourneyId'] != ''].reset_index(drop=True)



#%% Store for later
if make_csv:
    extracts_dir = os.path.join(utils_dir, 'extractions', extraction_id)
    
    #Set up directory structure if needed
    if not os.path.exists(extracts_dir):
        os.makedirs(extracts_dir)

    df_final.to_csv(os.path.join(extracts_dir, 'arrival_history.csv'), index=False)
    
    
    
#%% Variation by timetabled stop...    
stat = 'var'
stop_summary = df_final[['LocationCode', 'arrival_delta']].groupby('LocationCode').agg({'arrival_delta':stat}).reset_index()

#Merge in geometry
stop_summary = stop_summary.merge(df_geometry[['location_code', 'unpacked_route', 'latitude', 'longitude']], how='left', left_on='LocationCode', right_on='location_code')
stop_summary['unpacked_route'] = stop_summary['unpacked_route'].astype(str)
stop_summary = stop_summary.loc[stop_summary['unpacked_route'] == track_service].reset_index(drop=True)

ordered_summary = stop_summary.sort_values(by='arrival_delta', ascending=False)

#Arrange raw data according to summary statistic
stat_dict = dict(list(df_final[['LocationCode', 'arrival_delta']].groupby('LocationCode')))
stat_dict = {i:list(stat_dict[i]['arrival_delta'].dropna().values) for i in ordered_summary['LocationCode']}

#Boxplot representation
fig_bo, ax_bo = plt.subplots()
ax_bo.boxplot(stat_dict.values(), vert=True, showfliers=False)

#...or using coloured route geometry
fig_go, ax_go = plt.subplots()
cmap = cm.get_cmap('RdYlGn')
ax_go.scatter(stop_summary['longitude'].values,
              stop_summary['latitude'].values,
              c=stop_summary['arrival_delta'].values,
              cmap=cmap,
              edgecolor='k',
              alpha=1,
              s=50)
ax_go.set_xlabel('Latitude / degrees')
ax_go.set_ylabel('Longitude / degrees')

#Colour bar...
cbar = plt.colorbar(ax_go, ticks=[stop_summary['arrival_delta'].min(), stop_summary['arrival_delta'].max()])
plt.tight_layout()
    

#%% % of journeys allocated to each pattern
# jp_distro = df_final.groupby(['JourneyPattern', 'LiveJourneyId']).agg({'Sequence':'count'}).reset_index()
# jp_distro  = jp_distro.groupby('JourneyPattern').agg({'LiveJourneyId':'count'}).reset_index()
# jp_distro.rename({'LiveJourneyId':'percentage'}, axis=1, inplace=True)
# jp_distro['percentage'] = 100*jp_distro['percentage']/jp_distro['percentage'].sum()
# jp_distro.sort_values(by='percentage', ascending=False, inplace=True)



#%% Visualise allocation of patterns 
# fig_d, ax_d = plt.subplots()
# ax_d.bar(jp_distro['JourneyPattern'].values, jp_distro['percentage'].values, facecolor='dodgerblue', edgecolor='k', alpha=0.5)
# ax_d.axhline(journey_perc_thresh, ls='--', c='r')
# ax_d.set_xlabel('Journey Pattern')
# ax_d.set_ylabel('Percentage of journeys made / %')
# ax_d.set_title('Allocation of journey patterns \n Service: {} ({} - {})'.format(track_service, date_start.replace('-', ''), date_end.replace('-', '')))
# plt.xticks(rotation=90)
# plt.tight_layout()



#%% Visualise pattern geometry - this is a bit shaky. JourneyPattern is not as solid as I would like (i.e doesn't always correspond to a unique type of 
#traversal through the network - probably better to just focus on the arrival discrepancy at each location)
# if save_journey_vis:
#     vis_dir = os.path.join(utils_dir, 'figures', extraction_id)
    
#     #Set up directory structure if needed
#     if not os.path.exists(vis_dir):
#         os.makedirs(vis_dir)
    
#     #Visualise the journeys and save
#     for j in df_final.groupby('JourneyPattern'):
#         fig_j, ax_j = visualise_route(j[1], track_service, j[0], df_geometry)
#         use_perc = jp_distro.loc[jp_distro['JourneyPattern'] == j[0]]['percentage'].values[0]
#         ax_j.set_title(ax_j.get_title() + ' Prevalence: {:.2f}%'.format(use_perc))
#         plt.savefig(os.path.join(vis_dir, j[0] + '.png'))
    


#%% Stats and plotting
# temporal_variance = df_final.groupby(['calendar_day', 'LocationCode']).agg({'arrival_delta':'mean'}).rename({'arrival_delta':'mean'}, axis=1).reset_index()
# journey_breakdown = temporal_variance.groupby('LocationCode')

# fig, ax = plt.subplots()
# for j in journey_breakdown:
#     j[1].sort_values(by='calendar_day', inplace=True)
    
#     x = j[1]['calendar_day'].apply(lambda x: pd.to_datetime(x))
#     x  = matplotlib.dates.date2num(x)
    
#     ax.plot_date(x, j[1]['mean'].values, label=j[0], marker='None', linestyle='-', alpha=0.15, c='red')
# ax.set_xlabel('Day index')
# ax.set_ylabel('Mean arrival delta / seconds')
# ax.set_xticks(desired_dates)
# ax.set_xticklabels(desired_dates)
# plt.xticks(rotation=90)
# plt.tight_layout()
    
    