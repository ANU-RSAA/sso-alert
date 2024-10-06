"""django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from .views import AboutView, page_not_found, CustomObservationCreateView, CustomObservationTemplateCreateView, \
    CustomObservationTemplateUpdateView

urlpatterns = [
    # disabled pages
    path("observations/status/", page_not_found, name="facility-status"),

    # required for custom validation of proposal id using user information
    path("observations/<str:facility>/create/", CustomObservationCreateView.as_view(), name="create"),
    path('observations/template/<str:facility>/create/', CustomObservationTemplateCreateView.as_view(),
         name='template-create'),
    path('observations/template/<int:pk>/update/', CustomObservationTemplateUpdateView.as_view(),
         name='template-update'),
    path('observations/template/<int:pk>/', CustomObservationTemplateUpdateView.as_view(), name='template-detail'),

    path("", include("tom_registration.registration_flows.open.urls", namespace="registration"), ),
    path("", include("accounts.urls")),
    path("", include("tom_common.urls")),
    path("chains/", include("chained.urls")),
    path("sso_alerts/", include("sso_alerts.urls")),
    path("about/", AboutView.as_view(), name="about"),
]
