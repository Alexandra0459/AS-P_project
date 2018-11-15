from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ASP.models import ClinicManager, MedicineSupply, Order, Dispatcher, Location


TYPE_CHOICES = \
    (
        ('CM', 'Clinic Manager'),
        ('WP', 'Warehouse Personel'),
        ('DP', 'Dispatcher'),
    )

class SignupForm_1(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(label='password', widget=forms.PasswordInput())
    first_name = forms.CharField(label='first name', max_length=200)
    last_name = forms.CharField(label='last name', max_length=200)
    type = forms.ChoiceField(label='type', choices=TYPE_CHOICES, widget=forms.Select(), required=True)
    email = forms.CharField(label='email',max_length=50)
    clinic_name = forms.CharField(label='clinic managed if capable', max_length=200, required=False)
    clinic_location_name = forms.CharField(label='location name if capable', max_length=200, required=False)
    clinic_location_latitude = forms.DecimalField(label='location latitude if capable', max_digits=10, decimal_places=6, required=False)
    clinic_location_longitude = forms.DecimalField(label='location longitude if capable', max_digits=10, decimal_places=6,required=False)
    clinic_location_altitude = forms.DecimalField(label='location altitude if capable', max_digits=6, decimal_places=0, required=False)
    dispatcher_name = forms.CharField(label='dispacher name if capable', max_length=200)


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=50)
    password = forms.CharField(label='password', widget=forms.PasswordInput())