from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

# Create your models here.

class BaseModel(models.Model):
    class Active(models.IntegerChoices):
        NO = 0, _('No')
        YES = 1, _('Yes')
    
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_created_by', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name = '%(class)s_updated_by', on_delete=models.SET_NULL,null=True, blank = True)
    isActive = models.IntegerField(choices=Active.choices)
    class Meta:
        abstract = True

class location(BaseModel):
    location_key = models.IntegerField(unique=True)
    city = models.CharField(max_length=255, verbose_name="Name of city")

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = "City"
        verbose_name_plural = 'Cities'

class user_daily_forecast(BaseModel):
    location_id = models.ForeignKey(location, related_name='%(class)s_created_by', on_delete=models.SET_NULL, null=True)
    headline_text = models.CharField(max_length=200)
    forecast_date= models.DateField(auto_now_add=True)
    min_temp = models.DecimalField(decimal_places=2, max_digits=10)
    max_temp = models.DecimalField(decimal_places=2, max_digits=10)
    day_precipitation_type=models.CharField(max_length=40, blank=True)
    day_precipitation_intensity=models.CharField(max_length=40,blank=True)
    day_icon = models.CharField(max_length=40, blank=True)
    night_precipitation_type=models.CharField(max_length=40,blank=True)
    night_precipitation_intensity=models.CharField(max_length=40,blank=True)
    night_icon = models.CharField(max_length=40,blank=True)
