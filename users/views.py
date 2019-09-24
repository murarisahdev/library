import json
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import (SessionAuthentication,
    BasicAuthentication, TokenAuthentication)

from .serializers import UserSerializer, AuthCustomTokenSerializer
from users.tasks import (user_account_confirmation_mail,
    forget_password_mail)



# from django.conf import settings
# from django.contrib.auth.models import User
# # from celery import shared_task
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail
# from django.urls import reverse
# from django.utils.encoding import force_bytes
# from django.utils.http import urlsafe_base64_encode
# from django.contrib.sites.models import Site


class UserCreate(APIView):
    __doc__ = 'Creates the user.'

    authentication_classes = [BasicAuthentication,]
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user_account_confirmation_mail.delay(user=user.id)

            return Response(data={
                'result':True,
                'message':'Account Successfully created.'
                }, 
                status=status.HTTP_201_CREATED)

        return Response(data={
            'result':False,
            'message':'provided credentials are not correct'
            }, 
            status=status.HTTP_400_BAD_REQUEST)


class CreateSocialUser(APIView):
    __doc__ = 'Create Social user.'

    authentication_classes = [BasicAuthentication,]
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def post(self, request, format='json'):

        try:
            email = request.data['email']
        except:
            return Response(data={
                'result':False,
                'message':'email not found'}, 
                status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(
            email=email, username=email)
        token, created = Token.objects.get_or_create(
            user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username':user.username,
            'is_admin':user.is_superuser
        })

def activate_user_account(request, uid=None, token=None):
    __doc__ = """Account Activation."""
   
    try:
        uid = force_text(urlsafe_base64_decode(uid))
        user = get_object_or_404(User, pk=uid)
    except User.DoesNotExist:
        user = None
    if user and default_token_generator.check_token(user, token):
        user.is_email_verified = True
        user.is_active = True
        user.save()

        site = Site.objects.get(name='development')
        url = '{0}{1}'.format(site.domain, '/accountconfirmation/')
        return redirect(url)

    else:
        return HttpResponse("Activation link has expired,\
        Provide a resend Account activation link")


class CustomAuthToken(ObtainAuthToken):
    __doc__ = """User Login/Authenticate"""

    authentication_classes = [BasicAuthentication,]
    permissions_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = AuthCustomTokenSerializer(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'username':user.username,
            'is_admin':user.is_superuser
        })


class UserLogout(APIView):
    __doc__ = 'Uesr logout'

    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.request.user
        get_object_or_404(Token, user=user).delete()
        return Response(data={
            'message':'Successfully Logout', 'result':True})


class UpdatePassword(APIView):
    __doc__ = 'Change/update user password.'

    authentication_classes = [TokenAuthentication,]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        current_password = request.data['current_password']
        new_password = request.data['new_password']
        user = self.request.user
        checked = user.check_password(current_password)
        
        if checked:
            user.set_password(new_password)
            user.save()

            return Response(data={
                'result':True,
                'message':'Password successfully update'
                }, 
                status=status.HTTP_200_OK)

        return Response(data={
            'result':False,
            'message':'current password not correct'
            }, 
            status=status.HTTP_400_BAD_REQUEST)


class ForgetPassword(APIView):
    authentication_classes = [BasicAuthentication,]
    permissions_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data['email']
            user = get_object_or_404(User, email=email)
        except:
            user = None

        if user:
            forget_password_mail.delay(user=user.id)
            # token, created = Token.objects.get_or_create(user=user)
            # site = Site.objects.get(name='development')
            # reset_url = '/passwordreset/'
            # reset_link = "{0}{1}{2}".format(
            #     site.domain, reset_url, token.key)
            # msg = 'Please click on the below link\
            # to reset your account password\n'+reset_link
            
            # send_mail(
            #     'Password Reset',
            #     msg,
            #     settings.EMAIL_HOST_USER,
            #     [user.email],
            #     fail_silently=False,
            # )

            return Response(data={
                'result':True,
                'message':'Email Sent to associated email, please check.'
                },
                status=status.HTTP_201_CREATED)

        return Response(data={
            'result':False,
            'message':'No Account associated with this email'
            },
            status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    authentication_classes = [TokenAuthentication,]
    permissions_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            password = request.data['password']
        except:
            return Response(data={
                'result':False,
                'message':'password is required.'
                },
                status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user

        user.set_password(password)
        user.save()

        return Response(data={
            'result':True,
            'message':'Password successfully update, please login'
            },
            status=status.HTTP_200_OK)