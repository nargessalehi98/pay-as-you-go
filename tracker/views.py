from django.db.models import Sum
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .decorators import increment_request_count
from .models import RequestLog
from .serializers import LoginSerializer, ProfileSerializer, RegisterSerializer, RequestLogSerializer
import logging

logger = logging.getLogger(__name__)


class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            logger.info(AuthenticationFailed)
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.validated_data)


@method_decorator(increment_request_count, name='get')
class ProfileAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class RequestReportView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RequestLogSerializer

    def get(self, request):
        since = request.GET.get('since')
        user = request.user
        queryset = RequestLog.objects.filter(user=user, date__gt=since)
        total_count = queryset.aggregate(total_count=Sum('count'))['total_count'] or 0
        total_cost = queryset.aggregate(total_cost=Sum('cost'))['total_cost'] or 0
        response_data = {
            'total_count': total_count,
            'total_cost': total_cost
        }
        serializer = self.serializer_class(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)



