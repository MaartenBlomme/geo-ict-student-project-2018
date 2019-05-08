# -*- coding: utf-8 -*-
"""
Created on Wed May  8 10:18:43 2019

@author: User
"""

import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString, shape
def ReadData(bestand):
    
    data = pd.read_csv( bestand, sep=',' ,header=(0),low_memory=False, parse_dates=['date_time'], dayfirst=True)

    data = data.drop(['calc_sunlight','colony_longitude','colony_latitude','calc_corine_value','device_info_serial','project_leader','ring_code','colour_ring_code','species_code','scientific_name','catch_weight','sex','catch_location','tracking_started_at','tracking_ended_at','is_active','remarks','altitude','pressure','temperature','satellites_used','gps_fixtime','positiondop','h_accuracy','v_accuracy','x_speed','y_speed','z_speed','speed_accuracy','userflag','speed_3d','speed_2d','altitude_agl','calc_year','calc_month','calc_hour','calc_time_diff','calc_distance_diff','calc_speed_2d','calc_distance_to_colony','calc_outlier','calc_corine_legend','ESA.land.cover'], axis=1)
    
    # dataframes per meeuw in dictionary steken
    
    dfdict = dict(tuple(data.groupby('bird_name')))
    meeuwen = list(dfdict.keys())
    
    return dfdict, meeuwen

def lijn(dfdict):
    
    meeuwen = list(dfdict.keys())
    for meeuw in meeuwen:
        dfdict[meeuw] = dfdict[meeuw].set_index(pd.DatetimeIndex(dfdict[meeuw].date_time))
    
        geometry = [Point(xy) for xy in zip(dfdict[meeuw].longitude, dfdict[meeuw].latitude)]
        geo_df = gpd.GeoDataFrame(dfdict[meeuw], geometry=geometry)
    
        crs = {'init': 'epsg:4326'}
        geo_df = geo_df.groupby([geo_df.index.year, geo_df.index.month, geo_df.index.day])['geometry'].apply(lambda x: LineString(x.tolist()))
        geo_df = GeoDataFrame(geo_df, crs = crs, geometry='geometry')
        geo_df = geo_df.to_crs({'init': 'epsg:31370'})
        
        geo_df.to_file('trajecten_{}'.format(meeuw), 'GPX')
    
    return geo_df

dfdict, meeuwen = ReadData(r'C:\Users\User\Documents\2e master geografie\projectwerk geo-ict\data.geo.ict.csv')

shplijn = lijn(dfdict)
