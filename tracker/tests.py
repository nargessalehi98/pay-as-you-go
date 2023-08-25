import datetime

from django.db.models import Sum
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from config.settings import REDIS
from tracker.authentication import JWTAuthentication
from tracker.models import User, RequestLog
from tracker.serializers import RequestLogSerializer


class RegisterViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')

    def test_register_view(self):
        data = {
            'username': 'user',
            'password': 'password'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access_token', response.data)

    def test_register_view_missing_username(self):
        data = {
            'password': 'password'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_missing_password(self):
        data = {
            'username': 'user'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_existing_username(self):
        User.objects.create_user(username='user', password='password')
        data = {
            'username': 'user',
            'password': 'password'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPIViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)

    def test_login_invalid_credentials(self):
        data = {
            'username': self.username,
            'password': 'wrong-password'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        data = {
            'password': self.password
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            'username': self.username
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileAPIViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('profile')
        self.user = User.objects.create_user(username='user', password='password')
        self.token = JWTAuthentication.encode_jwt_token(self.user)['access_token']

    def test_profile_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertNotIn('password', response.data)

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_view_request_count(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cache_key = f'request_count_{self.user.id}_{datetime.date.today()}'
        request_count = REDIS.get(cache_key)
        self.assertEqual(int(request_count), 1)


class RequestReportViewTest(APITestCase):
    def setUp(self):
        self.url = reverse('request-report')
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = JWTAuthentication.encode_jwt_token(self.user)['access_token']

    def test_request_report_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        date_string1 = '2023-08-25'
        date1 = datetime.datetime.strptime(date_string1, '%Y-%m-%d').date()
        date_string2 = '2023-08-26'
        date2 = datetime.datetime.strptime(date_string2, '%Y-%m-%d').date()
        RequestLog.objects.create(user=self.user, date=date1, count=5, cost=0.005)
        RequestLog.objects.create(user=self.user, date=date2, count=6, cost=0.006)
        since_date = '2023-01-01'
        response = self.client.get(self.url, data={'since': since_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        total_count = RequestLog.objects.filter(user=self.user, date__gt=since_date).aggregate(total_count=Sum('count')
                                                                                               )['total_count'] or 0
        total_cost = RequestLog.objects.filter(user=self.user, date__gt=since_date).aggregate(total_cost=Sum('cost'))[
                                                                                                    'total_cost'] or 0
        expected_data = {
            'total_count': float(total_count),
            'total_cost': float(total_cost)
        }
        serializer = RequestLogSerializer(data=response.data)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(dict(serializer.validated_data), expected_data)
