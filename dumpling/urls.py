from django.urls import path
from django.views.decorators.cache import cache_page

from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('dumplings/list', cache_page(60)(ListDumplings.as_view()), name='all_dumplings'),

    path("dumpling/<slug:dumpling_slug>", IndexDumpling.as_view(), name='dumpling-detail-view'),
    path("add-post", DumplingAddPost.as_view(), name='add_post'),

    path('registration/', RegisterUser.as_view(), name='registration'),
    path('profile/<slug:profile_slug>', profile, name='user_profile'),
    path('comment/<int:pk>/like', dumpling_comment_like, name='comment_like'),
    path("comment/<int:pk>/delete", dumpling_comment_delete, name='comment_delete'),
    path("comment/<int:pk>/ban", dumpling_comment_ban, name='comment_ban'),

    path("comment/<int:pk>/update", DumplingCommentUpdateView.as_view(), name='comment_update'),

    path("about/", about, name="about")

]
