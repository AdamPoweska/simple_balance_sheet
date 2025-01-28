# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, ListView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView

from .forms import *
from .models import *

# def hello_view(request):
#     template = loader.get_template('first_hello.html')
#     return HttpResponse(template.render())

class HelloView(TemplateView):
    template_name = 'first_hello.html'


class UserLoginView(LoginView):
    template_name = 'registration/user_login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('trial_balance')


class UserLogoutView(LogoutView):
    redirect_authenticated_user = True
    success_url = 'first_hello'


class UserRegisterView(FormView):
    template_name = 'registration/user_registration.html'
    form_class = NewUserForm
    success_url = reverse_lazy('trial_balance')

    def form_valid(self, form):
        user = form.save() # zapisanie użytkownika, FormView nie robi tego automatycznie
        login(self.request, user) # zalogowanie użytkownika
        return super().form_valid(form)


class AccountCreateView(CreateView):
    template_name = 'user_form.html'
    form_class = TrialBalanceForm
    success_url = reverse_lazy('trial_balance')


# class TrialBalanceListView(ListView):
#     model = SimpleTrialBalance
#     template_name = 'trial_balance.html'
#     context_object_name = 'trial_balance_data' # dane przekazywane do kontekstu pod nazwą 'trial_balance_data'


class FormsDropdownList(TemplateView):
    template_name = 'trial_balance.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['dropdown_list_main'] = [ # dane przekazywane do kontekstu pod nazwą 'dropdown_list_main'
            {'name': 'Add account', 'class': 'TrialBalanceForm'}
        ]

        return context
    

class ParentViewTrialBalance(TemplateView):
    template_name = 'trial_balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pobieranie danych z MODELU
        context['trial_balance_data'] = SimpleTrialBalance.objects.all() 
        # dropdown:
        context['dropdown_list_main'] = [
            {'name': 'Add account','class': 'TrialBalanceForm'}
        ]
        return context
