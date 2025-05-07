from django.urls import path
from .views import SensorDataListView, EMDataListView, RawSensorDataCreateView, SensorDataBulkCreateView

urlpatterns = [
    path('data/co2', SensorDataListView.as_view(), name='sensor_data'),
    path('data/em', EMDataListView.as_view(), name='em_data'),
    path('sensor/', RawSensorDataCreateView.as_view(), name='raw_sensor_data'),
    path('sensor/bulk/', SensorDataBulkCreateView.as_view(), name='bulk_sensor_data'),
]
