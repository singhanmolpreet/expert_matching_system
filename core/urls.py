from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_and_match, name='upload_and_match'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),  
    path('',views.SignupPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('logout/',views.LogoutPage,name='logout'),

]
