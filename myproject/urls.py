from django.contrib import admin
from django.urls import path
from myapp import views
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('symptom-checker/', views.symptom_checker, name='symptom_checker'),
    path('history/', views.history, name='history'),
    path('history/clear/', views.clear_history, name='clear_history'),
]