from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='index'),  # Index page
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Login page
    path('logout/', views.logout_user, name="logout"),
]
