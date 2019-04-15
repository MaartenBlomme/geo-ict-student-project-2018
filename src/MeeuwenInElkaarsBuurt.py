# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 11:07:17 2019

@author: maarten
"""
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import Point
import itertools
import numpy as np
import math
import matplotlib.pyplot as plt

def ReadData(bestand):
    
    data = pd.read_csv( bestand, sep=',' ,header=(0),low_memory=False, parse_dates=['date_time'], dayfirst=True)

    data = data.drop(['calc_sunlight','colony_longitude','colony_latitude','calc_corine_value','device_info_serial','project_leader','ring_code','colour_ring_code','species_code','scientific_name','catch_weight','sex','catch_location','tracking_started_at','tracking_ended_at','is_active','remarks','altitude','pressure','temperature','satellites_used','gps_fixtime','positiondop','h_accuracy','v_accuracy','x_speed','y_speed','z_speed','speed_accuracy','userflag','speed_3d','speed_2d','altitude_agl','calc_year','calc_month','calc_hour','calc_time_diff','calc_distance_diff','calc_speed_2d','calc_distance_to_colony','calc_outlier','calc_corine_legend','ESA.land.cover'], axis=1)
    
    # dataframes per meeuw in dictionary steken
    
    dfdict = dict(tuple(data.groupby('bird_name')))
    meeuwen = list(dfdict.keys())
    
    return dfdict, meeuwen

def SyncMeeuwen(dfdict, meeuwen, frequentie):

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

def Merge(dfdict, meeuwen):
    # alle data opnieuw samenbrengen
    # eerste meeuw uit dictionary halen en aanvullen met de andere meeuwen
    mergeddf = dfdict[meeuwen[0]]
    for m in meeuwen[1:]:
        mergeddf = mergeddf.append(dfdict[m])
    
    mergeddf = mergeddf.sort_index()

    return mergeddf

def BepaalBuren(mergeddf, meeuwen, buffer_afstand):
    import pandas as pd

    mergeddf_zi = mergeddf.reset_index(level=1)
    
    mTI = pd.DataFrame(index=meeuwen, columns=['eerste','laatste'])
    
    for meeuw in meeuwen:
        mTI.at[meeuw, 'eerste'] = mergeddf_zi.loc[meeuw].date_time.min()
        mTI.at[meeuw, 'laatste'] = mergeddf_zi.loc[meeuw].date_time.max()
        
    total_TI = [mTI['eerste'].min(), mTI['laatste'].max()]
    
    koppels = list(itertools.combinations(meeuwen,2))
    
    koppelsTI = dict()
    buren = pd.DataFrame(index= total_TI, columns=koppels)
    buren.fillna(False, inplace=True)
    buren = buren.resample('60S').pad()
    buren.index.name = 'date_time'
    
    for koppel in koppels:
        meeuw1 = koppel[0]
        meeuw2 = koppel[1]
    
        samen_begin = max(mTI.loc[meeuw1]['eerste' ], mTI.loc[meeuw2]['eerste' ])
        samen_eind  = min(mTI.loc[meeuw1]['laatste'], mTI.loc[meeuw2]['laatste'])
        koppelsTI.update({koppel:(samen_begin,samen_eind)})
    
        for tijdstip, row in buren.iterrows():
            if tijdstip >= samen_begin and tijdstip <= samen_eind:
            
                if mergeddf.loc[meeuw1, tijdstip]['geometry'].distance(mergeddf.loc[meeuw2, tijdstip]['geometry']) <= buffer_afstand:
                    row[koppel] = True

    return buren, koppels

def GetBuurSequenties(buren, koppels):
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


dfdict, meeuwen = ReadData(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\test\DrieMeeuwen.csv')
freq = '60S'
dfdict = SyncMeeuwen(dfdict, meeuwen, freq)
mergeddf = Merge(dfdict, meeuwen)
buren, koppels = BepaalBuren(mergeddf, meeuwen, buffer_afstand)
sequenties = GetBuurSequenties(buren, koppels)
