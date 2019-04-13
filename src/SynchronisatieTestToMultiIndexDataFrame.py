import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import numpy as np
import math
import matplotlib.pyplot as plt

# bij inlezen, date_time kolom als dates instellen, met datum als eerste op true (default is false)
# is noodzakelijk om bij resampling problemen te vermijden
driemeeuwen = pd.read_csv(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\test\DrieMeeuwen.csv', sep=',' ,header=(0),low_memory=False, parse_dates=['date_time'], dayfirst=True)

driemeeuwen = driemeeuwen.drop(['calc_sunlight','colony_longitude','colony_latitude','calc_corine_value','device_info_serial','project_leader','ring_code','colour_ring_code','species_code','scientific_name','catch_weight','sex','catch_location','tracking_started_at','tracking_ended_at','is_active','remarks','altitude','pressure','temperature','satellites_used','gps_fixtime','positiondop','h_accuracy','v_accuracy','x_speed','y_speed','z_speed','speed_accuracy','userflag','speed_3d','speed_2d','altitude_agl','calc_year','calc_month','calc_hour','calc_time_diff','calc_distance_diff','calc_speed_2d','calc_distance_to_colony','calc_outlier','calc_corine_legend','ESA.land.cover'], axis=1)

dfdict = dict(tuple(driemeeuwen.groupby('bird_name')))

meeuwen_list = list(dfdict.keys())

for meeuw in meeuwen_list:
    # timestamp als index zetten
    dfdict[meeuw] = dfdict[meeuw].set_index('date_time')
    
    #als frequentie instellen (gelijk aan .resamle('600S').asfreq() )
    dfdict[meeuw] = dfdict[meeuw].asfreq('600S')
    
    #interpoleren van kolommen (series)
    dfdict[meeuw][['longitude','latitude','direction']] = dfdict[meeuw][['longitude','latitude','direction']].interpolate(method='linear')
    
    # apart aangezien volgende lijn, error geeft: "Cannot interpolate with all NaNs."
    # dfdict[meeuw][['bird_name','behaviour']] = dfdict[meeuw][['bird_name','behaviour']].interpolate(method='pad')
    dfdict[meeuw]['bird_name'] = dfdict[meeuw]['bird_name'].interpolate(method='pad')
    dfdict[meeuw]['behaviour'] = dfdict[meeuw]['behaviour'].interpolate(method='pad')
    
    #geometrie toevoegen en onmiddelijk transformeren, kan ook nu pas omdat deze data niet geïnterpoleerd kan worden
    punt= [Point(xy) for xy in zip(dfdict[meeuw].longitude, dfdict[meeuw].latitude)]
    crs = {'init': 'epsg:4326'} #crs toekennen
    dfdict[meeuw] = GeoDataFrame(dfdict[meeuw], crs=crs, geometry=punt)
    dfdict[meeuw] = dfdict[meeuw].to_crs(epsg=31370)
    
    #naam van de meeuw als kolom toevoegen
    #zou logischer lijken in het begin maar dan werkt resampling niet
    dfdict[meeuw] = dfdict[meeuw].set_index(['bird_name'], append=True)
    
    #eerste index naam van de meeuw
    dfdict[meeuw] = dfdict[meeuw].swaplevel()

# alle data opnieuw samenbrengen
# eerste meeuw uit dictionary halen en aanvullen met de andere meeuwen
merged = dfdict[meeuwen_list[0]]
for m in meeuwen_list[1:]:
    merged = merged.append(dfdict[m])

merged = merged.sort_index()
