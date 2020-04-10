from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('verifyOrRegister/<phone>', views.verifyOrRegister),
    path('submitAnswer/', views.submitAnswer),
    path('fetchQuestion/', views.fetchQuestion),
    path('fetchTransDetails/', views.trans_num_details),
]