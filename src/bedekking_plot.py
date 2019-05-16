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

#importeren van shapefile met kolom 'bedekking'
dataframe = geopandas.read_file(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\PuntenHighres\PuntenHighRes_Catia\Catia_bodembedekking.shp')

code_bedekking = {
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

#in dataframe code van bekking vervangen door woorden 
dataframe.replace({'bedekking':code_bedekking}, inplace =True)


# bar plot van frequentie per bedekking
print(dataframe['bedekking'].groupby(data['bedekking']).count().plot.bar())
