from django.urls import path
from . import views

urlpatterns = [
    path('', views.TrialBalanceListView.as_view(), name='trial_balance'),
    path('user_form/', views.AccountCreateView.as_view(), name='user_form'),
]
