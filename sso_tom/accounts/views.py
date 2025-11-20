import logging

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .forms.profile import EditProfileForm
from .forms.registation import RegistrationForm

logger = logging.getLogger(__name__)


def registration(request):
    """
    View to process the registration
    :param request: A Django request object
    :return: A rendered HTML template
    """

    # returning to profile if the user is authenticated
    if request.user.is_authenticated:
        return redirect(reverse("profile"))

    data = {}
    if request.method == "POST":

        # creating the registration form from the data
        form = RegistrationForm(request.POST)

        # if form is valid save the information
        if form.is_valid():
            data = form.cleaned_data
            form.save()

            return render(
                request,
                "accounts/notification.html",
                {
                    "type": "registration_submitted",
                    "data": data,
                },
            )
    else:

        # get request will serve a blank form
        form = RegistrationForm()

    return render(
        request,
        "accounts/registration.html",
        {
            "form": form,
            "data": data,
            "submit_text": "Register",
        },
    )


@login_required
def profile(request):
    """
    View to process the profile updates
    :param request: A Django request object
    :return: A rendered HTML template
    """

    data = {}
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            data = form.cleaned_data
            form.save()
            messages.success(
                request, "Information successfully updated", "alert alert-success"
            )
            return render(
                request,
                "accounts/profile.html",
                {
                    "form": form,
                    "type": "update_profile_success",
                    "data": data,
                },
            )
        else:
            messages.error(
                request, "Please correct the error(s) below.", "alert alert-warning"
            )
    else:
        form = EditProfileForm(instance=request.user)

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "data": data,
            "submit_text": "Update",
        },
    )
