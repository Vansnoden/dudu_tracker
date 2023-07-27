from django import forms 
from django.contrib.auth.models import User 
from .models import *
from django.core import validators
from django.forms import CharField
import re


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('fullname', 'phone', 'picture')


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)



class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    new_password = forms.CharField(label="New password", widget=forms.PasswordInput)

    def clean_new_password(self):
        pattern = re.compile("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")
        password = str(self.cleaned_data['new_password'])
        if pattern.match(password):
            return password
        else:
            raise forms.ValidationError("Password should contain minimum eight \
                                        characters, at least one uppercase letter, \
                                        one lowercase letter, one number and one \
                                        special character", code="password_error")

