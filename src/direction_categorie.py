meeuwen = pd.read_csv(r'C:\Users\User\Documents\2e master geografie\projectwerk geo-ict\data.geo.ict.csv', sep=',' ,header=(0))
lijst = []
lijst2 = []
#richting van -180° tot 180° omzetten naar richting van 0° tot 360°, is niet noodzakelijk verplicht 
for punt in meeuwen['direction']:
    if punt <= 0:
        lijst.append(punt + 360)
    else:
        lijst.append(punt)
#kolom richting in 360° systeem
meeuwen['360_degrees'] = lijst

#categorie toewijzen aan elk meetpunt
for x in meeuwen['360_degrees']:
    if x < 22.5 or x >= 337.5:
        lijst2.append('N')
    elif 22.5 <= x < 67.5:
        lijst2.append('NE')
    elif 67.5 <= x < 112.5:
        lijst2.append('E')
    elif 112.5 <= x < 157.5:
        lijst2.append('SE')
    elif 157.5 <= x < 202.5:
        lijst2.append('S')
    elif 202.5 <= x < 247.5:
        lijst2.append('SW')
    elif 247.5 <= x < 292.5:
        lijst2.append('W')
    elif 292.5 <= x < 337.5:
        lijst2.append('NW')
    else:
        lijst2.append('Geen richting')
meeuwen['direction_code'] = lijst2
