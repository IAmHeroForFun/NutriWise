from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.onboarding, name='onboarding'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('food/<int:pk>/', views.food_detail, name='food_detail'),
    path('food/<int:pk>/alternatives/', views.food_alternatives, name='alternatives'),
    path('food/<int:pk>/cant-make/', views.mark_cant_make, name='cant_make'),
    path('food/<int:pk>/feedback/', views.food_feedback, name='food_feedback'),
    path('api/recommendations/', views.api_recommendations, name='api_recommendations'),
    path('api/reverse-geocode/', views.api_reverse_geocode, name='reverse_geocode'),
]
