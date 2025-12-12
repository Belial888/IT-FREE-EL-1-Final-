# core/views.py

from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import AidRequest, Distribution, Beneficiary
from django.shortcuts import get_object_or_404, redirect
from .forms import ResidentRegistrationForm
from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import DetailView
from .forms import BeneficiaryForm, DistributionForm
from django.views.generic import DetailView


class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = ResidentRegistrationForm
    success_url = reverse_lazy('login') # Redirect to login after successful registration

class DistributionReportView(UserPassesTestMixin, ListView):
    model = Distribution
    template_name = 'distribution_report.html'
    context_object_name = 'distributions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate total quantity distributed per item
        context['summary'] = Distribution.objects.values('item_name').annotate(total_qty=Sum('qty'))
        return context

    def test_func(self):
        return self.request.user.is_staff
    
# RESIDENT VIEW: Submits an aid request
class RequestCreateView(LoginRequiredMixin, CreateView):
    model = AidRequest
    fields = ['item_requested', 'quantity_requested']
    template_name = 'core/request_form.html'
    # Redirect to home after submitting a request (previously referenced a missing 'request_list')
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Automatically set the beneficiary based on the logged-in user
        # Create if doesn't exist (for old users who registered before this feature)
        beneficiary, created = Beneficiary.objects.get_or_create(user=self.request.user)
        form.instance.beneficiary = beneficiary
        return super().form_valid(form)


def home_view(request):
    # Provide dashboard counts for home page
    stats = {}
    if request.user.is_authenticated:
        if request.user.is_staff:
            stats['total_requests'] = AidRequest.objects.count()
            stats['pending_requests'] = AidRequest.objects.filter(status='PENDING').count()
            stats['approved_requests'] = AidRequest.objects.filter(status='APPROVED').count()
            stats['distributed'] = AidRequest.objects.filter(status='DISTRIBUTED').count()
        else:
            # Resident stats
            resident_requests = AidRequest.objects.filter(beneficiary__user=request.user)
            stats['my_requests'] = resident_requests.count()
            stats['my_pending'] = resident_requests.filter(status='PENDING').count()
            stats['approved_requests'] = resident_requests.filter(status='APPROVED').count()
            stats['distributed'] = resident_requests.filter(status='DISTRIBUTED').count()
    return render(request, 'home.html', {'stats': stats})


class RequestDetailView(LoginRequiredMixin, DetailView):
    model = AidRequest
    template_name = 'core/request_detail.html'
    context_object_name = 'request_obj'


# Resident view: list the current user's requests
class RequestListView(LoginRequiredMixin, ListView):
    model = AidRequest
    template_name = 'core/request_list.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        return AidRequest.objects.filter(beneficiary__user=self.request.user).order_by('-date_requested')


# Resident profile: view and edit beneficiary details
class BeneficiaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Beneficiary
    form_class = BeneficiaryForm
    template_name = 'core/beneficiary_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return get_object_or_404(Beneficiary, user=self.request.user)


# Staff: record a distribution
class DistributionCreateView(UserPassesTestMixin, CreateView):
    model = Distribution
    form_class = DistributionForm
    template_name = 'core/distribution_form.html'
    success_url = reverse_lazy('distribution_report')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.barangay_staff = self.request.user
        return super().form_valid(form)

# ADMIN VIEW: List all requests for verification
class AdminRequestListView(UserPassesTestMixin, ListView):
    model = AidRequest
    template_name = 'admin_request_list.html'
    context_object_name = 'requests'

    # Only allow barangay staff to access this view
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        qs = super().get_queryset().order_by('-date_requested')
        status = self.request.GET.get('status')
        q = self.request.GET.get('q')
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(item_requested__icontains=q) | qs.filter(beneficiary__full_name__icontains=q)
        return qs

# ADMIN VIEW: Update the status (Verify/Approve) of a request
class RequestUpdateView(UserPassesTestMixin, UpdateView):
    model = AidRequest
    fields = ['status'] # Admin can change the status for verification
    template_name = 'core/request_update_form.html'
    success_url = reverse_lazy('admin_request_list')

    # Only allow barangay staff to access this view
    def test_func(self):
        return self.request.user.is_staff