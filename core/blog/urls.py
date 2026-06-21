from django.urls import path
from .views import *

app_name = 'blog'

urlpatterns = [
    path('blog_home/', PostList.as_view(), name='blog_home'),
    path('post/<int:pk>/', Post_detail.as_view(), name='post_detail'),
    path('create/', PostCreateView.as_view(), name='create_post'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('post/<int:pk>/like/', ToggleLikeView.as_view(), name='toggle_like'),
]