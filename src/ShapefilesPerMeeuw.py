import csv
import PYSHP
from PYSHP import Writer

vorige = ''
n = 0
with open('data.geo.ict.csv', newline='') as csvfile:
    data = csv.reader(csvfile, delimiter=',', quotechar='"')
    kolomnamen = next(data)
    k_bird =kolomnamen.index('bird_name')                           
    k_lat = kolomnamen.index('latitude')
    k_long = kolomnamen.index('longitude')
    
    for row in data:
        meeuw = row[k_bird]
        #Eerste rij
        if vorige == '': 
            newSHP = Writer(PYSHP.POINT)
            newSHP.field('bird_name', 'C', 10)
            newSHP.record(meeuw)
            newSHP.point( float(row[k_long]),float(row[k_lat]))
            vorige = meeuw
            bestandsnaam = 'Shapefiles/'+ meeuw
            print('eerste bestand', meeuw)
        
        
        elif meeuw == vorige:
            newSHP.record(row[k_bird])
            newSHP.point(float(row[k_long]),float(row[k_lat]))
            vorige = row[k_bird]
         
        else:
            
            newSHP.save(bestandsnaam)
            meeuw = row[k_bird]
            bestandsnaam = 'Shapefiles/' + meeuw
            
            newSHP = Writer(PYSHP.POINT)
            newSHP.field('bird_name', 'C', 10)
            newSHP.record(row[k_bird])
            newSHP.point(float(row[k_long]),float(row[k_lat]) )
            vorige = meeuw 
            print(meeuw, 'nieuw bestand')
            
newSHP.save(bestandsnaam)      
