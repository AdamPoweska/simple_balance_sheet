from django.urls import path
from . import views

urlpatterns = [
    path('', views.HelloView.as_view(), name='first_hello'),
    path('user_logout/', views.UserLogoutView.as_view(), name='user_logout'),
    # path('trial_balance/', views.TrialBalanceListView.as_view(), name='trial_balance'),
    path('trial_balance/', views.ParentViewTrialBalance.as_view(), name='trial_balance'),
    path('user_form/', views.AccountCreateView.as_view(), name='user_form'),
    path('user_login/', views.UserLoginView.as_view(), name='user_login'),
    path('user_registration/', views.UserRegisterView.as_view(), name='user_registration'),
    path('delete_account/', views.AccountDeleteView.as_view(), name='delete_account'),
    path('account_update_select/', views.AccountUpdateSelectView.as_view(), name='account_update_select'),
    path('update_account/<int:pk>/', views.AccountUpdateView.as_view(), name='update_account'),
]
