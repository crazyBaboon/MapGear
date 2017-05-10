#This script is licensed under the GNU GPLv2+

from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
from geopy.distance import great_circle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np








###Get data from FlightGear Log file and transform it into numpy arrays #################################################################################################






#### Import the .csv file
a=pd.read_csv('fg_log-sicily.csv')
z=a.as_matrix()
lons=z[:, [1]]
lats=z[:, [2]]

#### Downsize the csv data to make the animation faster:

# 'data_reduction_factor' is used to reduce the amount of data necessary to create animation (especially affects GIF anumation).
#Tweak 'data_reduction_factor' until your GIF animation speed is fine.
data_reduction_factor=30   #Decrease/Increase the 'data_reduction_factor' in order to make GIF animations slower/faster
original_size=len(lons)
resized_size=int(original_size/data_reduction_factor)
lons_resized=np.zeros(resized_size)
lats_resized=np.zeros(resized_size)
dummy=0             
             
for i in np.arange(0,original_size-data_reduction_factor+1):
    if ((i%data_reduction_factor)==0):
        lons_resized[dummy]=lons[i]
        lats_resized[dummy]=lats[i]
        dummy=dummy+1

#Calculate total distance travelled:
distance_traveled=0
for n in range(1,original_size):
    x2 = (lats[n],lons[n])
    x1 = (lats[n-1],lons[n-1])
    distance_traveled=distance_traveled+great_circle(x2,x1).km

#### Calculate stuff like mid value of lat/lon for to set the center of the map
angle=max( abs(z[1,2]-z[-1,2]), abs(z[1,1]-z[-1,1]) ) #map angle in degrees
mid_lat=0.5*(z[1,2]+z[-1,2])
mid_lon=0.5*(z[1,1]+z[-1,1])

#Choose map projection type based on the angle: 1 is narrow, 2 is wide, 3 is world map
if angle < 10:  
    projection=1
elif angle <120:
    projection=2
else:
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
    #mapa.shadedrelief(scale=0.5)
    mapa.fillcontinents(color='Beige',lake_color='lightBlue')
elif projection == 2: 
    mapa.shadedrelief(scale=0.5)
    mapa.fillcontinents(color='Beige',lake_color='lightBlue')
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








#### Now do the animation ######################################################################################





x, y = mapa(lons_resized, lats_resized)
line = mapa.plot(x[:1], y[:1], linewidth=2, color='r')[0]

#Animation function:
def animate(i):
    line.set_data(x[:i], y[:i])
    return line,

#Animation procedure. Search the web for 'Matplotlib animation examples'
anim = animation.FuncAnimation(plt.gcf(), animate, frames=resized_size+int(0.33*resized_size),interval=6000/(resized_size**1.2), blit=True)

#Display the total distance:
plt.annotate('Total distance='+str(round(distance_traveled,1))+'km', xy=(0.32,-0.04), xycoords='axes fraction')

#Draw starting point of the journey:
x_start,y_start = mapa(lons_resized[1], lats_resized[1])
mapa.scatter(x_start,y_start,70,marker='o',color='r',edgecolors='black',zorder=10)

#Draw the end point of the journey:
x_end,y_end = mapa(lons_resized[-1], lats_resized[-1])
mapa.scatter(x_end,y_end,70,marker='o',color='r',edgecolors='black',zorder=10)







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







########### Create GIF/video files ##################################################################################################






#### Create the movie file:
#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=30, metadata=dict(artist='Me'), bitrate=1800)
#anim.save('Flight_Path.mp4', writer=writer)

#### Save in gif format. Potentialy slow. Only use this if you know what you are doing.
#anim.save('Flight_Path_cairo.gif', writer='imagemagick')
