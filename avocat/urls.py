from . import views 
from django.urls import path
from .views import *
urlpatterns = [
    path('',views.home,name="home"),
    path('profile/<str:pk>/',views.profile,name="profile"),
    path('createProfile/',views.createAvocatProfile,name="createAvovatProfile"),
    path('updateProfile/<str:pk>/',views.updateAvocatProfile,name="updateAvocatProfile"),
    path('createPost/<str:pk>/',views.post_create,name="post_create"),
    path('add_comment/<int:avocat_id>/', views.add_comment, name='add_comment'),
    path('evaluate/<str:pk>/', views.evaluate, name='evaluate'),
    path('rendez_vous/<int:avocat_id>/', views.prendreRendezVous, name='prendreRendezVous'),
    path('List_Rendez_Vous/<int:avocat_id>/', views.listRendezVous, name='ListRendezVous'),
    path('delete/<str:pk>/',views.delete,name="delete"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('signup/',views.signup,name="signup"),
    
    
    path('api/home/',views.home_api , name='home-api'),
    path('api/login/', LoginAPI.as_view(), name='login_api'),
    path('api/signup/', signup_api, name='signup_api'),
    path('api/profile/<int:pk>/', profile_api, name='profile_api'),
    path('api/avocats/', AvocatListAPIView.as_view(), name='avocat-list'),
    path('api/avocats/<str:pk>',views.avocatDetails , name='avocatDetails'),
    path('api/add_rendezvous/<int:avocat_id>/', add_Rendez_Vous_api, name='add_Rendez_Vous_api'),
    path('api/add_Langue/',views.addLangues , name='addLangue'),

    path('langues/<str:pk>',views.langues , name='Langues'),
    
    
]


