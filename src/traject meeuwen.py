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
    kolommen = ['bird_name','date_time','longitude','latitude','direction','behaviour','calc_time_diff']
    data = pd.read_csv(bestand, usecols = kolommen, sep=',' ,header=(0),low_memory=False, parse_dates=['date_time'], dayfirst=True)

    
    return data

def GetData(data):
    
    dfdict = dict(tuple(data.groupby('bird_name')))
    
    meeuwen = list(dfdict.keys())

    return dfdict, meeuwen

data = ReadData(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\data.geo.ict.csv')
dfdict, meeuwen = GetData(data)

def lijn(dfdict):
    
    lijnen_dfdict = dict()
    meeuwen = list(dfdict.keys())
    for meeuw in meeuwen:
        dfdict[meeuw] = dfdict[meeuw].set_index(pd.DatetimeIndex(dfdict[meeuw].date_time))
    
        geometry = [Point(xy) for xy in zip(dfdict[meeuw].longitude, dfdict[meeuw].latitude)]
        punten_df = GeoDataFrame(dfdict[meeuw], geometry=geometry)
    
        crs = {'init': 'epsg:4326'}
        grouped = punten_df.groupby([punten_df.index.year, punten_df.index.month, punten_df.index.day]).filter(lambda x: len(x) >1 )
        grouped = grouped.groupby([grouped.index.year, grouped.index.month, grouped.index.day])['geometry'].apply(lambda x: LineString(x.tolist()))
        grouped.index.rename(['jaar', 'maand', 'dag'], inplace = True)
        
        lijnen_df = GeoDataFrame(grouped, crs = crs, geometry='geometry')
        lijnen_df.reset_index(inplace=True)
        lijnen_df = lijnen_df.to_crs({'init': 'epsg:31370'})
        
        lijnen_df.to_file(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\Trajecten\trajecten_{}'.format(meeuw), 'ESRI Shapefile')
        
        lijnen_dfdict[meeuw] = lijnen_df
    
    return lijnen_dfdict

shplijn = lijn(dfdict)
