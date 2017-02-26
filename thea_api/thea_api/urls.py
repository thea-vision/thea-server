from django.conf.urls import include, url
from django.contrib import admin
from eye_analysis.views import detect

urlpatterns = [
    url(r'^eye_analysis/analyze/$', detect, name="analyze")
]
