from io import BytesIO
from urllib.parse import urlencode
import requests, matplotlib.pyplot as plt, numpy as np, base64, utils as aux
import matplotlib


finalAmenityDict = {'Sustenance': ['bar', 'biergarten', 'cafe', 'fast_food', 'food_court', 'ice_cream', 'pub', 'restaurant'], 'Education': ['college', 'driving_school', 'kindergarten', 'language_school', 'library', 'toy_library', 'music_school', 'school', 'university'], 'Transportation': ['kick-scooter_rental', 'bicycle_parking', 'bicycle_repair_station', 'bicycle_rental', 'boat_rental', 'boat_sharing', 'bus_station', 'car_rental', 'car_sharing', 'car_wash', 'vehicle_inspection', 'charging_station', 'ferry_terminal', 'fuel', 'grit_bin', 'motorcycle_parking', 'parking', 'parking_entrance', 'parking_space', 'taxi'], 'Financial': ['atm', 'bank', 'bureau_de_change'], 'Healthcare': ['baby_hatch', 'clinic', 'dentist', 'doctors', 'hospital', 'nursing_home', 'pharmacy', 'social_facility', 'veterinary'], 'Entertainment, Arts & Culture': ['arts_centre', 'brothel', 'casino', 'cinema', 'community_centre', 'conference_centre', 'events_venue', 'fountain', 'gambling', 'love_hotel', 'nightclub', 'planetarium', 'public_bookcase', 'social_centre', 'stripclub', 'studio', 'swingerclub', 'theatre'], 'Public Service': ['courthouse', 'embassy', 'fire_station', 'police', 'post_box', 'post_depot', 'post_office', 'prison', 'ranger_station', 'townhall'], 'Facilities': ['bbq', 'bench', 'dog_toilet', 'drinking_water', 'give_box', 'shelter', 'shower', 'telephone', 'toilets', 'water_point', 'watering_place'], 'Waste Management': ['sanitary_dump_station', 'recycling', 'waste_basket', 'waste_disposal', 'waste_transfer_station']}

def google_geocoding(calle, geocodingurl = "https://maps.googleapis.com/maps/api/geocode/json", key = "AIzaSyAoafYjVCpZ6jH8fP57jY7rfXjxRaBJxEo"):
    params = urlencode(
            {"address":  calle,
            "key": key})

    calle_alcala_location = requests.get(f"{geocodingurl}?{params}")
    if calle_alcala_location.json()["status"] == "ZERO_RESULTS":
        print("No results for {}".format(calle))
        print("\n\n", calle_alcala_location.json())
        return None, None
    # print(json.dumps(calle_alcala_location.json(), indent=2))
    # "bounds" means the strict edges of where the street fits, but if its not a street then its a "viewport"
    # "viewport" means the view that Google recommends, so I can safely assume that any relevant information will be inside that "viewport"
    bounds = calle_alcala_location.json()["results"][0]["geometry"].get("bounds", None)
    bounds = bounds if bounds != None else calle_alcala_location.json()["results"][0]["geometry"].get("viewport")
    bounds = [content for key, content in bounds.items()]
    
    location = [str(i) for i in calle_alcala_location.json()["results"][0]["geometry"]["location"].values()]
    
    return location, bounds




def generate_summary_queries(radius, location, currentlySelectedAmenities, chunklen = 50):
    finaldict = finalAmenityDict.copy()
    finaldict = {topic:[amenity for amenity in subamentieis if amenity in currentlySelectedAmenities] for topic, subamentieis in finaldict.items() }
    
    overpass_query = """\n(    {} );out count;    """
    
    queries = {}
    querylist = []
    counter = 0
    for key, contentlist in finaldict.items():
        queries[key] = {}
        for amenity in contentlist:
            customamenity = 'node["amenity"={}](around:{},{},{});\n'.format(f'"{amenity}"', radius, location[0], location[1])
            
            querylist.append(overpass_query.format(customamenity))
            
            queries[key][amenity] = counter
        
            counter += 1
    
    
    finalqueries = []
    chunkquant = int(len(querylist)/chunklen)+1
    end = chunklen
    start = 0
    for chunk in range(chunkquant):
        finalqueries.append("[out:json];\n" + "\n".join(querylist[start:end]))
        start = end
        end += chunklen
    
    
    return queries, finalqueries




def herramienta_radio(location, currentlySelectedAmenities, radius = 1500, overpass_urls =["https://overpass.kumi.systems/api/interpreter", "https://lz4.overpass-api.de/api/interpreter", "https://overpass.openstreetmap.ru/api/interpreter"]):
    summary = {}
    queriesidx, giantquery = generate_summary_queries(radius, location, currentlySelectedAmenities)
    
    data = []
    for query in giantquery:
        for overpass_url in overpass_urls:
            try:
                data += requests.get(overpass_url, params={'data': query}).json()["elements"]
                break
            except:
                print(f"herramienta radio falla con servidor {overpass_url} probando el siguiente")
                continue
        
    
    
    
    for amenitytype, amenityqueriesdict in queriesidx.items():
        summary[amenitytype] = {}
        for amenityname, idx in amenityqueriesdict.items():
            summary[amenitytype][amenityname] = int(data[idx]["tags"]["total"])




    labels = []
    sizes = []
    for generaltheme, contenttheme in summary.items():
        for amenity, quantity in contenttheme.items():
            if quantity != 0:
                labels.append(amenity)
                sizes.append(quantity)
    
    newlabels = []
    newsizes = []
    
    mean = np.mean(sizes) + np.std(sizes) if len(sizes) != 0 else 0
    for label, size in zip(labels, sizes):
        if size < mean:
            newlabels.append(" ".join(label.split("_")).capitalize())
            newsizes.append(size)
            

  
 
            
    return newlabels, newsizes

def html_barplot_summary_amenities(address, labels, sizes, figsize = (7.2, 3.3)):
    no_report = len(labels) == 0
    

    matplotlib.use('Agg')
    if no_report == False:
        
        fig = plt.figure(figsize=figsize)
        
        plt.xticks(rotation=90)
        plt.bar(labels, sizes, color = "#493262")
        """for i,v in enumerate(sizes):
            plt.text(i-0.30, v+(0.05*max(sizes)), str(v), color='black', va = "center")"""

        plt.tight_layout()

        

        tmpfile = BytesIO()
        fig.savefig(tmpfile, format='png')
        print("BEFORE OPENING ENCODER BASE64")

        imagencoded =  base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    else:
        print("EMPTY")
        with open(aux.resource_path("auxFiles/emptyLogo.png"), "rb") as emptyImage:
            imagencoded= base64.b64encode(emptyImage.read()).decode('utf-8')

    
    return "<h2>{}</h2>".format(address) + '<img src=\'data:image/png;base64,{}\'>'.format(imagencoded)