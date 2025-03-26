import pytest
from django.contrib.auth.models import User, Group

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

@pytest.mark.django_db
def test_trial_balance_form_1():
    form = TrialBalanceForm(data={
        "account_name": "GenLedgAcct",
        "account_number": 1234,
        "opening_balance": 100,
        "activity": 10,
    })

    assert form.is_valid()

@pytest.mark.django_db
def test_trial_balance_form_2():
    # nowy yżytkonik
    user = User.objects.create_user(username="testuser_1", password="password_1")

    # nadanie użytkownikowi accessu z new_hire_perm:
    group = Group.objects.create(name="new_hire_permissions")
    user.groups.add(group)

    # stworzenie formularza dla powyższego usera
    form = TrialBalanceForm(user=user)

    # czy faktycznie pola sa zablokowane
    assert form.fields["account_name"].disabled is True
    assert form.fields["account_number"].disabled is True
    assert form.fields["opening_balance"].disabled is True

@pytest.mark.django_db
def test_trial_balance_form_3():
    # nowy superuser
    user = User.objects.create_superuser(username="superuser_1", password="password_1")

    # stworzenie formularza dla superusera
    form = TrialBalanceForm(user=user)

    # czy faktycznie pola sa odblokowane
    assert form.fields["account_name"].disabled is False
    assert form.fields["account_number"].disabled is False
    assert form.fields["opening_balance"].disabled is False