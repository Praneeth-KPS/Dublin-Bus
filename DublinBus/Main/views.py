from posixpath import split
from django.shortcuts import render
from django.http import HttpResponse
from Main.models import DublinBikesStatic
from bs4 import BeautifulSoup 
from datetime import datetime
import pickle
import sklearn
import numpy as np
import requests
import pyodbc
import json
import os

server = "dublinbus-team12-server.database.windows.net"
db = "dublinbus-team12-db"
user = "innovationgeeks"
password = "Laurawillsaveus445!"
port = "1433"
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=' + server + ';PORT=' + port + ';DATABASE=' + db +';UID=' + user + ';PWD=' + password)
bus_number = []
rush_hour = []
time_24hr = []
Traffic = []
primary_model_data = []

# Create your views here.
def index(request):
    #(not required) for importing json file obj = json.load(open('BusStops.json', encoding="utf8"))

    # BusData = BusStationsCoordinates() #for getting coordinates of all bus stations from text file.
    cursor = conn.cursor()
    cursor.execute("select * from Static_DublinBikes")
    data = cursor.fetchall()
    Bike_headers = ['ID','Number','Name','Address','Latitude','Longitude']
    BikeStands = []
    for result in data:
        BikeStands.append(dict(zip(Bike_headers, result)))
    # Stations = json.dumps(data,default=str)
    DynamicData = Bikes_DynamicData()
    
    tourist_data = load_tourist_attraction_data()
    return render(request, "index.html", {'BusStatic': json.dumps(BikeStands, default=str), 'BikeDynamic': DynamicData, 'tourist_data_500': json.dumps(tourist_data, default=str)})

def about(request):
    return render(request, "about.html")

def transport_details(request):
    return render(request, "transport_details.html")

def settings(request):
    return render(request, "settings.html")


def Bikes_DynamicData():
    cursor = conn.cursor()
    # cursor.execute("SELECT MAX([number]) as [Number] ,MAX([bike_stands]) as bike_stands, MAX([available_bike_stands]) as parking_slots, MAX([available_bikes]) as available_bikes, MAX([now]) AS most_recent FROM [dbo].[dublinBikesDynamic] GROUP BY [number];")
    cursor.execute("SELECT TOP 109 [number] as [Number], [bike_stands], [available_bike_stands] as parking_slots, [available_bikes], [now] AS most_recent FROM [dbo].[dublinBikesDynamic] order by [now] desc;")
    row_headers = [x[0] for x in cursor.description]
    data = cursor.fetchall()    
    Dynamic_Json = []
    for result in data:
        Dynamic_Json.append(dict(zip(row_headers, result)))
    return json.dumps(Dynamic_Json,default=str)

def BusStationsCoordinates():
    file = open("stops.txt", encoding="utf8")
    # print(file)
    json_data = []
    row_headers = ['Latitude', 'Longitude']
    count = 0
    next(file)
    for line in file:
        fields = line.strip().split("\",")
        # print(fields[1])
        line_words = []
        for i in fields:
            
            if(count == 2):
                
                line_words.append(i[1:])
            if(count == 3):
                line_words.append(i[1:-3])
            count = count + 1
        json_data.append(dict(zip(row_headers, line_words)))
        count = 0  
    return json.dumps(json_data)
    
def load_tourist_attraction_data():
    obj = json.load(open('new_open_trip_map.json', encoding="utf8"))
    return obj

def Historic(request):
    if(request.method == 'GET'):
        param1 = request.GET.get('param_first')
        param1 = param1.lower()

        # if(param1 == "historic"):
        file = 'tourists_'+param1+'.json'
        # print(file)
        data = json.load(open(file, encoding="utf8"))
            
        return HttpResponse(json.dumps(data), content_type="application/json")

