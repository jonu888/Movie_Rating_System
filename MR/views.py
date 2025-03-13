from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserLoginForm, MovieForm, ReviewForm
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Movie, MovieRating
from django.contrib import messages
from django.db.models import Avg
import logging

class WelcomeView(View):
    def get(self, request):
        return render(request, 'welcome.html')
    
class RegisterView(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})
    
    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            return redirect('login')
        return render(request, 'register.html', {'form': form})
    
   
class LoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})
    
    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if request.user.is_staff:
                    return redirect('HomeAdminView', pk=request.user.id)
                else:
                    return redirect('HomeUserView', pk=request.user.id)
            else:
                messages.error(request, 'Invalid username or password')
        return render(request, 'login.html', {'form': form})








logger = logging.getLogger(__name__)

class HomeUserView(View):
    def get(self, request, pk):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to access HomeUserView")
            return redirect('LogoutView')

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            logger.error(f"User with id {pk} does not exist")
            return redirect('LogoutView')

        if request.user.id != pk or user.id != pk or user.is_staff:
            logger.warning(f"User {request.user.id} attempted to access HomeUserView for user {pk}")
            return redirect('LogoutView')

        # Calculate average rating for each movie and sort by average rating
        movie_ratings = (
            MovieRating.objects.values('movie')
            .annotate(avg_rating=Avg('rating'))
            .order_by('-avg_rating')
        )

        # Prepare top 4 movies based on average rating
        top_movies = []
        for rating in movie_ratings[:4]:  # Limit to top 4
            try:
                movie = Movie.objects.get(id=rating['movie'])
                avg_rating = rating['avg_rating'] if rating['avg_rating'] else 0
                avg_rating_int = int(round(avg_rating))  # Round to nearest integer for star display
                top_movies.append({
                    'movie': movie,
                    'avg_rating': avg_rating_int,  # Pass the integer value for star display
                    'ratings_count': MovieRating.objects.filter(movie=movie).count(),
                })
            except Movie.DoesNotExist:
                logger.warning(f"Movie with id {rating['movie']} not found")
                continue

        logger.debug(f"Top movies data: {top_movies}")

        return render(request, 'homeuser.html', {
            'user': user,
            'top_movies': top_movies,
        })
        
class HomeAdminView(View):
     def get(self, request, pk):
        user = User.objects.get(pk=pk)
        if request.user.id == pk and user.id == pk and user.is_staff == True:
            movies = Movie.objects.all()
            reviews = MovieRating.objects.all()
            movie_count=movies.count()
            review_count=reviews.count()
            user_count=User.objects.filter(is_staff=False).count()
            return render(request, 'homeadmin.html', {'user': user, 'movies': movies, 'reviews': reviews, 'movie_count': movie_count, 'review_count': review_count, 'user_count': user_count})
        else:
            return redirect('LogoutView')
        
