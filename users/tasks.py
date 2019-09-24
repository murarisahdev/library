from django.conf import settings
from django.contrib.auth.models import User
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.models import Site

@shared_task
def user_account_confirmation_mail(user=None):
    user = get_object_or_404(User, pk=user)
    site = Site.objects.get(name='development')
    kwargs = {
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user)
    }

    activation_url = reverse("activate_user_account",
        kwargs=kwargs)
    activate_url = "{0}{1}".format(
        site.domain, activation_url)

    msg='Please click on the below link to activate your account\n'\
        +activate_url

    send_mail(
    'Account Confirmation',
    msg,
    settings.EMAIL_HOST_USER,
    [user.email],
    fail_silently=False,
    )


@shared_task
def forget_password_mail(user=None):
    user = get_object_or_404(User, pk=user)
    token, created = Token.objects.get_or_create(user=user)

    site = Site.objects.get(name='development')

    reset_url = '/passwordreset/'
    reset_link = "{0}{1}{2}".format(
        site.domain, reset_url, token.key)
    msg = 'Please click on the below link\
    to reset your account password\n'+reset_link
    
    send_mail(
        'Password Reset',
        msg,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )