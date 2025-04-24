import pytest
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse

from account.models import SimpleTrialBalance
from account.forms import *


@pytest.mark.django_db
def test_trial_balance_1():    
    account_name_var="GenLedgAcct"
    account_number_var=1234
    opening_balance_var=100
    activity_var=10

    trial_balance = SimpleTrialBalance.objects.create(
        account_name=account_name_var,
        account_number=account_number_var,
        opening_balance=opening_balance_var,
        activity=activity_var,
    )

    assert str(trial_balance) == f"{account_name_var} | {account_number_var}"

@pytest.mark.django_db
def test_trial_balance_2():
    account_name_var="GenLedgAcct"
    account_number_var=1234
    opening_balance_var=100
    activity_var=10

    trial_balance = SimpleTrialBalance.objects.create(
        account_name=account_name_var,
        account_number=account_number_var,
        opening_balance=opening_balance_var,
        activity=activity_var,
    )

    assert trial_balance.closing_balance == int(opening_balance_var) + int(activity_var)

@pytest.mark.django_db
def test_trial_balance_3():
    account_name_var="GenLedgAcct"
    account_number_var=1234
    opening_balance_var=100
    activity_var=10

    trial_balance = SimpleTrialBalance.objects.create(
        account_name=account_name_var,
        account_number=account_number_var,
        opening_balance=opening_balance_var,
        activity=activity_var,
    )
    
    activity_total = int(opening_balance_var) + int(activity_var)
    assert repr(trial_balance) == f"{account_name_var} | {account_number_var} | {opening_balance_var} | {activity_var} | {activity_total}"
