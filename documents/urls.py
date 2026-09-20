from django.urls import path
from . import views

app_name = 'documents'
urlpatterns = [
    path('process/<int:pk>/', views.process_source, name='process'),
]
