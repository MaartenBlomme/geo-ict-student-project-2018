import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point

bram = pd.read_csv(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\Meeuwen\Bram.csv', sep=',' ,header=(0))

#tijd van string naar timestamp zetten
bram['date_time'] = pd.to_datetime(bram['date_time'])

# geopandas geometrie aanmaken op basis van coördinaten
punt = [Point(xy) for xy in zip(bram.longitude, bram.latitude)]
bram = bram.drop(['longitude', 'latitude'], axis=1) # om kolommen longitude en latitude weg te laten
crs = {'init': 'epsg:4326'} #crs toekennen
bram = GeoDataFrame(bram, crs=crs, geometry=punt)
bram= bram.to_crs(epsg=31370) #transformatie
