from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path('signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]