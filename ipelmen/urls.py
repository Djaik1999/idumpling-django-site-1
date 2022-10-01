"""ipelmen URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.template.defaulttags import url     # импорт должен быть из from django.conf.urls import url, но его там нет
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from dumpling.views import LoginUser, logout_user, ResetUserPassword
from dumpling.forms import LoginUserForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dumpling.urls')),

    path('login/', LoginUser.as_view(redirect_authenticated_user=True,
                                     authentication_form=LoginUserForm), name='login'),
    path('logout/', logout_user, name='logout'),

    path('password-reset/', ResetUserPassword.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    re_path(r'^oauth/', include('social_django.urls', namespace='social')),

    path('_debug_/', include('debug_toolbar.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
