# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def hello_view(request):
    template = loader.get_template('first_hello.html')
    return HttpResponse(template.render())