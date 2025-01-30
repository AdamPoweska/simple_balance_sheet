from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.HelloView.as_view(), name='first_hello'),
    path('user_logout/', views.UserLogoutView.as_view(), name='user_logout'),
    # path('trial_balance/', views.TrialBalanceListView.as_view(), name='trial_balance'), # poprzedni url kiedy nie było jeszcze parent view
    path('trial_balance/', views.ParentViewTrialBalance.as_view(), name='trial_balance'),
    path('user_form/', views.AccountCreateView.as_view(), name='user_form'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('user_registration/', views.UserRegisterView.as_view(), name='user_registration'),
    path('delete_account/', views.AccountDeleteView.as_view(), name='delete_account'),
    path('account_update_select/', views.AccountUpdateSelectView.as_view(), name='account_update_select'),
    path('update_account/<int:pk>/', views.AccountUpdateView.as_view(), name='update_account'),
    # do resetowania hasła - gotowe widoki już istniejące w django
    path('reset_password//', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
