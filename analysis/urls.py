from django.contrib import admin
from django.urls import path
from analysis.views import (
    register, 
    login, 
    analyze, 
    get_analyses, 
    delete_analysis
)

urlpatterns = [
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('api/analyze/', analyze, name='analyze'),
    path('api/analyses/', get_analyses, name='get_analyses'),
    path('api/analyses/<int:id>/', get_analyses, name='get-analysis-by-id'),
    path('api/analyses/<int:pk>/', delete_analysis, name='delete-analysis'),
]