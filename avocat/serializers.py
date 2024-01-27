from rest_framework import serializers
from .models import Avocat,Langues

class AvocatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avocat
        fields = '__all__'


class langueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Langues
        fields = '__all__' 
