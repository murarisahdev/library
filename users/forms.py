from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class AddUserForm(UserCreationForm):
    class Meta:
        model = User
        exclude = ['user_permissions', ]

    def __init__(self, *args, **kwargs):
        super(AddUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True


class ChangeUserForm(UserChangeForm):
    class Meta:
        model = User
        exclude = ['user_permissions', ]

    def __init__(self, *args, **kwargs):
        super(ChangeUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        # self.fields['groups'].required = True

