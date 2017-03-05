#This script is licensed under the GNU GPLv3

from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
from geopy.distance import great_circle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#### Import the .csv file
a=pd.read_csv('fg_log.csv')
z=a.as_matrix()
lons=z[:, [1]]
lats=z[:, [2]]



#### Downsize the csv data (by 15 times) to make the animation faster:
original_size=len(lons)
resized_size=int(len(lons)/15)
lons_resized=np.zeros(resized_size)
lats_resized=np.zeros(resized_size)
dummy=0             
             
for i in range(original_size-14):
    if ((i%15)==0):
        lons_resized[dummy]=lons[i]
        lats_resized[dummy]=lats[i]
        dummy=dummy+1

#### stuff like mid value of lat/lon for to set the center of the map
angle=max( abs(z[1,2]-z[-1,2]), abs(z[1,1]-z[-1,1]) ) #map angle in degrees
mid_lat=0.5*(z[1,2]+z[-1,2])
mid_lon=0.5*(z[1,1]+z[-1,1])

#calculate city population threshold:
pop_threshold=800*angle*angle*angle*angle
#pop_threshold=12116*angle*angle


#Choose projection type based on the angle: 1 is narrow, 2 is wide, 3 is world map


if angle < 10:  
    projection=1
elif angle <120:
    projection=2
else:
    projection=3    


#Automatically selects the best projection based on the map angle:          
if projection == 1: ### Best for small paths. 
    mapa = Basemap(llcrnrlon=mid_lon-2*angle,llcrnrlat=mid_lat-1.1*angle,urcrnrlon=mid_lon+2*angle,urcrnrlat=mid_lat+1.1*angle,resolution='i', projection='tmerc', lat_0 = mid_lat, lon_0 =mid_lon)
elif projection == 2: #### medium size paths
    mapa = Basemap(projection='ortho',lon_0=mid_lon,lat_0=mid_lat,resolution='i');
else: #### very long paths (Whole world!)                
    mapa = Basemap(projection='robin', resolution = 'i', area_thresh = 1000.0,lat_0=0, lon_0=0)


#Calculate total distance travelled:
distance_traveled=0
for n in range(1,original_size):
    x2 = (lats[n],lons[n])
    x1 = (lats[n-1],lons[n-1])
    distance_traveled=distance_traveled+great_circle(x2,x1).km


fig=plt.figure()
ax = fig.add_subplot(1,1,1)
fig.tight_layout()
fig.patch.set_facecolor('darkGrey')

mapa.drawcoastlines(color='green')
#mapa.drawcountries()
mapa.fillcontinents(color='lightGreen',lake_color='lightBlue')
mapa.drawmapboundary(fill_color='lightBlue')
#mapa.drawmeridians(np.arange(0, 360, 20))
#mapa.drawparallels(np.arange(-90, 90, 20))

#### Now do the animation:

x, y = mapa(lons_resized, lats_resized)
line = mapa.plot(x[:1], y[:1], linewidth=2, color='r')[0]

def init():
    line.set_data([], [])
    return line,

def animate(i):
    x, y = mapa(lons_resized, lats_resized)
    line.set_data(x[:i], y[:i])
    return line,

anim = animation.FuncAnimation(plt.gcf(), animate, init_func=init,
                               frames=resized_size+int(0.33*resized_size),interval=6000/(resized_size**1.2), blit=True)

plt.annotate('Total distance='+str(round(distance_traveled,1))+'km', xy=(0.32,-0.04), xycoords='axes fraction')


#mapa.bluemarble()

##### Plot cities:
    
if projection == 0 or projection == 1:

    #Load city data (Data obtained in www.naturalearthdata.com)
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
        if (city_lat>mid_lat-1.1*angle) and (city_lat<mid_lat+1.1*angle) and (city_lon>mid_lon-2*angle)and (city_lon<mid_lon+1.6*angle) : 
            if population< pop_threshold: 
                continue # population threshold for projection 1
            pop.append(population)
            city_names.append(city_name)
            city_lats.append(city_lat)
            city_lons.append(city_lon)

    # compute the native map projection coordinates for cities
    x_city,y_city = mapa(city_lons,city_lats)

    mapa.plot(x_city,y_city,'ko')

    # plot the names of cities.
    for name,xpt,ypt in zip(city_names,x_city,y_city):
        plt.text(xpt+2000,ypt+2000,name,color='k')

 
else:
    #Load city data for world map
    latitudes_city = [34.03, 40.3, -23.33, 19.26, -12.2, -33.27, -33.55, 30.3, 14.41, 48.51, 55.45, -1.17, 28.36, 13.45, 35.41, -33.51, 47.55]
    longitudes_city = [-118.15, -71.51, -46.38, -99.8, -77.1, -70.40, 18.25, 31.14, -17.26, 2.21, 37.37, 36.49, 77.13, 100.28, 139.41, 151.12, 106.55]
    cities=['Los Angleles','New York', 'São Paulo', 'Mexico City', 'Lima', 'Santiago','Cape Town', 'Cairo','Dakar', 'Paris', 'Moscow','Nairobi', 'Delhi', 'Bangkok', 'Tokyo', 'Sydney', 'Ulaanbaatar']
 
    # compute the native map projection coordinates for cities
    x_city,y_city = mapa(longitudes_city,latitudes_city)

    mapa.plot(x_city,y_city,'ko')

    # plot the names of cities.
    for name,xpt,ypt in zip(cities,x_city,y_city):
        plt.text(xpt+50000,ypt+50000,name,color='k')




plt.show()

#### Create the movie file:
#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=1800)
#
#anim.save('Flight_Path.mp4', writer=writer)

#### Save in gif format:
#anim.save('Flight_Path.gif', writer='imagemagick', fps=100)
