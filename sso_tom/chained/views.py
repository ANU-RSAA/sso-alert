import logging
from io import StringIO
from urllib.parse import urlencode

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import BadRequest
from django.core.management import call_command
from django.forms import HiddenInput
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

from crispy_forms.layout import Div, Layout, ButtonHolder, Submit, Fieldset
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, ListView, CreateView, DetailView
from django.views.generic.edit import FormView
from tom_common.hints import add_hint
from tom_common.mixins import Raise403PermissionRequiredMixin
from tom_observations.facility import get_service_class, get_service_classes
from tom_observations.models import ObservationTemplate, ObservationRecord
# from tom_observations.observation_template import ApplyObservationTemplateForm
from .forms import ChainedApplyObservationTemplateForm, ChainTemplateForm

from tom_observations.views import ObservationCreateView, ObservationTemplateCreateView
from tom_targets.models import Target
from tom_targets.views import TargetDetailView

from .forms import ChainedObservationForm, ChainForm
from .models import ChainedObservation, Chain, SUBMITTED, TemplatedChain, ChainedTemplate

logger = logging.getLogger(__name__)


class ChainedTargetDetailView(Raise403PermissionRequiredMixin, DetailView):
    """
    View that handles the display of the target details for chained observations. Requires authorization.
    """
    permission_required = 'tom_targets.view_target'
    model = Target
    template_name = 'chained/chain_target_detail.html'

    def get_context_data(self, *args, **kwargs):
        """
        Adds the ``DataProductUploadForm`` to the context and prepopulates the hidden fields.

        :returns: context object
        :rtype: dict
        """
        context = super().get_context_data(*args, **kwargs)
        chain_id = self.kwargs.get('chain_id', None)
        chain = Chain.objects.get(pk=chain_id)
        if not chain:
            raise BadRequest('Chain not found')

        observation_template_form = ChainedApplyObservationTemplateForm(initial={
            'target': self.get_object(),
            'chain': chain,
        })

        if any(self.request.GET.get(x) for x in ['observation_template']):
            initial = {'target': self.object}
            initial.update(self.request.GET)
            observation_template_form = ChainedApplyObservationTemplateForm(
                initial=initial
            )
        observation_template_form.fields['chain'].widget = HiddenInput()
        observation_template_form.fields['target'].widget = HiddenInput()
        context['observation_template_form'] = observation_template_form
        context['chain_id'] = chain.id
        return context

    def get(self, request, *args, **kwargs):
        """
        Handles the GET requests to this view. If update_status is passed into the query parameters, calls the
        updatestatus management command to query for new statuses for ``ObservationRecord`` objects associated with this
        target.

        :param request: the request object passed to this view
        :type request: HTTPRequest
        """
        update_status = request.GET.get('update_status', False)
        chain_id = kwargs.get('chain_id', None)
        if update_status:
            if not request.user.is_authenticated:
                return redirect(reverse('login'))
            target_id = kwargs.get('pk', None)
            out = StringIO()
            call_command('updatestatus', target_id=target_id, stdout=out)
            messages.info(request, out.getvalue())
            add_hint(request, mark_safe(
                'Did you know updating observation statuses can be automated? Learn how in'
                '<a href=https://tom-toolkit.readthedocs.io/en/stable/customization/automation.html>'
                ' the docs.</a>'))
            return redirect(reverse('tom_targets:detail', args=(target_id,)) + '?tab=observations')

        obs_template_form = ChainedApplyObservationTemplateForm(request.GET)
        if obs_template_form.is_valid():
            obs_template = ObservationTemplate.objects.get(pk=obs_template_form.cleaned_data['observation_template'].id)
            obs_template_params = obs_template.parameters
            obs_template_params['cadence_strategy'] = request.GET.get('cadence_strategy', '')
            obs_template_params['cadence_frequency'] = request.GET.get('cadence_frequency', '')
            params = urlencode(obs_template_params)
            return redirect(
                reverse('chains:create',
                        args=(chain_id, obs_template.facility)) + f'?target_id={self.get_object().id}&' + params)

        return super().get(request, *args, **kwargs)


