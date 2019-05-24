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

 
def ReadData(bestand):
    kolommen = ['bird_name','date_time','longitude','latitude','direction','behaviour','calc_time_diff']
    data = pd.read_csv(bestand,usecols=kolommen, sep=',' ,header=(0),low_memory=False, parse_dates=['date_time'], dayfirst=True)
    
    return data
    
def MeeuwenDict(data):
    dfdict = dict(tuple(data.groupby('bird_name')))
    meeuwen = list(dfdict.keys())
    
    return dfdict, meeuwen

def SyncMeeuwen(dictionary, syncfreq, limiet):
    """" Synchroniseer de meeuwen op een bepaalde frequentie"""
    
    dfdict = dictionary
    meeuwen = list(dfdict.keys())
    
    for meeuw in meeuwen:
        # timestamp als index zetten
        dfdict[meeuw] = dfdict[meeuw].set_index('date_time')
        
        #als frequentie instellen (gelijk aan .resamle('600S').asfreq() )
        dfdict[meeuw] = dfdict[meeuw].asfreq(syncfreq)
        
        #interpoleren van kolommen (series)
        dfdict[meeuw][['longitude','latitude']] = dfdict[meeuw][['longitude','latitude']].interpolate(method='linear', limit = limiet,  limit_area = 'inside')
        
        
        # apart aangezien volgende lijn, error geeft: "Cannot interpolate with all NaNs."
        # dfdict[meeuw][['bird_name','behaviour']] = dfdict[meeuw][['bird_name','behaviour']].interpolate(method='pad')
        dfdict[meeuw]['bird_name'] = dfdict[meeuw]['bird_name'].interpolate(method='pad', limit = limiet, limit_area = 'inside')
        dfdict[meeuw]['behaviour'] = dfdict[meeuw]['behaviour'].interpolate(method='pad', limit = limiet, limit_area = 'inside')
        
        #geometrie toevoegen en onmiddelijk transformeren, kan ook nu pas omdat deze data niet geïnterpoleerd kan worden
        punt= [Point(xy) for xy in zip(dfdict[meeuw].longitude, dfdict[meeuw].latitude)]
        crs = {'init': 'epsg:4326'} #crs toekennen
        dfdict[meeuw] = GeoDataFrame(dfdict[meeuw], crs=crs, geometry=punt)
        dfdict[meeuw] = dfdict[meeuw].to_crs({'init': 'epsg:31370'})
        
        
        dfdict[meeuw] = dfdict[meeuw].set_index(['bird_name'], append=True)
        
        #eerste index naam van de meeuw
        dfdict[meeuw] = dfdict[meeuw].swaplevel()
     
    return dfdict

def Merge(dfdicts):
    dfdict = dfdicts
    meeuwen = list(dfdict.keys())
    # alle data opnieuw samenbrengen
    # eerste meeuw uit dictionary halen en aanvullen met de andere meeuwen
    mergeddf = dfdict[meeuwen[0]]
    for m in meeuwen[1:]:
        mergeddf = mergeddf.append(dfdict[m])
    
    #mergeddf = mergeddf.sort_index(sort=True)

    return mergeddf



"""afstanden berekenen van alle meeuwen tot elkaar"""
def BerekenAfstanden(dataframe):
    mergeddf = dataframe
    mergeddf.index.get_level_values('bird_name').unique()
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
                
    afstanden.dropna(how='all', inplace=True)
    return punten, afstanden



""" buren bepalen binnen afstand"""
def BepaalBuren(afstanden, meeuwen, buffer):
    buren = pd.DataFrame(index=afstanden.index, columns= afstanden.columns)
    koppels =  list(itertools.combinations(meeuwen,2))

    for koppel in koppels:
        buren[koppel] = afstanden[koppel].apply(lambda x: True if x <= buffer else False)
        
    return buren


""" tijdsintervallen bepalen wanneer meeuwen buren zijn"""
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

""" sequenties naar dataframe zetten """
def SequentieDictToDF(sequenties_dict):
    koppels = list(sequenties_dict.keys())
    
    sequenties_df = pd.DataFrame()
    for koppel in koppels:
        length = len(sequenties_dict[koppel])
        
        if sequenties_dict[koppel]:
            koppel_seqdf = pd.DataFrame.from_dict(sequenties_dict[koppel])
            
            koppel_seqdf.columns = ['begin','einde']
            koppel_seqdf['koppel'] = Series([koppel]*length)
            
            sequenties_df = sequenties_df.append(koppel_seqdf, ignore_index=True)
    
    sequenties_df = sequenties_df[['koppel','begin','einde']]
    sequenties_df["duur"] = sequenties_df["einde"]-sequenties_df["begin"]
    
    
    return sequenties_df 



"""momenteel enkel locatie eerste meeuw begintijdstip"""
class Locaties:
    def BeginMeeuw1(row):
        return mergeddf.loc[row.koppel[0], row.begin]['geometry']
    def BeginMeeuw2(row):
        return mergeddf.loc[row.koppel[1], row.begin]['geometry']
    def EindeMeeuw1(row):
        return mergeddf.loc[row.koppel[0], row.einde]['geometry']
    def EindeMeeuw2(row):
        return mergeddf.loc[row.koppel[1], row.einde]['geometry']   
       
    def BeginEind(dataframe):
        dataframe['geometry']  = dataframe.apply(Locaties.BeginMeeuw1, axis=1)
#        dataframe['beginlocatie2']  = dataframe.apply(Locaties.BeginMeeuw2, axis=1)
#        dataframe['eindlocatie1']  = dataframe.apply(Locaties.EindeMeeuw1, axis=1)
#        dataframe['eindlocatie2']  = dataframe.apply(Locaties.EindeMeeuw2, axis=1)
        return dataframe



