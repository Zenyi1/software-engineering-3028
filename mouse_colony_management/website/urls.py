from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('legal/terms-of-service/', views.terms_of_service, name='terms_of_service'), # legal
    path('legal/privacy-policy/', views.privacy_policy, name='privacy_policy'), # legal
    path('', views.home, name='index'),  # Index page
    path('login/', auth_views.LoginView.as_view(), name='login'),  # Login page
    path('register/', views.register, name='register'), # Register page
    path('logout/', views.logout_user, name="logout_user"),
    path('genetic-tree/<int:mouse_id>/', views.genetic_tree, name='genetic_tree'), # Genetic Tree page
]