class AddMovieView(View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        if request.user.id == pk and user.id == pk and user.is_staff == True:
            form = MovieForm()
            return render(request, 'addmovie.html', {'form': form})
        else:
            return redirect('LogoutView')
    
    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        if request.user.id == pk and user.id == pk and user.is_staff == True:
            form = MovieForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('HomeAdminView', pk=request.user.id)
        else:
            return redirect('LogoutView')
        
class Addreview(View):
    def get(self, request, user_pk, movie_pk):
        # Check if user is authenticated and matches the requested user_pk
        if not request.user.is_authenticated or request.user.id != user_pk:
            return redirect('LogoutView')
        
        # Check if user is not staff (only regular users can review)
        if request.user.is_staff:
            return redirect('LogoutView')
        
        
        try:
            movie = Movie.objects.get(id=movie_pk)
            form = ReviewForm()
            existing_review = MovieRating.objects.filter(user=request.user, movie=movie).exists()
            if existing_review:
                msg=messages.warning(request, "You have already reviewed this movie.")
                return render(request, 'addreview.html', {
                    'form': form,
                    'movie': movie,
                    'user': request.user,
                    'msg': msg
                })
                
            return render(request, 'addreview.html', {
                'form': form,
                'movie': movie,
                'user': request.user
            })
        except Movie.DoesNotExist:
            messages.error(request, "Movie not found.")
            return redirect('HomeUserView', pk=user_pk)
    
    def post(self, request, user_pk, movie_pk):
        # Check if user is authenticated and matches the requested user_pk
        if not request.user.is_authenticated or request.user.id != user_pk:
            return redirect('LogoutView')
        
        # Check if user is not staff (only regular users can review)
        if request.user.is_staff:
            return redirect('LogoutView')
        
        try:
            movie = Movie.objects.get(id=movie_pk)
            form = ReviewForm(request.POST)
            
            if form.is_valid():
                # Check if user has already reviewed this movie
                existing_review = MovieRating.objects.filter(user=request.user, movie=movie).exists()
                if existing_review:
                    return redirect('HomeUserView', pk=user_pk)
                
                # Create new review
                MovieRating.objects.create(
                    user=request.user,
                    movie=movie,
                    rating=form.cleaned_data['rating'],
                    review=form.cleaned_data['review']
                )
                
                return redirect('HomeUserView', pk=user_pk)
            else:
                return render(request, 'addreview.html', {
                    'form': form,
                    'movie': movie,
                    'user': request.user
                })
        except Movie.DoesNotExist:
            messages.error(request, "Movie not found.")
            return redirect('HomeUserView', pk=user_pk)
      
      
class ReviewListView(View):
    def get(self, request, movie_pk):
        try:
            movie = Movie.objects.get(id=movie_pk)
            reviews = MovieRating.objects.filter(movie=movie).order_by('-id')  # Most recent first
            # Calculate average rating
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            return render(request, 'review_list.html', {
                'reviews': reviews,
                'movie': movie,
                'user': request.user,
                'average_rating': avg_rating
            })
        except Movie.DoesNotExist:
            messages.error(request, "Movie not found.")
            return redirect('HomeView', pk=request.user.id)
        
        
class MyRatingsView(View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        if request.user.id == pk and user.id == pk:
            reviews = MovieRating.objects.filter(user=request.user).order_by('-id')
            return render(request, 'myratings.html', {'reviews': reviews, 'user': user})
        else:
            return redirect('LogoutView')
        
        
class Editreview(View):
    def get(self, request, pk, movie_pk):
        user = User.objects.get(id=pk)
        r=MovieRating.objects.get(user=request.user, movie=movie_pk)
        if request.user.id == pk and r.user.id == pk:
            review = MovieRating.objects.get(user=request.user, movie=movie_pk)
            form = ReviewForm(instance=review)
            return render(request, 'editreview.html', {'form': form, 'review': review, 'user': user})
        else:
            return redirect('LogoutView')
        
    def post(self, request, pk, movie_pk):
        user = User.objects.get(id=pk)
        r=MovieRating.objects.get(user=request.user, movie=movie_pk)
        if request.user.id == pk and r.user.id == pk:
            review = MovieRating.objects.get(user=request.user, movie=movie_pk)
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('myratings', pk=pk)
        else:
            return redirect('LogoutView')
        
        
class UpdateMovieView(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        if request.user.id == pk and user.id == pk and user.is_staff == True:
            movie = Movie.objects.get(id=pk)
            form = MovieForm(instance=movie)
            return render(request, 'update_movie.html', {'form': form, 'movie': movie})
        else:
            return redirect('LogoutView')
    
    def post(self, request, pk):
        user = User.objects.get(id=pk)
        if request.user.id == pk and user.id == pk and user.is_staff == True:
            movie = Movie.objects.get(id=pk)
            form = MovieForm(request.POST, instance=movie)
            if form.is_valid():
                form.save()
                return redirect('HomeAdminView', pk=request.user.id)
        else:
            return redirect('LogoutView')
        
class DeleteMovieView(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        if request.user.id == pk and user.id == pk and user.is_staff == True:
            movie = Movie.objects.get(id=pk)
            movie.delete()
            return redirect('HomeAdminView', pk=request.user.id)
        else:
            return redirect('LogoutView')
        
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
class UsersView(View):
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        if request.user.id == pk and user.id == pk:
            users = User.objects.filter(is_staff=False)
            return render(request, 'users.html', {'users': users, 'user': user})
        else:
            return redirect('LogoutView')
        




logger = logging.getLogger(__name__)

class ReportView(View):
    def get(self, request, pk):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to access ReportView")
            return redirect('LogoutView')

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            logger.error(f"User with id {pk} does not exist")
            return redirect('LogoutView')

        if request.user.id != pk or user.id != pk:
            logger.warning(f"User {request.user.id} attempted to access reports for user {pk}")
            return redirect('LogoutView')

        # Fetch all movies
        movies = Movie.objects.all()

        # Calculate average rating for each movie
        movie_ratings = (
            MovieRating.objects.values('movie')
            .annotate(avg_rating=Avg('rating'))
            .order_by('-avg_rating')
        )

        # Prepare data for the chart: movie titles and their average ratings
        chart_data = []
        for rating in movie_ratings:
            try:
                movie = Movie.objects.get(id=rating['movie'])
                chart_data.append({
                    'movie_title': movie.title,
                    'avg_rating': round(rating['avg_rating'], 2) if rating['avg_rating'] else 0,
                })
            except Movie.DoesNotExist:
                logger.warning(f"Movie with id {rating['movie']} not found")
                continue

        # Sort movies by average rating and limit to top 10
        chart_data = sorted(chart_data, key=lambda x: x['avg_rating'], reverse=True)[:10]

        logger.debug(f"Chart data prepared: {chart_data}")

        return render(request, 'report.html', {
            'user': user,
            'chart_data': chart_data,
        })
        
        


logger = logging.getLogger(__name__)

class DiscoverMoviesView(View):
    def get(self, request, pk):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            logger.warning("Unauthenticated user attempted to access DiscoverMoviesView")
            return redirect('LogoutView')

        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            logger.error(f"User with id {pk} does not exist")
            return redirect('LogoutView')

        if request.user.id != pk or user.id != pk or user.is_staff:
            logger.warning(f"User {request.user.id} attempted to access DiscoverMoviesView for user {pk}")
            return redirect('LogoutView')

        # Get all movies
        movies = Movie.objects.all()

        # Calculate average rating and ratings count for each movie
        movie_ratings = (
            MovieRating.objects.values('movie')
            .annotate(avg_rating=Avg('rating'))
            .order_by('-avg_rating')
        )

        # Prepare movie data with ratings
        movie_data = []
        for movie in movies:
            avg_rating = next(
                (item['avg_rating'] for item in movie_ratings if item['movie'] == movie.id), 0
            )
            avg_rating_int = int(round(avg_rating)) if avg_rating else 0
            movie_data.append({
                'movie': movie,
                'avg_rating': avg_rating_int,
                'ratings_count': MovieRating.objects.filter(movie=movie).count(),
            })

        # Get unique genres for filter buttons
        movie_genres = Movie.objects.values_list('genre', flat=True).distinct()

        # Get unique release years for filter dropdown
        release_years = Movie.objects.values_list('release_date__year', flat=True).distinct().order_by('-release_date__year')

        # Apply filters
        genre_filter = request.GET.get('genre', 'All')
        year_filter = request.GET.get('year', '')
        rating_filter = request.GET.get('rating', '')
        search_query = request.GET.get('search', '')

        filtered_movies = movie_data

        # Filter by genre
        if genre_filter != 'All':
            filtered_movies = [
                movie for movie in filtered_movies
                if movie['movie'].genre == genre_filter
            ]

        # Filter by release year
        if year_filter:
            filtered_movies = [
                movie for movie in filtered_movies
                if str(movie['movie'].release_date.year) == year_filter
            ]

        # Filter by average rating
        if rating_filter:
            try:
                min_rating = int(rating_filter)
                filtered_movies = [
                    movie for movie in filtered_movies
                    if movie['avg_rating'] >= min_rating
                ]
            except ValueError:
                pass  # Ignore invalid rating filter

        # Search by movie title
        if search_query:
            filtered_movies = [
                movie for movie in filtered_movies
                if search_query.lower() in movie['movie'].title.lower()
            ]

        return render(request, 'discover_movies.html', {
            'user': user,
            'movies': filtered_movies,
            'movie_genres': movie_genres,
            'release_years': release_years,
            'selected_genre': genre_filter,
            'selected_year': year_filter,
            'selected_rating': rating_filter,
            'search_query': search_query,
        })       