from django.urls import path
from .views import SensorDataListView

urlpatterns = [
    path('data/', SensorDataListView.as_view(), name='sensor_data'),
]
