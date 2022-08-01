import datetime
import json
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from  django.contrib import messages
from psycopg2 import DatabaseError
import requests
from .models import location, user_daily_forecast


from WeatherCurLocation.forms import CityForm 
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required
from django.conf import settings


# Create your views here.


@unauthenticated_user
def registerUser(request):
    
    creation_form = UserCreationForm()
    if request.method == 'POST':
        creation_form = UserCreationForm(request.POST)
        if creation_form.is_valid():
            creation_form.save()
            messages.success(request, 'Registration Successful')
            return redirect('loginUser')  
        else:
            messages.error(request, 'Data Entered is invalid')     
    else:
        creation_form = UserCreationForm()

    context = {'creation_form':creation_form}
    return render(request, 'register.html', context)

@unauthenticated_user
def loginUser(request):
      
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')                
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'User is not registered')
    context = {}
    return render(request, 'login.html', context)

@login_required(login_url="loginUser")
def autocomplete(request):
    api_key = settings.API_KEY
    print("In autocomplete")
    print (api_key)
    locations = location.objects.all()

    if 'term' in request.GET:
        print (request.GET['term'])
        #locations = location.objects.get(city__contains=request.GET['term'])
        titles = []
        if locations:
            for p in locations:
                s_loc ={}
                s_loc['key'] = p.location_key
                s_loc['value'] = p.city
                titles.append(s_loc)
        #titles = [{'key':202396,'value':'Delhi'}, {'key':204108,'value':'Bengaluru'}]
        
        return JsonResponse(titles, safe=False)
    return render(request, 'home.html')

@login_required(login_url="loginUser")
def home(request):
    api_key = settings.API_KEY
    locationKey=0
    print (api_key)
    url = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{0:g}?apikey='+api_key
    print (url)
    #form = CityForm
    #print(str(form))
    
    if request.user.is_authenticated:
        
        loc_ac_url = 'http://dataservice.accuweather.com/locations/v1/cities/autocomplete?q={}&apikey='+api_key

        if request.method == 'POST':
            form = CityForm(request.POST)
            print(str(form))
            if form.is_valid():
                print(request.POST);
                #entered_city = form.cleaned_data['location_key']
                entered_city = request.POST.get('city')
                locationKey=request.POST.get('location_key')
                #print(loc_ac_url.format(entered_city))
                #loc_r = requests.get(loc_ac_url.format(entered_city))
                
                #loc_response_status = loc_r.status_code
                #print ("Status of Response" + str(loc_response_status))
                #if loc_response_status == 200:
                #    loc_data=loc_r.json()
                #    print("Location Data")
                #    print(loc_data)
                #else:
                #        messages.error(request, 'Error access location data from Accuweather')    
                #        return redirect('home')
            else:
                messages.error(request, 'City doest not exist')    
                return redirect('home')      
        else:
            form=CityForm                  

    #locationKey = 204108;
    city_weather = []
    accu_h_data = []
    forecast = user_daily_forecast()
    loc = location()
    city = ''
    r_data = {}
    if locationKey :
        if settings.USE_ACCU:
            r = requests.get(url.format(int(locationKey)))
            # Check if there is a response from the API service and only then proceed.
            response_status = r.status_code
            if response_status == 200:
                 r_data = r.json()
        else:
            r_hardcoded={"Headline": {"EffectiveDate": "2022-08-01T13:00:00+05:30","EffectiveEpochDate": 1659339000,
                        "Severity": 3,"Text": "Thunderstorms in the area Monday afternoon through Tuesday evening",
                        "Category": "thunderstorm", "EndDate": "2022-08-03T01:00:00+05:30",
                        "EndEpochDate": 1659468600  },  "DailyForecasts": [  { "Date": "2022-08-01T07:00:00+05:30","EpochDate": 1659317400,      "Temperature": {  "Minimum": { "Value": 72, "Unit": "F",
                        "UnitType": 18        }, "Maximum": { "Value": 80, "Unit": "F", "UnitType": 18 } },"Day": { "Icon": 15,        "IconPhrase": "Thunderstorms", 
                        "PrecipitationType": "Rain",        "PrecipitationIntensity": "Heavy"      },
                        "Night": {        "Icon": 15,        "IconPhrase": "Thunderstorms",        
                        "PrecipitationType": "Rain",        "PrecipitationIntensity": "Heavy"      },
                        "Sources": [        "AccuWeather"      ]                    }
                    ]}
            r_data = r        

        #r = json.dumps(r_dict)
        response_status = 200
        print ("Status of Response" + str(response_status))
        if response_status == 200:
            #r_data =  r #r.json()
            print("Received response")
            print(r_data)
            # Check if the location data exists
            if r_data:
                accu_h_data = r_data['Headline']
                print ('Headline Data')
                accu_h_data['id'] = locationKey
                print (accu_h_data)
                
                print(accu_h_data['Text'])
                
                accu_forecast_data = r_data['DailyForecasts'][0]
                print("Daily Forecast Data")
                print(accu_forecast_data)
                print(accu_forecast_data['Day']['HasPrecipitation'])
                
                
                #forecast_data.append(city_weather)
                
                loc= location.objects.get(location_key = locationKey)
                forecast.location_id = loc
                forecast.min_temp = accu_forecast_data['Temperature']['Minimum']['Value']
                forecast.max_temp = accu_forecast_data['Temperature']['Maximum']['Value']
                forecast.day_icon = accu_forecast_data['Day']['IconPhrase']
                if accu_forecast_data['Day']['HasPrecipitation'] :
                    forecast.day_precipitation_intensity = accu_forecast_data['Day']['PrecipitationIntensity']
                    forecast.day_precipitation_type = accu_forecast_data['Day']['PrecipitationType']
                else:
                    forecast.day_precipitation_intensity="None"
                    forecast.day_precipitation_type= "None"
                forecast.night_icon = accu_forecast_data['Night']['IconPhrase']
                if accu_forecast_data['Night']['HasPrecipitation'] :
                    forecast.night_precipitation_intensity = accu_forecast_data['Night']['PrecipitationIntensity']
                    forecast.night_precipitation_type = accu_forecast_data['Night']['PrecipitationType']
                else:
                    forecast.night_precipitation_intensity="None"
                    forecast.night_precipitation_type= "None"     
                
                forecast.headline_text = accu_h_data['Text']
                
                #forecast.forecast_date = datetime.datetime.strptime(city_weather['date'], '%Y-%m-%dT%H:%M:%S+%z').date()
                forecast.created_by = request.user
                forecast.updated_by = request.user
                forecast.isActive = 1
                try:
                    forecast.save()
                except DatabaseError:
                    messages.error(request,"Unable to save forecast- DatabaseError")

                

            else:
                messages.info(request, 'No data for the location')
        else:
            messages.error(request, 'Accuweather Status '+str(response_status))    
            return redirect('home')
    
    context = {
        'city': loc, 
        'forecast_data' : forecast,
        'form': form,
    }
    print("after save")
    print (accu_h_data)
    return render(request, 'index.html', context)

@login_required(login_url="loginUser")
def logoutUser(request):
    logout(request)
    return redirect('loginUser')

@login_required(login_url="loginUser")
def delete(request, pk):
    
    
    messages.success(request, 'Removed City')
    return redirect('home')