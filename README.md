# reading_buses
The Reading Buses Open Data API (https://rtl2.ods-live.co.uk/cms/) contains a large amount of data on historic and current movements of buses in the town of Reading, UK. 

This project explores various pieces of analysis using these datasets.

1) For a given service, which location served is associated with the greatest arrival time uncertainty?
Historic data on bus arrival times is available, as well as historic timetabling. Customers rely on timetables to plan their business, and therefore significant departures from expected arrival times directly impact their experience. 

# Setup
If you'd like to run the code for yourself, clone to your machine and adjust the "utils_dir" within buses_analysis.py to match the absolute path to your clone. Then, adjust the "Parameters" to select a date range, service etc. Be aware that choosing >a few days of data can be slow. It can take around an hour to pull and cleanse 8 months worth of data for one service on the network. 
