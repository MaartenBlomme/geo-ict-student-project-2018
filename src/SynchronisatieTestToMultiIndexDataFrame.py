import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import numpy as np
import math
import matplotlib.pyplot as plt

# bij inlezen, date_time kolom als dates instellen, met datum als eerste op true (default is false)
# is noodzakelijk om bij resampling problemen te vermijden
driemeeuwen = pd.read_csv(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\test\DrieMeeuwen.csv', sep=',' ,header=(0),low_memory=False, parse_dates=['date_time'], dayfirst=True)

# overbodige kolommen weglaten
driemeeuwen = driemeeuwen.drop(['calc_sunlight','colony_longitude','colony_latitude','calc_corine_value','device_info_serial','project_leader','ring_code','colour_ring_code','species_code','scientific_name','catch_weight','sex','catch_location','tracking_started_at','tracking_ended_at','is_active','remarks','altitude','pressure','temperature','satellites_used','gps_fixtime','positiondop','h_accuracy','v_accuracy','x_speed','y_speed','z_speed','speed_accuracy','userflag','speed_3d','speed_2d','altitude_agl','calc_year','calc_month','calc_hour','calc_time_diff','calc_distance_diff','calc_speed_2d','calc_distance_to_colony','calc_outlier','calc_corine_legend','ESA.land.cover'], axis=1)

dfdict = dict(tuple(driemeeuwen.groupby('bird_name')))

meeuwen_list = list(dfdict.keys())

for meeuw in meeuwen_list:
    dfdict[meeuw] = dfdict[meeuw].set_index('date_time')
    
    dfdict[meeuw] = dfdict[meeuw].resample('600S').asfreq() #alle andere resample methodes mean, sum,.. laten niet numerieke kolommen weg
    #numerieke data interpoleren
    dfdict[meeuw][['longitude','latitude','direction']] = dfdict[meeuw][['longitude','latitude','direction']].interpolate(method='linear')
    
    #geodataframes maken
    punt= [Point(xy) for xy in zip(dfdict[meeuw].longitude, dfdict[meeuw].latitude)]
    crs = {'init': 'epsg:4326'} #crs toekennen
    dfdict[meeuw] = GeoDataFrame(dfdict[meeuw], crs=crs, geometry=punt)
    dfdict[meeuw] = dfdict[meeuw].to_crs(epsg=31370)
    
    #NaN waarden bij bird_name vervangen door de naam van de meeuw
    dfdict[meeuw]['bird_name'] = dfdict[meeuw]['bird_name'].interpolate(method='pad')
    dfdict[meeuw] = dfdict[meeuw].set_index(['bird_name'], append=True)
    
# alle data samenbrengen 
merged = dfdict[meeuwen_list[0]]
for m in meeuwen_list[1:]:
    merged = merged.append(dfdict[m])
    
merged = merged.sort_index() #gaat groeperen op eerste index (tijdstip) 

#alle data van 1 juni op de middag tonen
#print(merged.loc['2017-06-01 12:00:00'])
