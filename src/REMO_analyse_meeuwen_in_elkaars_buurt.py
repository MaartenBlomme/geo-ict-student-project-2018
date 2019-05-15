# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 10:07:09 2019

@author: User
"""

import pandas as pd
from geopandas import GeoDataFrame
from pandas import Series
from shapely.geometry import Point
import itertools
import numpy as np
import math
import matplotlib.pyplot as plt
import time

def ReadData(bestand):
    
    data = pd.read_csv( bestand, sep=',' ,header=(0),low_memory=False, parse_dates=['date_time'], dayfirst=True)

    data = data.drop(['calc_sunlight','colony_longitude','colony_latitude','calc_corine_value','device_info_serial','project_leader','ring_code','colour_ring_code','species_code','scientific_name','catch_weight','sex','catch_location','tracking_started_at','tracking_ended_at','is_active','remarks','altitude','pressure','temperature','satellites_used','gps_fixtime','positiondop','h_accuracy','v_accuracy','x_speed','y_speed','z_speed','speed_accuracy','userflag','speed_3d','speed_2d','altitude_agl','calc_year','calc_month','calc_hour','calc_time_diff','calc_distance_diff','calc_speed_2d','calc_distance_to_colony','calc_outlier','calc_corine_legend','ESA.land.cover'], axis=1)
    
    # dataframes per meeuw in dictionary steken
    
    dfdict = dict(tuple(data.groupby('bird_name')))
    meeuwen = list(dfdict.keys())
    
    return dfdict, meeuwen

def SyncMeeuwen(dfdict, frequentie):
    meeuwen = list(dfdict.keys())
    for meeuw in meeuwen:
        # timestamp als index zetten
        dfdict[meeuw] = dfdict[meeuw].set_index('date_time')
        
        #als frequentie instellen (gelijk aan .resamle('600S').asfreq() )
        dfdict[meeuw] = dfdict[meeuw].asfreq(frequentie)
        
        #interpoleren van kolommen (series)
        dfdict[meeuw][['longitude','latitude']] = dfdict[meeuw][['longitude','latitude']].interpolate(method='linear')
        
        # apart aangezien volgende lijn, error geeft: "Cannot interpolate with all NaNs."
        # dfdict[meeuw][['bird_name','behaviour']] = dfdict[meeuw][['bird_name','behaviour']].interpolate(method='pad')
        dfdict[meeuw]['bird_name'] = dfdict[meeuw]['bird_name'].interpolate(method='pad')
        dfdict[meeuw]['behaviour'] = dfdict[meeuw]['behaviour'].interpolate(method='pad')
        dfdict[meeuw]['direction'] = dfdict[meeuw]['direction'].interpolate(method='pad')
        
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

    return dfdict

def Merge(dfdict):
    meeuwen = list(dfdict.keys())
    # alle data opnieuw samenbrengen
    # eerste meeuw uit dictionary halen en aanvullen met de andere meeuwen
    mergeddf = dfdict[meeuwen[0]]
    for m in meeuwen[1:]:
        mergeddf = mergeddf.append(dfdict[m])
    
    mergeddf = mergeddf.sort_index()
    
    return mergeddf
def BerekenAfstanden(mergeddf, meeuwen):
    
    punten = mergeddf.loc[meeuwen[0]][['geometry']]
    kolomnaam = 'geometry_'+meeuwen[0]
    punten.columns = [kolomnaam]

    for meeuw in meeuwen[1:]:
        rsuf = '_'+meeuw
        punten = punten.join(mergeddf.loc[meeuw][['geometry']], how='outer', rsuffix= rsuf)

    punten.columns = meeuwen #naam veranderen van kolommen
    
    koppels = list(itertools.combinations(meeuwen,2))
    
    afstanden = pd.DataFrame(index=punten.index, columns= koppels)
    

    for tijdstip, row in afstanden.iterrows():
        for koppel in koppels:
            if pd.notna(punten.loc[tijdstip, koppel[0]]) and pd.notna(punten.loc[tijdstip,koppel[1]]):
                row[koppel] = punten.loc[tijdstip, koppel[0]].distance(punten.loc[tijdstip,koppel[1]]) 
          
    return afstanden

def BepaalBuren(afstanden, meeuwen, buffer):
    buren = pd.DataFrame(index=afstanden.index, columns= afstanden.columns)
    koppels =  list(itertools.combinations(meeuwen,2))

    for koppel in koppels:
        buren[koppel] = afstanden[koppel].apply(lambda x: True if x <= buffer else False)    
    buren.reset_index(inplace = True)
    return buren

def HeatmapBuren(mergeddf, buren):
    mergeddf.reset_index(inplace = True)
    #mergeddf.rename(columns = {'date_time':'date_time1'}, inplace = True)
    buren.rename(columns = {('Bram', 'Brigitte'): 'voorwaarde1', ('Bram', 'Claude'): 'voorwaarde2', ('Brigitte', 'Claude'): 'voorwaarde3'}, inplace = True)
    test = pd.merge(mergeddf, buren, how = 'outer', on = 'date_time')
    return test
def REMO(heatmap):
    #sorteren volgens tijd
    gesorteerd = heatmap.sort_values(by=['date_time'])
    #selecteer vanaf welke rij je een heatmap wil maken. 
    #de 3 meeuwen moeten voorkomen in de geselecteerde tijdsperiode
    #enkel de kolommen bird_name, date_time en direction hebben we nodig
    #bepaalt de grote van de REMO matrix. 30 wil 3 meeuwen op 10 tijdsmomenten.
    selectie = gesorteerd[(gesorteerd['voorwaarde1'] == True) & (gesorteerd['voorwaarde2'] == True) & (gesorteerd['voorwaarde3'] == True)]
    selectie = selectie.iloc[24654:]
    couple_columns = selectie[['bird_name','date_time', 'direction']].head(30)
    #print(couple_columns)
    phase_1_2 = couple_columns.groupby(['bird_name', 'date_time']).mean()
    phase_1_2 = phase_1_2.reset_index()
    
    #heatmap plotten
    plt.figure(figsize=(9,9))
    pivot_table = phase_1_2.pivot('bird_name', 'date_time', 'direction')
    plt.xlabel('date_time', size = 15)
    plt.ylabel('bird_name', size = 15)
    plt.title('Flight direction', size = 15)
    sns.heatmap(pivot_table, vmin = -180, vmax = 180, annot=True, fmt=".1f", linewidths=.5, square = True, cmap = 'twilight')
    return pivot_table
    
dfdict, meeuwen = ReadData(r'C:\Users\User\Documents\2e master geografie\projectwerk geo-ict\DrieMeeuwen.csv')
freq = '60S'
buffer = 500
dfdict = SyncMeeuwen(dfdict, freq)
mergeddf = Merge(dfdict)
afstandendf = BerekenAfstanden(mergeddf, meeuwen)
buren = BepaalBuren(afstandendf, meeuwen, buffer)
heatmap = HeatmapBuren(mergeddf, buren)
remo = REMO(heatmap)
heatmap.to_csv('buren.csv', sep=',' ,header=(0))