def FilterFrequentie(data, freq=5, kwartiel='25%'):
    """ dictionary opstellen waarvoor de frequentie van de data op een bepaald kwartiel onder een maximale waarde valt. 
    Default moet 25% van de data een temporele frequentie hebben kleiner dan 5 seconden"""
    hfreqdict = dict()
    
    tempres_kwartiel = data.groupby('bird_name').calc_time_diff.describe()[kwartiel]
    meeuwen_highfreq = list(tempres_kwartiel[tempres_kwartiel <= freq].index)
    meeuwen_highfreq
    
    
    for meeuw in meeuwen_highfreq:
        hfreqdict[meeuw] = data.loc[(data['bird_name'] == meeuw) & (data['calc_time_diff'] <= freq)]
    
    return hfreqdict


def FilterInterpolated(dfdictsynched):
    dfdict = dfdictsynched
    meeuwen = dfdict.keys()

    for meeuw in meeuwen:
        dfdict[meeuw].dropna(subset =['latitude'], inplace=True)
        
    return dfdict


def Trajecten(dfdict):
    
    lijnen_dfdict = dict()
    meeuwen = list(dfdict.keys())
    for meeuw in meeuwen:
        #dfdict[meeuw] = dfdict[meeuw].set_index(pd.DatetimeIndex(dfdict[meeuw].date_time))
    
        #geometry = [Point(xy) for xy in zip(dfdict[meeuw].longitude, dfdict[meeuw].latitude)]
        punten_df = dfdict[meeuw] #GeoDataFrame(dfdict[meeuw], geometry=geometry)
    
        crs = {'init': 'epsg:4326'}
        grouped = punten_df.groupby([punten_df.index.year, punten_df.index.month, punten_df.index.day]).filter(lambda x: len(x) >1 )
        grouped = grouped.groupby([grouped.index.year, grouped.index.month, grouped.index.day])['geometry'].apply(lambda x: LineString(x.tolist()))
        grouped.index.rename(['jaar', 'maand', 'dag'], inplace = True)
        
        lijnen_df = GeoDataFrame(grouped, crs = crs, geometry='geometry')
        lijnen_df.reset_index(inplace=True)
        lijnen_df = lijnen_df.to_crs({'init': 'epsg:31370'})
        
        lijnen_df.to_file(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\TrajectenHighres\trajecten_{}'.format(meeuw), 'ESRI Shapefile')
        
        lijnen_dfdict[meeuw] = lijnen_df
    
    return lijnen_df


def PuntenShapefile(dfdict):
    meeuwen = list(dfdict.keys())
    df = dfdict
    
    
    for meeuw in meeuwen:
        df[meeuw].reset_index(inplace=True)
        df[meeuw]['date']= str(df[meeuw])
        df[meeuw] = df[meeuw].to_crs({'init': 'epsg:31370'})
        
        print(df[meeuw].head())
        df[meeuw].to_file(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\PuntenHighres\PuntenHighRes_{}'.format(meeuw), 'ESRI Shapefile')
        
        
    return 'exported'

def ExportDataFrameCSV(dataframe):
    dataframe.to_csv(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\PuntenHighres\puntenhighres.csv')
#ExportDataFrameCSV(mergeddf)


#data = ReadData(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\test\Hoogfrequentemeeuwen.csv')
#dfdict, meeuwen = MeeuwenDict(data)

#hfreqdict = FilterFrequentie(data, 5, '25%')

#dfdictsynched = SyncMeeuwen(hfreqdict, '1S', 5) #synchroniseren op 1 seconde, maximaal 5 waarden invullen
#dfdictsynchedfilterd = FilterInterpolated(dfdictsynched)

#mergeddf = Merge(dfdictsynchedfilterd)

#export shapefile van trajecten   
#shplijn = Trajecten(dfdictsynchedfilterd)

#export shapefile van punten
#PuntenShapefile(dfdictsynchedfilterd)

#punten, afstandendf = BerekenAfstanden(mergeddf)

#buffer = 1000
#buren = BepaalBuren(afstandendf, meeuwen, buffer)


#sequenties = GetBuurSequentiesDict(buren, meeuwen)

#sequentiesdf = SequentieDictToDF(sequenties)

#sequentiesdfLoc = Locaties.BeginEind(sequentiesdf)
#sequentiesgdf = GeoDataFrame(sequentiesdfLoc, geometry=sequentiesdfLoc['geometry'], crs=31370)

def GetTrajectory(gull, t1, t2):
    trackingpoints = mergeddf.loc[(gull, t1):(gull,t2)]
    group = trackingpoints.groupby(level=0) #group by gull, even though there is only one gull, makes creating a line possible
    lijn = group['geometry'].apply(lambda x: LineString(x.tolist()))
    
    return lijn

def GetSequenceTrajectories():
    trajectories = pd.DataFrame(columns = ['gull pair', 'start', 'end','gull','geometry'])
    
    koppels = sequenties.keys()
    for koppel in koppels:
        for sequentie in sequenties[koppel]:
            t1 = sequentie[0]
            t2 = sequentie[1]
            for gull in koppel:
                print( koppel, t1, t2, gull, GetTrajectory(gull,t1,t2))
                trajectories = trajectories.append({
                'gull pair': str(koppel),
                'start': str(t1),
                'end': str(t2),
                'gull': gull,
                'geometry': GetTrajectory(gull,t1,t2).iloc[0]
                }, ignore_index=True)
     
    trajectories = GeoDataFrame(trajectories, crs={'init':'epsg:31370'},geometry='geometry')   
    trajectories.to_file(r'C:\Users\maart\OneDrive\Master\Projectwerk Geo-ICT\Trajecten\trajecten_{}'.format('buren_sequenties'), 'ESRI Shapefile')    
    
    return trajectories
