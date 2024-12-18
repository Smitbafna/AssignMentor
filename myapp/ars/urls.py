from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("loginoauth/", views.loginoauth, name="loginoauth"),
    path("Orgselect/", views.Orgselect, name="Orgselect"),
    path('user/<str:email>/orgs/', views.getOrgsOfUser, name='get_orgs_of_user'),
    path('api/assignments/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:pk>/', views.update_assignment, name='update-assignment'),
    path('api/submissions/', views.submit_assignment, name='submit_assignment'),
    path('api/assignments/${assignmentDetails.assignment_id}/', views.delete_assignment, name='delete_assignment'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]