def dummy():
    if(1 == 1):
        a = 1
    else:
            url = 'https://api.opentripmap.com/0.1/en/places/bbox?lon_min=-6.60&lon_max=-5.938&lat_min=53.150&lat_max=53.655&kinds=&limit=1000&apikey=5ae2e3f221c38a28845f05b6bf7b88eab4fbbccc47f4090a37ad921a' 
            source = requests.get(url)
            data = json.loads(source.text)
            features = data.get("features")
            for feature in features: 
                wikidatacode = feature.get("properties").get("wikidata")
                try:
                    wikidata_url = 'https://www.wikidata.org/wiki/' + wikidatacode
                except:
                    wikidata_url = "null"
                if(wikidata_url == "null"):
                    feature["Photo"] = "null"
                    feature["Website"] = "null"
                else:
                    r = requests.get(wikidata_url).text
                    soup = BeautifulSoup(r, 'lxml')
                    try:
                        thumb = soup.find("div", {"class": "thumb"})
                        src = thumb.find("img")
                        photo = ('http:' + src['src'])
                        
                    except: 
                        photo = "null"
                    if photo != "null":
                        feature["Photo"] = photo
                    else:
                        feature["Photo"] = "null"
                    try:
                        wikibase = soup.find("a", {"class": "external free"})
                        website = wikibase['href']
                    except:
                        website = "null"
                    if website != "null":
                        feature["Website"] = website
                    else:
                        feature["Website"] = "null"

