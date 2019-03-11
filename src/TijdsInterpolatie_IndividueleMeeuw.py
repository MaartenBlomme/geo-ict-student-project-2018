import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import numpy as np

bram = pd.read_csv(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\Meeuwen\Bram.csv', sep=',' ,header=(0))

#tijd van string naar timestamp zetten
bram['date_time'] = pd.to_datetime(bram['date_time'])
bram.set_index('date_time')  #opzich niet nodig

bram = bram.resample('60S', on='date_time').mean()
bram = bram.interpolate(method='linear')
