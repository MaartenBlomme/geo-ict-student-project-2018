import pandas as pd
import geopandas
from geopandas import GeoDataFrame
from pandas import Series
from shapely.geometry import Point, MultiPoint, LineString, MultiLineString, Polygon
import itertools
import numpy as np
import math
import matplotlib.pyplot as plt
import time
import datetime 

import fiona

shapefile = geopandas.read_file(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\PuntenHighres\PuntenHighRes_Catia\HihgRes_Catia_bodembedekking2.shp')

di = {
	1: "Gebouwen",
  	2: "Autowegen",
  	3: "Overig Afgedekt",
	4: "Spoorwegen",
	5: "Water",
	6: "Overig Onafgedekt",
	7: "Akker",
	8: "Gras,Struiken",
	9: "Bomen",
	10: "Gras,Struiken Lbgebrperc",
	11: "Gras,Struiken WBN",
	12: "Bomen WBN",
	13: "Gras,Struiken WTZ",
	14: "Bomen WTZ"
}


x11 = shapefile['BBKKb11'].dropna()
x12 = shapefile['BBKKb12'].dropna()
merged = pd.concat([x11, x12])
merged = merged.astype(int)
merged.replace(di, inplace =True)


print(merged.groupby(merged).count().plot.bar())