def Model(request):

    no_model=['7N', '17', '18', '25N', '29N', '31N', '33N', '42N', '46N', '49N', '53A', '66E', '66N', '67N',
     '69N', '70N', '77N', '84N', '88N', '90', '155', '747', '757', '904', '860']
    if(request.method == 'GET'):
        Parameters = request.GET.get('Details')
        Json_data = json.loads(Parameters)
        # print("PRIMARY MODEL JSON DATA: ", Json_data)
        PlanTime_Json = json.load(open('totalTimeSecondsRoutes.json', encoding="utf8"))
        Stop_times = json.load(open('stops_times.json', encoding="utf8"))
        dt = datetime.now().date()
        months_binary = [0,0,0,0,0,0,0,0,0,0,0,0]
        Month = {'Jan' : 1, 'Feb': 2, 'Mar':3, 'Apr':4, 'May':5, 'Jun' :6, 'Jul':7, 'Aug': 8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        Int_month = 0
        bool_holiday = national_holidaty_check(dt)
        national_holiday = 0
        if(bool_holiday):
            national_holiday = 1

        Est_time = 0
        
        cursor = conn.cursor()
        cursor.execute("select TOP 1 * from [dbo].[weather_current] ORDER BY [now]")
        data = cursor.fetchall()
        Weather_headers = ['id', 'now','weather_id','cloudModel','rainModel','weather_main','weather_description', 'pressure', 'humidity']
        Weather = []
        for result in data:
            Weather.append(dict(zip(Weather_headers, result)))
        # print(Weather)

        for i in range(0, len(Json_data[0])-2, 1):
            # print('This is 1st loop',Json_data[0][i])
            RouteA = json.loads(Json_data[0][i])
            for key, value in RouteA.items():
                if(key == 'Month'):
                    Int_month = Month[value]
            months_binary[Int_month-1] = 1
        
            Bus = RouteA['BusNumber'].upper()

            cursor.execute("select TOP 1 * from [dbo].[GTFSWithTraffic] WHERE [bus_Number] = '" + Bus + "' ORDER BY [now] DESC")
            traffic_data = cursor.fetchall()
            # print("TEST --> SQL DATA: ", traffic_data)
            Traffic_headers = ['now', 'bus_Number', 'I_O','stop_sequence_no','stop_id','stop_lat','stop_lng', 'Arr_Delay', 'curr_speed', 'freeflow_speed', 'curr_travel_time', 'freeflow_travel_time', 'pressure', 'cloud', 'rain', 'humidity']
            TEMPCHANGE = []
            for traffic_result in traffic_data:
                TEMPCHANGE.append(dict(zip(Traffic_headers, traffic_result)))
            # print("TEMPCHANGE: ", TEMPCHANGE)

            if(Bus in no_model):
                # print(RouteA['Est_journey_time'])
                # Est_time = Est_time + RouteA['Est_journey_time']
                Est_time = Est_time + ((RouteA['Est_journey_time']) * ((RouteA['TotalBusStops'])/(Stop_times['Stops'][Bus])))
            else:
                PlanTime_Model = PlanTime_Json['timeTotalSeconds'][Bus]
                dbfile = open("Model/modelsND.pkl", 'rb')  
                Models = pickle.load(dbfile)
                dbfile.close()
                # print(Models[Bus])

                Get_Data(TEMPCHANGE, Bus, RouteA['Dept_time_24_hr'], RouteA['Rush_hr'])

                result_sec = Models[Bus]["svmModel"].predict([np.array([Weather[0]['pressure'], RouteA['Dept_time_24_hr'], PlanTime_Model, Weather[0]['cloudModel'], Weather[0]['rainModel'], Weather[0]['humidity'], Int_month, RouteA['Day_Of_Week'], 
                            RouteA['Rush_hr'], months_binary[0], months_binary[1], months_binary[2], months_binary[3], months_binary[4], months_binary[5], months_binary[6], 
                            months_binary[7], months_binary[8], months_binary[9], months_binary[10], months_binary[11], national_holiday])])
                # print(result_sec)
                result_sec = ((result_sec) * ((RouteA['TotalBusStops'])/(Stop_times['Stops'][Bus])))
                Est_time = Est_time + result_sec

        print(Est_time)
        # ["DIRECTION","pressure","hours","PLANNEDTIME_TOTAL","Clouds","Rain","humidity","month","weekday", "rush_hour",1,2,3,4,5,6,7,8,9,10,11,12,"national_holiday"]
    return HttpResponse(Est_time)

def national_holidaty_check(date):
    result = False
    day = date.day
    month = date.month
    
    #check against new years, st. steven's day, and new years day (static holidays). 
    #St. Patricks is an exception as traffic is usually heavy that day
    fixed_dates = [[1,1],[25,12],[26,12]]
        
    for d in range(len(fixed_dates)):
        if (day == fixed_dates[d][0]) and (month == fixed_dates[d][1]):
            result = True
            break
                
                
    #check against bank holidays (dynamic dates)
    #easter monday is left out currently as it is difficult to determine until the 21st of march that years
        
    #First Monday in May
    if (date.strftime("%A") == 'Monday') and (month == 5) and (day < 8):
            result = True
        
    #First Monday in June
    if (date.strftime("%A") == 'Monday') and (month == 6) and (day < 8):
            result = True
        
    #First Monday in August
    if (date.strftime("%A") == 'Monday') and (month == 8) and (day < 8):
            result = True
        
    #Last Monday in October
    if (date.strftime("%A") == 'Monday') and (month == 10) and (day > 24):
            result = True

    return False

def Traffic_Model(request):
    
    no_model=['7N', '17', '18', '25N', '29N', '31N', '33N', '42N', '46N', '49N', '53A', '66E', '66N', '67N',
     '69N', '70N', '77N', '84N', '88N', '90', '155', '747', '757', '904', '860']
    if(request.method == 'GET'):
        # secondary model traffic
        secondary_model_result = []
        
        if(bus_number in no_model):
            return HttpResponse(0)

        else:
            for i in range(0, len(primary_model_data)):
                traffic_file = open("Model/models_secondary.pkl", 'rb')  
                TrafficModels = pickle.load(traffic_file)
                traffic_file.close()
                traffic_model_result = TrafficModels[bus_number[i]].predict([np.array([primary_model_data[i][0]['rain'],primary_model_data[i][0]['humidity'],primary_model_data[i][0]['pressure'],primary_model_data[i][0]['cloud'],primary_model_data[i][0]['curr_travel_time'],primary_model_data[i][0]['freeflow_travel_time'],primary_model_data[i][0]['curr_speed'],primary_model_data[i][0]['freeflow_speed'],time_24hr[i],rush_hour[i]])])
                # print("SECONDARY MODEL RESULT: ", traffic_model_result)
                secondary_model_result.append(traffic_model_result)
            # print("NEW ARRAY SECONDARY MODEL: ", secondary_model_result)

            # ["rain","humidity","pressure","cloud","curr_travel_time","freeflow_travel_time","curr_speed","freeflow_speed","hours","rush_hour"]

    return HttpResponse(traffic_model_result)

def Get_Data(data, bus, time, hour):
    primary_model_data.append(data)
    bus_number.append(bus)
    time_24hr.append(time)
    rush_hour.append(hour)
