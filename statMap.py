import matplotlib.pyplot as plt
from folium import *
from folium.plugins import *
import io

import re
import requests
from urllib.parse import urlencode
import googlemaps
import geocoding

class Statmap():
    def __init__(self, addresses, radius):
        self.radius = radius
        self.addresses = {}
        self.get_incorrect_addresses = []
        self.repeated_addresses = []
        for address in addresses:
            geocoding = Statmap.getGeocoding(Statmap.clean_address(address))
            if geocoding[0] != None:
                flagRepeated = False
                for addressRepeated , (coordinates, _) in self.addresses.items():
                    if coordinates == geocoding[0]:
                        print(addressRepeated, coordinates)
                        self.repeated_addresses.append(address)
                        self.repeated_addresses.append(addressRepeated)
                        flagRepeated = True
                        #break
                if flagRepeated == False:
                    print("\t\t\t\t appended {}".format(address))
                    self.addresses[address] = geocoding

            else:
                self.get_incorrect_addresses.append(address)
        
        
        #print(addresses)   
        print(self.addresses)
        print(self.repeated_addresses)
        self.summaries = None

    def getGeocoding(address):
        return geocoding.google_geocoding(address)


    def clean_address(calle):
        calle = re.sub("(C|c) *\/", "Calle", calle)
        calle = re.sub("n *º", "", calle)
        calle = re.sub(", +de", "," , calle)
        
        print("\t\t\t", calle)
        return calle


    def perform_summary_queries(self, worker_progress = None):
        self.summaries = {}
        for idx, (address, (coordinates, _)) in enumerate(self.addresses.items()):
            if coordinates != None:  
                self.summaries[address] = (coordinates, geocoding.herramienta_radio(coordinates, self.radius) )   
            if worker_progress != None:
                worker_progress.emit((idx/len(self.addresses))*100)
            

    def getHtmlMap(self):
        if self.summaries == None:
            self.perform_summary_queries()
            
        centerCoordinates = None
        maxLenCoordinates = -1
        for address, (coordinates, _) in self.addresses.items():
            if coordinates != None and maxLenCoordinates < len(address):
                centerCoordinates = coordinates
                maxLenCoordinates = len(address)
        
        if centerCoordinates == None:
            return None
                
        m = Map(location=centerCoordinates,  zoom_start=15)

        print(self.summaries)
        for address, (coordinates, (labels, sizes)) in self.summaries.items():
            Marker(location=coordinates, popup=IFrame(html=geocoding.html_barplot_summary_amenities(address, labels, sizes), width=800, height=400).render()).add_to(m)

 

        data = io.BytesIO()
        m.save(data, close_file=False)
        
        return data.getvalue().decode()
        


    


