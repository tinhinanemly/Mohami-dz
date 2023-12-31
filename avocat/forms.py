from django.forms import ModelForm
from .models import *
from django import forms

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']


class AvocatForm(ModelForm):
    class Meta:
        model = Avocat
        fields = '__all__'
