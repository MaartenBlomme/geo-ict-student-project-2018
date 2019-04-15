# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 11:07:17 2019

@author: maart
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
        punten = punten.join(merged.loc[meeuw][['geometry']], how='outer', rsuffix= rsuf)

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
        
    return buren

def GetBuurSequentiesDict(buren, meeuwen):
    koppels =  list(itertools.combinations(meeuwen,2))

    sequenties = dict()

    for koppel in koppels:
        sequenties.update({koppel:[]})
        start_sequentie = np.nan
        einde_sequentie = np.nan
        opzoek = True
    
        for tijdstip, row in buren.iterrows():
    
            if row[koppel] == True:
                if opzoek == True:
                    start_sequentie = tijdstip    
                    einde_sequentie = tijdstip
                    opzoek = False
                else:
                    einde_sequentie = tijdstip
                
            elif opzoek == False:
                sequenties[koppel].append((start_sequentie, einde_sequentie))
                start_sequentie = np.nan
                einde_sequentie = np.nan 
                opzoek = True
            
    return sequenties

def SequentieDictToDF(sequenties_dict):
    koppels = list(sequenties_dict.keys())
    
    sequenties_df = pd.DataFrame()
    for koppel in koppels:
        length = len(sequenties[koppel])
        koppel_seqdf = pd.DataFrame.from_dict(sequenties[koppel])
        koppel_seqdf.columns = ['begin','einde']
        koppel_seqdf['koppel'] = Series([str(koppel)]*length)
        
        sequenties_df = sequenties_df.append(koppel_seqdf, ignore_index=True)
    
    sequenties_df = sequenties_df[['koppel','begin','einde']]
    sequenties_df["duur"] = sequenties_df["einde"]-sequenties_df["begin"]
    
    
    return sequenties_df

dfdict, meeuwen = ReadData(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\test\DrieMeeuwen.csv')
freq = '60S'
buffer = 500
dfdict = SyncMeeuwen(dfdict, freq)
mergeddf = Merge(dfdict)
afstandendf = BerekenAfstanden(mergeddf, meeuwen)
buren = BepaalBuren(afstandendf, meeuwen, buffer)
sequenties = GetBuurSequentiesDict(buren, meeuwen)
sequenties_df = SequentieDictToDF(sequenties)
