from django.urls import path

from . import views

urlpatterns = [
    path("boards/", views.profile_list, name="profile_list"),
    path("boards/new/", views.profile_create, name="profile_create"),
    path("boards/<int:pk>/edit/", views.profile_edit, name="profile_edit"),
    path("boards/<int:pk>/delete/", views.profile_delete, name="profile_delete"),
]
