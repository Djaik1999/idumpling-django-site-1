from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import *


class RegisterUserForm(UserCreationForm):
    # fields we want to include and customize in our form
    first_name = forms.CharField(max_length=100,
                                 required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                               'class': 'form-control',
                                                               }))
    last_name = forms.CharField(max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name',
                                                              'class': 'form-control',
                                                              }))
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'placeholder': 'Email',
                                                           'class': 'form-control',
                                                           }))
    credit_card_number = forms.CharField(max_length=255,
                                         widget=forms.TextInput(attrs={'placeholder': 'Credit Card Number',
                                                                       'class': 'form-control',
                                                                       }))
    cvc_code = forms.CharField(max_length=255,
                               widget=forms.TextInput(attrs={'placeholder': 'CVC code',
                                                             'class': 'form-control',
                                                             }))
    address = forms.CharField(max_length=255,
                              widget=forms.TextInput(attrs={'placeholder': 'Residential address',
                                                            'class': 'form-control',
                                                            }))
    where_key = forms.CharField(max_length=255,
                                widget=forms.TextInput(attrs={'placeholder': 'Where is the house key',
                                                              'class': 'form-control',
                                                              }))
    passport_number = forms.CharField(max_length=255,
                                      widget=forms.TextInput(attrs={'placeholder': 'Passport Number',
                                                                    'class': 'form-control',
                                                                    }))
    bio = forms.CharField(max_length=255,
                          required=False,
                          widget=forms.Textarea(attrs={'placeholder': 'About you',
                                                       'class': 'form-control',
                                                       'rows': 5,
                                                       }))
    slug = forms.CharField(max_length=255,
                           required=True,
                           widget=forms.TextInput(attrs={'placeholder': 'URL',
                                                         'class': 'form-control',
                                                         }))
    password1 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))
    password2 = forms.CharField(max_length=50,
                                required=True,
                                widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password',
                                                                  'class': 'form-control',
                                                                  'data-toggle': 'password',
                                                                  'id': 'password',
                                                                  }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'credit_card_number', 'cvc_code', 'address', 'where_key',
                  'passport_number', 'bio', 'slug', 'password1', 'password2']


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'Username',
                                                             'class': 'form-control',
                                                             }))
    password = forms.CharField(max_length=50,
                               required=True,
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password',
                                                                 'class': 'form-control',
                                                                 'data-toggle': 'password',
                                                                 'id': 'password',
                                                                 'name': 'password',
                                                                 }))
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'remember_me']


class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,
                               required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    credit_card_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    cvc_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    where_key = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    passport_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    slug = forms.SlugField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['photo', 'first_name', 'last_name', 'slug',
                  'credit_card_number', 'cvc_code', 'address', 'where_key', 'passport_number', 'bio']


class DumplingAddPostForm(forms.ModelForm):
    class Meta:
        model = Dumpling
        fields = ('name', 'meat', 'size', 'tasty', 'photo', 'slug')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя Пельменя'}),
            'meat': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Мясо'}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'tasty': forms.Select(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL'}),
        }


class DumplingAddCommentForm(forms.ModelForm):
    class Meta:
        model = DumplingComment
        fields = ('comment',)
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Комментарий', 'rows': '5'}),
        }
