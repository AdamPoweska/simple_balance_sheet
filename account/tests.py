import pytest

from .models import SimpleTrialBalance
from .forms import *

# Model tests:
@pytest.mark.django_db
def test_trial_balance_1():
    trial_balance = SimpleTrialBalance.objects.create(
        account_name="GenLedgAcct",
        account_number=1234,
        opening_balance=100,
        activity=10,
    )

    assert str(trial_balance) == "GenLedgAcct | 1234"

@pytest.mark.django_db
def test_trial_balance_2():
    trial_balance = SimpleTrialBalance.objects.create(
        account_name="GenLedgAcct",
        account_number=1234,
        opening_balance=100,
        activity=10,
    )

    assert trial_balance.closing_balance == 110

@pytest.mark.django_db
def test_trial_balance_3():
    trial_balance = SimpleTrialBalance.objects.create(
        account_name="GenLedgAcct",
        account_number=1234,
        opening_balance=100,
        activity=10,
    )

    assert repr(trial_balance) == "GenLedgAcct | 1234 | 100 | 10 | 110"


# forms tests:
@pytest.mark.django_db
def test_new_user():
    form_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "strongpassword123",
        "password2": "strongpassword123"
    }
    form = NewUserForm(data=form_data)
    assert form.is_valid()