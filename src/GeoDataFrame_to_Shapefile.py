import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import numpy as np
import math
import matplotlib.pyplot as plt

meeuwen = pd.read_csv(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\data.geo.ict.csv', sep=',' ,header=(0), low_memory=False)

print('Data ingelezen')
#tijd van string naar timestamp zetten, verhindert omzetten naar shapefile
#meeuwen['date_time'] = pd.to_datetime(meeuwen['date_time'])
meeuwen.set_index('date_time')  #opzich niet nodig

print("Set index date_time")
punt = [Point(xy) for xy in zip(meeuwen.longitude, meeuwen.latitude)]
meeuwen = meeuwen.drop(['longitude', 'latitude'], axis=1) # om kolommen longitude en latitude weg te laten
crs = {'init': 'epsg:4326'} #crs toekennen
meeuwen = GeoDataFrame(meeuwen, crs=crs, geometry=punt)
meeuwen= meeuwen.to_crs(epsg=31370) #transformatie

print('Geometrie naar Lambert')
meeuwen['meeuwen_x'] = meeuwen.geometry.x
meeuwen['meeuwen_y'] = meeuwen.geometry.y
meeuwen = meeuwen.rename(columns={'geometry': 'meeuwen_points'}).set_geometry('meeuwen_points') # hernoemen van geometrie kolom

print('Kolom x en y toegevoegd in Lambert')
meeuwen_dict = dict(tuple(meeuwen.groupby('bird_name')))

for meeuw in meeuwen_dict:
    x = meeuwen_dict[meeuw].drop(['calc_sunlight'],axis=1)
    x.to_file('C:/Users/maart/OneDrive/Master/Projectwerk Geo-ICT/ShapefilesLambert/{}.shp'.format(meeuw), driver='ESRI Shapefile')
    print(meeuw)
