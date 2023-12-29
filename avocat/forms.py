from django.forms import ModelForm
from .models import Avocat

class AvocatForm(ModelForm):
    class Meta:
        model = Avocat
        fields = '__all__'
