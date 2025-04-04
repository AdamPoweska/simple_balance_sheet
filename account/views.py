# Create your views here.
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template import loader
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, ListView, UpdateView
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView

from .forms import *
from .models import *


class HelloView(TemplateView):
    template_name = 'first_hello.html'


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('trial_balance')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('first_hello')
    # redirect_authenticated_user = True
    # success_url = 'first_hello'


class UserRegisterView(FormView):
    template_name = 'registration/user_registration.html'
    form_class = NewUserForm
    success_url = reverse_lazy('trial_balance')

    def form_valid(self, form):
        user = form.save() # zapisanie użytkownika, FormView nie robi tego automatycznie
        user_group, _ = Group.objects.get_or_create(name="new_hire_permissions") # get_or_create() zwraca krotkę (group, created) _ oznacza, że ignorujemy drugą wartość (created, czyli czy grupa została utworzona).
        user.groups.add(user_group) # nadanie nowemu użytkownikowi grupy new_hire_permissions - czyli podstawowe dostępy -> działa, jest wszystko w panelu admina
        login(self.request, user) # zalogowanie użytkownika
        return super().form_valid(form)


class AccountCreateView(CreateView):
    template_name = 'user_form.html'
    form_class = TrialBalanceForm
    success_url = reverse_lazy('trial_balance')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='all_permissions').exists(): # jeśli użytkownik nie należy do grupy 'all_permissions' to zwróci się na Httpresponse forbidden, jeśli jednak nim jest to dostanie standardową metodę dispatch
            raise PermissionDenied # django w ten sposób przekieruje do 403.html zapisanego w tamples (nadpisanego)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # przekazujemy użytkownika do formularza
        return kwargs


class AccountDeleteView(FormView):
    template_name = 'delete_account.html'
    form_class = AccountDeleteForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='all_permissions').exists(): # jeśli użytkownik nie należy do grupy 'all_permissions' to zwróci się na Httpresponse forbidden, jeśli jednak nim jest to dostanie standardową metodę dispatch
            raise PermissionDenied # django w ten sposób przekieruje do 403.html zapisanego w tamples (nadpisanego)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        accounts_to_delete = form.cleaned_data['accounts_to_delete']
        accounts_to_delete.delete()
        return redirect('trial_balance')


class AccountUpdateSelectView(FormView):
    template_name = 'account_update_select.html'
    form_class = AccountUpdateSelect
    
    def form_valid(self, form):
        selected_account = form.cleaned_data['account_update_select']
        return redirect('update_account', pk=selected_account.pk)


class AccountUpdateView(UpdateView):
    model = SimpleTrialBalance
    form_class = TrialBalanceForm
    template_name = 'update_account.html'

    def get_success_url(self):
        return reverse_lazy('trial_balance')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # przekazujemy użytkownika do formularza
        return kwargs


class ParentViewTrialBalance(TemplateView):
    template_name = 'trial_balance.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pobieranie danych z MODELU
        context['trial_balance_data'] = SimpleTrialBalance.objects.all() 
        # dropdown:
        context['dropdown_list_main'] = [
            {'name': 'Add account', 'class': 'AccountCreateView'},
            {'name': 'Delete account', 'class': 'AccountDeleteView'},
            {'name': 'Update account', 'class': 'AccountUpdateSelectView'},
        ]
        return context
    
    def get(self, request, *args, **kwargs):
        action = request.GET.get('action')

        if action == 'AccountDeleteView':
            return redirect('delete_account')
        elif action == 'AccountUpdateSelectView':
            return redirect('account_update_select')
        elif action == 'AccountCreateView':
            return redirect('user_form')
        return super().get(request, *args, **kwargs)
