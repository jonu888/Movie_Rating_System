from django import forms
from django.contrib.auth.models import User
from .models import Movie, MovieRating

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
        
class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput())
    
class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'release_date', 'language', 'genre', 'director']
        
class MovieRatingForm(forms.ModelForm):
    class Meta:
        model = MovieRating
        fields = ['rating', 'review']
        
class ReviewForm(forms.ModelForm):
    class Meta:
        model = MovieRating
        fields = ['review','rating']
        
        
        
        
        
        
        
        
        
    

