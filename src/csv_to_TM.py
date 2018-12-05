import csv
import PYSHP
from PYSHP import Writer

with open('intervallen.csv', newline='') as csvfile:
    data = csv.reader(csvfile, delimiter=';', quotechar='"')

    for row in data:
       meeuw = row[0] 
       start = row[1].split('/')
       einde = row[2].split('/')
       eerste = start[2]+'-'+start[1].rjust(2, '0')+'-'+start[0].rjust(2, '0')
       print(eerste)
       laatste = einde[2]+'-'+einde[1].rjust(2, '0')+'-'+einde[0].rjust(2, '0')
       
       bestandsnaam = 'MeeuwenTM/'+ meeuw + '.gpx'             
       file = open(bestandsnaam, 'w')
       file.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx creator="MJT" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd" version="1.1" xmlns="http://www.topografix.com/GPX/1/1">
 <trk>
  <name>Meeuw</name>
  <type>9</type>
  <trkseg>
   <trkpt lat="51.0346270" lon="3.7105780">
    <ele>8.0</ele>
    <time>{}</time>
      </trkpt>
<trkpt lat="51.0346270" lon="3.7105780">
    <ele>8.0</ele>
    <time>{}</time>
      </trkpt>
   
  
  </trkseg>
 </trk>
</gpx>""".format(eerste,laatste))
       file.close()
       
       
