"""
URL configuration for Movie_Rating_System project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from MR.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', WelcomeView.as_view(), name='welcome'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('LogoutView/', LogoutView.as_view(), name='LogoutView'),
    
    path('homeuser/<int:pk>/', HomeUserView.as_view(), name='HomeUserView'),
    path('homeadmin/<int:pk>/', HomeAdminView.as_view(), name='HomeAdminView'),
    
   
    
    path('addmovie/<int:pk>/', AddMovieView.as_view(), name='AddMovieView'),
    path('UpdateMovieView/<int:pk>/', UpdateMovieView.as_view(), name='UpdateMovieView'),
    path('DeleteMovieView/<int:pk>/', DeleteMovieView.as_view(), name='DeleteMovieView'),
    
    path('UsersView/<int:pk>/', UsersView.as_view(), name='UsersView'),
    path('ReportView/<int:pk>/', ReportView.as_view(), name='ReportView'),
    
    
    
    

    path('Addreview/<int:user_pk>/<int:movie_pk>/', Addreview.as_view(), name='Addreview'),
    path('Review_list/<int:movie_pk>/', ReviewListView.as_view(), name='Review_list'),
    path('MyRatings/<int:pk>/', MyRatingsView.as_view(), name='MyRatings'),
    path('Editreview/<int:pk>/<int:movie_pk>/', Editreview.as_view(), name='Editreview'),
    path('discover_movies/<int:pk>/', DiscoverMoviesView.as_view(), name='discover_movies'),
]
