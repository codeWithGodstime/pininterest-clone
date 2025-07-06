from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    # Board URLs
    path('boards/', views.BoardListView.as_view(), name='board_list'),
    path('boards/create/', views.BoardCreateView.as_view(), name='board_create'),
    path('boards/<int:pk>/', views.BoardDetailView.as_view(), name='board_detail'),
    path('boards/<int:pk>/edit/', views.BoardUpdateView.as_view(), name='board_edit'),
    path('boards/<int:pk>/delete/', views.BoardDeleteView.as_view(), name='board_delete'),

    # Pin URLs
    path('pins/', views.PinListView.as_view(), name='pin_list'),
    path('pins/create/', views.PinCreateView.as_view(), name='pin_create'),
    path('pins/<int:pk>/', views.PinDetailView.as_view(), name='pin_detail'),
    path('pins/<int:pk>/edit/', views.PinUpdateView.as_view(), name='pin_edit'),
    path('pins/<int:pk>/delete/', views.PinDeleteView.as_view(), name='pin_delete'),

    # Tag URLs
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/<int:pk>/', views.TagDetailView.as_view(), name='tag_detail'),

    # User profile
    path('users/<int:pk>/', views.UserProfileView.as_view(), name='user_profile'),

    # Search
    path('search/', views.SearchView.as_view(), name='search'),

    # AJAX endpoints
    path('pins/<int:pin_id>/toggle_like/', views.toggle_like, name='toggle_like'),
    path('pins/<int:pin_id>/save_to_board/', views.save_pin_to_board, name='save_pin_to_board'),
] 