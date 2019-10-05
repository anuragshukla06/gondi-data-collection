from django.urls import path
from . import views
urlpatterns = [
    path('', views.index),
    path('verifyOrRegister/<phone>', views.verifyOrRegister),
    path('submitAnswer/<phone>/<answer>/<int:addPoint>', views.submitAnswer),
    path('fetchQuestion/<phone>', views.fetchQuestion),
]