class SingleObservationCreateView(ObservationCreateView):
    def get_form(self, form_class=None):
        """
        Gets an instance of the form appropriate for the request.

        :returns: observation form
        :rtype: subclass of GenericObservationForm
        """
        try:
            form = super(FormView, self).get_form()
        except Exception as ex:
            logger.error(f"Error loading {self.get_facility()} form: {repr(ex)}")
            raise BadRequest(f"Error loading {self.get_facility()} form: {repr(ex)}")

        # tom_observations/facility.BaseObservationForm.__init__ to see how
        # groups is added to common_layout
        if not settings.TARGET_PERMISSIONS_ONLY:
            form.fields['groups'].queryset = self.request.user.groups.all()

        form.helper.form_action = reverse(
            'chains:create', kwargs=self.kwargs
        )
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'validate' in request.POST:
                return self.form_validation_valid(form)
            else:
                return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        Runs after form validation. Submits the observation to the desired facility and creates an associated
        ``ObservationRecord``, then redirects to the detail page of the target to be observed.

        If the facility returns more than one record, a group is created and all observation
        records from the request are added to it.

        :param form: form containing observating request parameters
        :type form: subclass of GenericObservationForm
        """
        # Submit the observation
        facility = self.get_facility_class()()
        facility.set_user(self.request.user)
        target = self.get_target()
        observation_payload = form.observation_payload()
        # observation_ids = facility.submit_observation(form.observation_payload())
        records = []

        # for observation_id in observation_ids:
        #     # Create Observation record
        #     record = ObservationRecord.objects.create(
        #         target=target,
        #         user=self.request.user,
        #         facility=facility.name,
        #         parameters=form.serialize_parameters(),
        #         observation_id=observation_id
        #     )
        #     records.append(record)

        chained_observation = ChainedObservation.objects.create(
            chain=Chain.objects.get(pk=self.kwargs['chain_id']),
            facility=facility.name,
            parameters=observation_payload['params'],
        )

        return redirect(
            reverse('chains:view_chain', kwargs={'chain_id': self.kwargs['chain_id']})
        )


class ChainCreateView(CreateView):
    model = Chain
    form_class = ChainForm
    template_name = 'chained/chain_add.html'
    success_url = reverse_lazy('chains:chain_list')

    def get_form_kwargs(self):
        kwargs = super(ChainCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ChainListView(ListView):
    model = Chain
    template_name = "chained/chain_list.html"

    def get_queryset(self):
        qs = super(ChainListView, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class ChainView(TemplateView):
    template_name = 'chained/chain_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chain_id = self.kwargs.get('chain_id')
        chain = get_object_or_404(
            Chain,
            pk=chain_id,
            user=self.request.user)

        chained_observations = ChainedObservation.objects.filter(
            chain=chain,
        )

        context['chain'] = chain
        context['chained_observations'] = chained_observations
        return context

    def post(self, request, *args, **kwargs):
        chain_id = self.kwargs.get('chain_id', None)

        chain = get_object_or_404(
            Chain,
            pk=chain_id,
            user=request.user,
        )

        chained_observations = ChainedObservation.objects.filter(chain=chain).order_by('created')

        if chained_observations.exists():
            first_chained_observation = chained_observations.first()

            facility = get_service_class(first_chained_observation.facility)()

            observation_ids = facility.submit_observation({
                'target': chain.target,
                'params': first_chained_observation.parameters,
            })

            # Create Observation record
            record = ObservationRecord.objects.create(
                target=chain.target,
                user=self.request.user,
                facility=facility.name,
                parameters=first_chained_observation.parameters,
                observation_id=observation_ids[0]
            )

            first_chained_observation.observation = record
            first_chained_observation.save()

            chain.status = SUBMITTED
            chain.save()

        return redirect(
            reverse('chains:view_chain', kwargs={'chain_id': chain_id})
        )


class ChainTemplateCreateView(CreateView):
    model = TemplatedChain
    form_class = ChainTemplateForm
    template_name = 'chained/chain_template_add.html'
    success_url = reverse_lazy('chains:chain_template_list')

    def get_form_kwargs(self):
        kwargs = super(ChainTemplateCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ChainTemplateListView(ListView):
    model = TemplatedChain
    template_name = "chained/chain_template_list.html"

    def get_queryset(self):
        qs = super(ChainTemplateListView, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs


class ChainTemplateView(TemplateView):
    template_name = 'chained/chain_template_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template_id = self.kwargs.get('template_id')
        templated_chain = get_object_or_404(
            TemplatedChain,
            pk=template_id,
            user=self.request.user)

        chained_templates = ChainedTemplate.objects.filter(
            templated_chain=templated_chain,
        )

        context['templated_chain'] = templated_chain
        context['chained_templates'] = chained_templates
        context['installed_facilities'] = get_service_classes()
        return context


class ChainedTemplateCreateView(ObservationTemplateCreateView):

    def get_form(self, form_class=None):
        form = super().get_form()
        form.helper.form_action = reverse('chains:add_template',
                                          kwargs={
                                              'template_id': self.kwargs['template_id'],
                                              'facility': self.get_facility_name()}
                                          )
        return form

    def form_valid(self, form):
        # calls the GenericTemplateForm's save method which returns the template
        # leaving it as is so that this can be used as a single template later on.
        template = form.save()

        # now creating a chained_template instance
        ChainedTemplate.objects.create(
            templated_chain=TemplatedChain.objects.get(pk=self.kwargs['template_id']),
            name=template.name,
            facility=template.facility,
            parameters=template.parameters,
        )

        return redirect(reverse('chains:view_chain_template',
                                kwargs={'template_id': self.kwargs['template_id'],
                                        }))
