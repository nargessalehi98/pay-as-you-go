from django.urls import path

from tracker.views import LoginAPIView, ProfileAPIView, RegisterAPIView, RequestReportView

urlpatterns = [
    path('api/v1/register/', RegisterAPIView.as_view(), name='register'),
    path('api/v1/login/', LoginAPIView.as_view(), name='login'),
    path('api/v1/profile/', ProfileAPIView.as_view(), name='profile'),
    path('api/v1/requests/reports/', RequestReportView.as_view(), name='request-report'),
]