from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("loginoauth/", views.loginoauth, name="loginoauth"),
    path("Orgselect/", views.Orgselect, name="Orgselect"),
    path('getOrgsOfUser/<str:email>/', views.getOrgsOfUser, name='getOrgsOfUser'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]