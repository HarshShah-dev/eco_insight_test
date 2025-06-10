from django.urls import path
from .views import (
    AirQualityDataListView, EnergyDataListView, OccupancyDataCreateView,
    AirQualityDataHistoryView, EnergyDataHistoryView, OccupancyDataHistoryView,
    EnergyDataHistoryViewLevel3, EnergyDataHistoryViewLevel4, RadarDataCreateView,
    SensorListView, SensorDetailView
)

urlpatterns = [
    path('data/co2', AirQualityDataListView.as_view(), name='aq_data'),
    path('data/em', EnergyDataListView.as_view(), name='em_data'),
    # path('data/oc', OccupancyDataCreateView.as_view(), name='oc_data'),
    path('data/oc/parsed', OccupancyDataCreateView.as_view(), name='parsed_oc_data'),
    path('data/co2/history', AirQualityDataHistoryView.as_view()),
    path('data/em/history', EnergyDataHistoryView.as_view()),
    path('data/oc/history', OccupancyDataHistoryView.as_view()),
    path('data/em/history/level3', EnergyDataHistoryViewLevel3.as_view()),
    path('data/em/history/level4', EnergyDataHistoryViewLevel4.as_view()),
    path('data/radar', RadarDataCreateView.as_view(), name='radar_data'),
    
    # Sensor management endpoints
    path('sensors', SensorListView.as_view(), name='sensor_list'),
    path('sensors/<str:sensor_id>', SensorDetailView.as_view(), name='sensor_detail'),
]
