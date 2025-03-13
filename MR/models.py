from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator




class Movie(models.Model):
    class MovieGenre(models.TextChoices):
        ACTION = 'Action'
        ADVENTURE = 'Adventure'
        ANIMATION = 'Animation'
        COMEDY = 'Comedy'
        DOCUMENTARY = 'Documentary'
        DRAMA = 'Drama'
        FANTASY = 'Fantasy'
        HORROR = 'Horror'
        MYSTERY = 'Mystery'
        ROMANCE = 'Romance'
        SCIENCE_FICTION = 'Science Fiction'
        THRILLER = 'Thriller'
        WAR = 'War'
        WESTERN = 'Western'
        
    class MovieLanguage(models.TextChoices):
        ENGLISH = 'English'
        HINDI = 'Hindi'
        TAMIL = 'Tamil'
        TELUGU = 'Telugu'
        KANNADA = 'Kannada'
        MARATHI = 'Marathi'
        BENGALI = 'Bengali'
        GUJARATI = 'Gujarati'
        PUNJABI = 'Punjabi'
        URDU = 'Urdu'
        MALAYALAM = 'Malayalam'
        OTHERS = 'Others'

    title = models.CharField(
        max_length=200,
        help_text="The title of the movie"
    )
    release_date = models.DateField(
        help_text="Release date of the movie")
        
    language = models.CharField(
        max_length=50,
        choices=MovieLanguage.choices,
        help_text="Primary language of the movie"
    )
    genre = models.CharField(
        max_length=50,
        choices=MovieGenre.choices,
        help_text="Primary genre of the movie"
    )
    director = models.CharField(
        max_length=200,
        help_text="Name of the movie director"
    )
    

    

    def __str__(self):
        return f"{self.title} ({self.release_date.year})"



class MovieRating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='movie_ratings'
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.FloatField(
        validators=[
            MinValueValidator(1.0),
            MaxValueValidator(5.0)
        ],
        help_text="Rating from 1.0 to 5.0 stars"
    )
    review = models.TextField(
        blank=True,
        help_text="Optional review text"
    )
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return f"{self.user.username}'s rating for {self.movie.title}: {self.rating:.1f}★"


