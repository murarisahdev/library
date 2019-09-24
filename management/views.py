from django.shortcuts import render

from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import (SessionAuthentication,
    BasicAuthentication)

from .models import (Category, Author, BookCatalog,
    Review, ReadersTracker)
from .serializers import (GetBookCatalogSerializer,
    PostBookCatalogSerializer, AuthorSerializer, ReviewSerializer, 
    CategorySerializer, GetReadersTrackerSerializer,
    PostReadersTrackerSerializer)
from library.custom_permission import APIPermission
from library.pagination import CustomResultsSetPagination


class CategoryViewSet(viewsets.ModelViewSet):
    __doc__ = 'Category Views'

    permission_classes = (IsAuthenticated, APIPermission)
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    
    @action(detail=False, methods=['get'], name='Author Books', 
        url_path='books/(?P<pk>\d+)', url_name='books')
    def books(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GetBookCatalogSerializer(
            instance.books.all(), many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# from rest_framework  import generics,status
from rest_framework.parsers import FormParser,MultiPartParser

class BookCatalogViewSet(viewsets.ModelViewSet):
    __doc__ = """Book Catalog Views"""

    permission_classes = (IsAuthenticated, APIPermission)
    serializer_class = GetBookCatalogSerializer
    pagination_class = CustomResultsSetPagination
    queryset = BookCatalog.objects.all()
    parser_classes = (MultiPartParser, )
    
    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request):
        serializer = PostBookCatalogSerializer(
            data=request.data,
            context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostBookCatalogSerializer(instance, request.data,
            context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PostBookCatalogSerializer(instance, request.data,
            context={'request':request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AuthorViewSet(viewsets.ModelViewSet):
    __doc__ = """Author Views"""

    permission_classes = (IsAuthenticated, APIPermission)
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()

    @action(detail=False, methods=['get'], name='Author Books',
        url_path='books/(?P<pk>\d+)', url_name='books')
    def books(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GetBookCatalogSerializer(
            instance.books.all(), many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    __doc__ = 'Readers Review Views'
    
    permission_classes = (IsAuthenticated,)
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    # def get_queryset(self):
    #     return Review.objects.filter(reader=self.request.user)


class ReadersTrackerViewSet(viewsets.ModelViewSet):
    __doc__ = """Readers Tracker Views"""
    
    permission_classes = (IsAuthenticated,)
    serializer_class = GetReadersTrackerSerializer
    queryset = ReadersTracker.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    # def get_queryset(self):
    #     return ReadersTracker.objects.filter(reader=self.request.user)

    def create(self, request):
        serializer = PostReadersTrackerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        percent = request.data.get("percent")

        if percent > instance.percent:
            instance.percent = percent
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)