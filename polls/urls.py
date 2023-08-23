from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "polls"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    path('add_question/', views.add_question, name='add_question'),
    path('search/', views.custom_sql_query, name='search'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login, name='login'),
    #path('logout/', views.logout, name='logout'),
    #path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]