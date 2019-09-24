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

import tempfile

fake = Faker()


class AccountTests(APITestCase):
    """
    Token authentication test case.
    """
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

        self.category = Category.objects.create(
            name='category1')

        self.author = Author.objects.create(
            name='author1')

        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        
        self.book = BookCatalog.objects.create(
            name='book1',
            description='description',
            category=self.category)
        self.book.author.add(self.author)
        self.book.save()


class BookTest(AccountTests):
    __doc__ = """Book test cases."""

    def setUp(self):
        super().setUp()

    def test_get_book_list(self):
        url = reverse('bookcatalog-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_book(self):
        url = reverse('bookcatalog-detail', kwargs={'pk': self.book.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.book.id)

    def test_book_create_by_admin(self):
        url = reverse('bookcatalog-list')
        book_name = 'book1'

        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)

        with open(tmp_file.name, 'rb') as data:
            data = {
                'name':book_name,
                'category': self.category.id,
                'author': [str(self.author.id), ],
                'description':'description',
                'book_cover':data,
                }
            response = self.client.post(url, data, format='multipart')    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], book_name)

    def test_book_create_by_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('bookcatalog-list')
        data = {
            'name':'book1',
            'category': self.category.id,
            'author': [str(self.author.id)],
            'description':'description'
            }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_update(self):
        url = reverse('bookcatalog-detail', kwargs={'pk': self.book.id})
        update_book_name = 'book1-udpate'
        data = {
            'name':update_book_name,
            'description':'update description'
            }
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], update_book_name)

    def test_book_delete(self):
        url = reverse('bookcatalog-detail', kwargs={'pk': self.book.id})
        response = self.client.delete(url, format='json')
        book_exist = BookCatalog.objects.filter(pk=self.book.id).exists()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(book_exist, False)


class CategoryTest(AccountTests):
    __doc__ = """Category test cases."""

    def setUp(self):
        super().setUp()

    def test_category_get_list(self):
        url = reverse('category-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data))

    def test_category_get(self):
        url = reverse('category-detail', kwargs={'pk':self.category.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.category.id)

    def test_category_books_list(self):
        url = reverse('category-books', kwargs={'pk': self.category.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_create_by_admin(self):
        url = reverse('category-list')
        data = {'name':'category1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_category_create_by_user(self):
        url = reverse('category-list')
        data = {'name':'category1'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_update(self):
        url = reverse('category-detail', kwargs={'pk':self.category.id})
        name = 'category1-update'
        data = {'name': name}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], name)

    def test_category_delete(self):
        url = reverse('category-detail', kwargs={'pk':self.category.id})
        url = '/api/category/'+str(self.category.id)+'/'
        response = self.client.delete(url, format='json')
        category_exist = Category.objects.filter(pk=self.category.id).exists()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(category_exist, False)


class AuthorTest(AccountTests):
    __doc__ = """Author test cases."""

    def setUp(self):
        super().setUp()

    def test_author_get_list(self):
        url = reverse('author-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_get(self):
        url = reverse('author-detail', kwargs={'pk': self.author.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.author.id)

    def test_author_books_list(self):
        url = reverse('author-books', kwargs={'pk': self.author.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_create_by_admin(self):
        url = reverse('author-list')
        # url = '/api/author/'
        data = {'name':'author1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_author_create_by_user(self):
        url = reverse('author-list')
        data = {'name':'author1'}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_update(self):
        url = reverse('author-detail', kwargs={'pk': self.author.id})
        name = 'author1-update'
        data = {'name': name}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], name)

    def test_author_delete(self):
        url = reverse('author-detail', kwargs={'pk': self.author.id})
        response = self.client.delete(url, format='json')
        author_exist = Author.objects.filter(pk=self.author.id).exists()
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)        
        self.assertEqual(author_exist, False)


class ReviewTest(AccountTests):
    __doc__ = """Reader Reviews test cases."""
    
    def setUp(self):
        super().setUp()
        self.write_review = 'Its awesome book I ever read'
        self.review = Review.objects.create(
            book=self.book,
            reader=self.user,
            review=self.write_review)

    def test_review_get_list(self):
        url = reverse('review-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_get(self):
        url = reverse('review-detail', kwargs={'pk':self.review.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review'], self.write_review)

    def test_review_create(self):
        url = reverse('review-list')
        review = 'new_review'
        data = {
            'review':review,
            'book':self.book.id,
            'reader':self.user.id
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['review'], review)

    def test_review_update(self):
        url = reverse('review-detail', kwargs={'pk':self.review.id})
        write_review = 'review update'
        data = {
            'review': write_review,
            'book': self.book.id,
            'reader': self.user.id
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review'], write_review)

    def test_review_delete(self):
        url = reverse('review-detail', kwargs={'pk':self.review.id})
        response = self.client.delete(url, format='json')
        review_exist = Review.objects.filter(pk=self.review.id).exists()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(review_exist, False)


class ReadersTrackerTest(AccountTests):
    __doc__ = """Readers Tracker test cases""" 

    def setUp(self):
        super().setUp()
        self.tracker = ReadersTracker.objects.create(
            book=self.book,
            reader=self.user,
            )

    def test_tracker_get_list(self):
        url = reverse('readerstracker-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tracker_get(self):
        url = reverse('readerstracker-detail', kwargs={'pk': self.tracker.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['percent'], 0)

    def test_tracker_create(self):
        url = reverse('readerstracker-list')
        data = {
            'book':self.book.id,
            'reader':self.user.id,
            'percent':0
            }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tracker_update(self):
        url = reverse('readerstracker-detail', kwargs={'pk': self.tracker.id})
        update_percent = 10
        data = {
            'percent': update_percent
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['percent'], update_percent)

    def test_tracker_delete(self):
        url = reverse('readerstracker-detail', kwargs={'pk': self.tracker.id})
        response = self.client.delete(url, format='json')
        tracker_exist = ReadersTracker.objects.filter(pk=self.tracker.id).exists()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(tracker_exist, False)