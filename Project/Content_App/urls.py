from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='Home'),
    path('QueryResults.html', views.QueryResults, name='QueryResults'),
    path('AddActorToMovie.html', views.AddActortoMovie, name='AddActorToMovie'),

    path('RecordWatching.html', views.RecordWatching, name='RecordWatching'),
]