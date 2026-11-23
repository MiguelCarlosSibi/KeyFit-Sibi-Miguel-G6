from django.urls import path

from . import check_views, views

urlpatterns = [
    # Keyboard profiles
    path("boards/", views.profile_list, name="profile_list"),
    path("boards/new/", views.profile_create, name="profile_create"),
    path("boards/<int:pk>/edit/", views.profile_edit, name="profile_edit"),
    path("boards/<int:pk>/delete/", views.profile_delete, name="profile_delete"),
    # Keycap set checks
    path("checks/", check_views.check_list, name="check_list"),
    path("checks/new/", check_views.check_create, name="check_create"),
    path("checks/<int:pk>/", check_views.check_detail, name="check_detail"),
    path("checks/<int:pk>/delete/", check_views.check_delete, name="check_delete"),
]
