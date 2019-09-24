"""library URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers
from rest_framework.authtoken import views

from users import views as user_views
from management import views as mgm_views


router = routers.SimpleRouter()

router.register(r'category', mgm_views.CategoryViewSet)
router.register(r'book-catalog', mgm_views.BookCatalogViewSet)
router.register(r'author', mgm_views.AuthorViewSet)
router.register(r'review', mgm_views.ReviewViewSet, basename='review')
router.register(r'track-readed-books', mgm_views.ReadersTrackerViewSet)

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    path('api/', include(router.urls)),
	path('api/login-user/', user_views.CustomAuthToken.as_view(),
        name='login_user'),
	path('api/create-user/', user_views.UserCreate.as_view(),
        name='account_create'),
    path('api/create-user-social/', user_views.CreateSocialUser.as_view(),
        name='account_create'),
    path('api/activate/<slug:uid>/<slug:token>',  user_views.activate_user_account,
        name='activate_user_account'),
    path('api/logout/', user_views.UserLogout.as_view(),
        name='logout_user'),
    path('api/forget-password/', user_views.ForgetPassword.as_view(),
        name='forget_password'),
    path('api/reset-password/', user_views.ResetPassword.as_view(),
        name='reset_password'),
    path('api/update-password/', user_views.UpdatePassword.as_view(),
        name='update_password'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)