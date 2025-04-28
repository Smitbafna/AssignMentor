from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("loginoauth/", views.loginoauth, name="loginoauth"),
    path("Orgselect/", views.Orgselect, name="Orgselect"),
    path('api/user/organizations/', views.getOrgsOfUser, name='get_orgs_of_user'),
    path('api/createassignment/', views.create_assignment, name='create_assignment'),
    path('assignments/<int:pk>/', views.update_assignment, name='update-assignment'),
    path('api/assignments/<str:role>/',  views.get_assignments_by_role, name='get_assignments_by_role'),
    path('api/assignments/<str:role>/',  views.get_assignments_name, name='get_assignments_name'),
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/file/', views.get_submission_for_reviewee, name='get_submissions_by_reviewee'),
    path('submit_form/', views.submit_form, name='submit_form'),
    path('api/user/profile/', views.profile_view, name='profile'),
    path('api/assignments/delete', views.delete_assignment, name='delete_assignment'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/reviewers/', views.get_reviewers, name='reviewer-list'),
    path('api/reviewees/', views.get_reviewees, name='reviewee-list'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



