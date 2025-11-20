from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views

from .views import (
    SingleObservationCreateView,
    ChainListView,
    ChainCreateView,
    ChainView,
    ChainedTargetDetailView,
    ChainTemplateCreateView,
    ChainTemplateListView,
    ChainTemplateView,
    ChainedTemplateCreateView,
)

app_name = "chains"

urlpatterns = [
    path("add/", ChainCreateView.as_view(), name="add_chain"),
    path(
        "templates/add/", ChainTemplateCreateView.as_view(), name="add_chain_template"
    ),
    path("", ChainListView.as_view(), name="chain_list"),
    path("templates/", ChainTemplateListView.as_view(), name="chain_template_list"),
    path("<int:chain_id>/", ChainView.as_view(), name="view_chain"),
    path(
        "templates/<int:template_id>/",
        ChainTemplateView.as_view(),
        name="view_chain_template",
    ),
    path(
        "<int:chain_id>/target/<int:pk>/",
        ChainedTargetDetailView.as_view(),
        name="chain_target",
    ),
    path(
        "<int:chain_id>/<str:facility>/create/",
        SingleObservationCreateView.as_view(),
        name="create",
    ),
    path(
        "templates/<int:template_id>/<str:facility>/create/",
        ChainedTemplateCreateView.as_view(),
        name="add_template",
    ),
]
