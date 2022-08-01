from django import forms
from django.forms import  TextInput

from WeatherCurLocation.models import location
from . import views
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    

class CityForm(forms.Form):
    class Meta:
        model = location
        fields = ['city', 'location_key']
        widgets = {'city' : TextInput(attrs={'class': 'white grey-text'})}