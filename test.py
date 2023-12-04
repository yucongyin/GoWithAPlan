
# importing googlemaps module
import googlemaps
from datetime import datetime
 
# Requires API key
gmaps = googlemaps.Client(key='')

origins = ['Toronto,Canada']

destinations = ['Paris,France']
# Requires cities name
now = datetime.now()
my_dist = gmaps.directions('Toronto','Montreal',mode="transit",departure_time=now)
 
# Printing the result
print(my_dist[0]['legs'][0]['vehicle'])