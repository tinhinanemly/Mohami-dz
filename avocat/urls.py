from . import views 
from django.urls import path

urlpatterns = [
    path('',views.home,name="home"),
     path('profile/<str:pk>/',views.profile,name="profile"),
    path('createProfile/',views.createAvocatProfile,name="createAvovatProfile"),
    path('updateProfile/<str:pk>/',views.updateAvocatProfile,name="updateAvocatProfile"),
    path('createPost/<str:pk>/',views.post_create,name="post_create"),
    path('add_comment/<int:avocat_id>/', views.add_comment, name='add_comment'),
    path('rendez_vous/<int:avocat_id>/', views.prendreRendezVous, name='prendreRendezVous'),
    path('delete/<str:pk>/',views.delete,name="delete"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),
    path('signup/',views.signup,name="signup"),
]
