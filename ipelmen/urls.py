from django.contrib import admin
from django.contrib.auth import views as auth_views
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
