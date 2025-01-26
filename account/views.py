# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, TemplateView, ListView, UpdateView

from .forms import *

def hello_view(request):
    template = loader.get_template('first_hello.html')
    return HttpResponse(template.render())

class AccountCreateView(CreateView):
    template_name = 'user_form.html'
    form_class = TrialBalanceForm
    success_url = reverse_lazy('trial_balance')

class TrialBalanceListView(ListView):
    model = SimpleTrialBalance
    template_name = 'trial_balance.html'
    context_object_name = 'trial_balance_data' # dane przekazywane do kontekstu