import tempfile
from PIL import Image
from datetime import datetime, timedelta, date, time
from faker import Faker

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import RequestsClient

from management.models import (Category, Author, BookCatalog,
    Review, ReadersTracker)

fake = Faker()


class AccountTests(APITestCase):
    __doc__ = """Token authentication test case."""

    token = None

    def setUp(self):
        self.admin_username = 'admin'
        self.admin_email = 'admin@example.com'
        self.password = 'password'      
        self.username = 'test_user'
        self.email = 'test_user@test.com'

        self.admin = User.objects.create(
            username=self.admin_username, 
            email=self.admin_email,
            password=make_password(self.password),
            is_superuser=True
        )

        self.user = User.objects.create(
            username=self.username, 
            email=self.email,
            password=make_password(self.password),
        )

        url = '/api/login-user/'
        data = {'email_or_username': self.email, 'password': self.password}
        response = self.client.post(url, data, format='json')
        self.token = response.data["token"]

        url = '/api/login-user/'
        data = {'email_or_username': self.admin_email, 'password': self.password}
        response = self.client.post(url, data, format='json')
        self.admin_token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token)


    def test_user_login(self):
        __doc__ = "Testing token based authentication."
        
        url = '/api/login-user/'
        data = {'email_or_username': self.email, 'password': self.password}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.data["token"], self.token)

    def test_user_login_with_incorrect_credentials(self):
        __doc__ = "Testing token based authentication."
        
        url = '/api/login-user/'
        data = {'email_or_username': self.email, 'password': fake.password()}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)