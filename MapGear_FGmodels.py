#This script is licensed under the GNU GPLv2+

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np








###Get data from FlightGear Log file and transform it into numpy arrays #################################################################################################






#### Import the .csv file
a=pd.read_csv('positions.csv') #25, sao paulo 20, africa 220, cairo 180
z=a.as_matrix()
lons=z[0:len(z), [0]]
lats=z[0:len(z), [1]]

original_size=len(lons)




#choose angle - only used for projection 1
angle = 10

#Choose projection values (1-narrow map, 2-medium size, 3-whole world)
projection=3

#function to choose the resolution based on the map angle:
def check_resolution( angle ):
    if angle < 2.5:  
        resolution='h'
    else:
        resolution='i'
    return resolution

#Create basemap object. 
#Automatically selects the best projection based on the map angle:          
if projection == 1: ### Best for small paths. 
    mapa = Basemap(llcrnrlon=mid_lon-1.2*angle,llcrnrlat=mid_lat-1.03*angle,urcrnrlon=mid_lon+1.2*angle,urcrnrlat=mid_lat+1.03*angle,resolution=check_resolution(angle), projection='tmerc', lat_0 = mid_lat, lon_0 =mid_lon)
elif projection == 2: #### medium size paths
    mapa = Basemap(projection='ortho',lon_0=mid_lon,lat_0=mid_lat,resolution='l');
else: #### very long paths (Whole world!)                
    mapa = Basemap(projection='robin', resolution = 'i', area_thresh = 1000.0,lat_0=0, lon_0=0)







##### Format the map/figure #############################################################################################################





fig=plt.figure()
ax = fig.add_subplot(1,1,1)
fig.tight_layout()
fig.patch.set_facecolor('darkGrey')
if projection == 1:  
    mapa.shadedrelief(scale=0.5)
    mapa.fillcontinents(color='LightGreen',lake_color='lightBlue')
elif projection == 2: 
    mapa.shadedrelief(scale=0.5)
   # mapa.fillcontinents(color='Beige',lake_color='lightBlue')
    mapa.drawmeridians(np.arange(0, 360, 30),linewidth=0.5)
    mapa.drawparallels(np.arange(-90, 90, 30),linewidth=0.5)
else:            
    mapa.shadedrelief(scale=0.5)
    #mapa.bluemarble()

mapa.drawcoastlines(color='Black')
mapa.drawcountries()

mapa.drawmapboundary(fill_color='lightBlue')
#Comment/Uncomment the following line to get fancy ocean map:
#mapa.bluemarble()









#Plot the coordinates of the FlightGear Models:
x_start,y_start = mapa(lons[0:len(z)], lats[0:len(z)])
mapa.scatter(x_start,y_start,8,marker='o',color='r',edgecolors='black',zorder=10)








##### Plot cities #########################################################################################################################





#calculate city population threshold:
pop_threshold=2000000*np.sin(angle/3.19)

if projection == 0 or projection == 1: #Naturalearth.com is only used for projection 0 and 1.

    #Load city data (Free license data originaly obtained in www.naturalearthdata.com)
    shp_info = mapa.readshapefile('ne_10m_populated_places','ne_10m_populated_places')

    pop=[]
    city_names = []
    city_lats=[]
    city_lons=[]

    for item in mapa.ne_10m_populated_places_info:
        population = item['POP_MAX']
        city_name = item['NAME']
        city_lat = item['LATITUDE']
        city_lon = item['LONGITUDE']
        if (city_lat>mid_lat-1.03*angle) and (city_lat<mid_lat+1.02*angle) and (city_lon>mid_lon-1.2*angle)and (city_lon<mid_lon+1*angle) : 
            if population< pop_threshold:  
                # population threshold for projections 0 and 1. Basically this
                # means that if the city X population is lower than threshold value,
                # that city X will not be plotted.
                continue
            pop.append(population)
            city_names.append(city_name)
            city_lats.append(city_lat)
            city_lons.append(city_lon)

    # compute the native map projection coordinates for cities
    x_city,y_city = mapa(city_lons,city_lats)
    # plot the city locations
    mapa.plot(x_city,y_city,'ko')
    # plot the names of cities.
    for name,xpt,ypt in zip(city_names,x_city,y_city):
        plt.text(xpt+2000,ypt+2000,name,color='k')

else:
    #Load wikipedia city data for world map (use this only in projection 2)
    latitudes_city = [34.03, 40.3, -23.33, -12.2, -33.27, -33.55, 30.3, 14.41, 48.51, 55.45, -1.17, 28.36, 13.45, 35.41, -33.51, 47.55]
    longitudes_city = [-118.15, -71.51, -46.38, -77.1, -70.40, 18.25, 31.14, -17.26, 2.21, 37.37, 36.49, 77.13, 100.28, 139.41, 151.12, 106.55]
    cities=['Los Angleles','New York', 'São Paulo', 'Lima', 'Santiago','Cape Town', 'Cairo','Dakar', 'Paris', 'Moscow','Nairobi', 'Delhi', 'Bangkok', 'Tokyo', 'Sydney', 'Ulaanbaatar']
 
    # compute the native map projection coordinates for cities
    x_city,y_city = mapa(longitudes_city,latitudes_city)

    #Comment the following lines NOT to display the cities using projection 2:
#    mapa.plot(x_city,y_city,'ko')
#
#    # plot the names of cities.
#    for name,xpt,ypt in zip(cities,x_city,y_city):
#        plt.text(xpt+50000,ypt+50000,name,color='k')

plt.show()


