import pytest
from django.contrib.auth.models import User, Group
from django.urls import reverse

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
        "email": "test@test.com",
        "password1": "password123!@#",
        "password2": "password123!@#"
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

#tests of AccountDeleteForm:
@pytest.mark.django_db
def test_account_delete_form_1():
    # formularz gdzie nie przekazujemy żadnego konta, więc bedzie pusty
    form = AccountDeleteForm(data={})
    assert form.is_valid()

@pytest.mark.django_db
def test_account_delete_form_2():
    # stworzenie konta:
    account = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # formularz gdzie nie przekazujemy żadnego konta, więc bedzie pusty
    form = AccountDeleteForm(data={})
    
    # is_valid musi być wywołane przed cleaned data
    assert form.is_valid()
    
    # sprawdzamy czy lista wybranych kont faktyczni bedzie pusta
    assert list(form.cleaned_data['accounts_to_delete']) == []

#sprawdzenie czy pojedyńcze konto zostaje poprawnie przekazane do usunięcia
@pytest.mark.django_db
def test_account_delete_form_3():
    # stworzenie konta:
    account = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # przekazujemy konto do usunięcia
    form = AccountDeleteForm(data={
        'accounts_to_delete': [account.id] #musi byc w [] bo ModelMultipleChoiceField potzebuje dostać listę wartości, musi byc tez .id <- ponieważ ponownie ModelMultipleChoiceField oczekuje identyfikatorów obiektów a nie samych obiektów
    })
    
    # is_valid musi być wywołane przed cleaned data
    assert form.is_valid()
    
    # sprawdzamy czy wybrane konto faktycznie jest na liscie do usunięcia
    assert list(form.cleaned_data['accounts_to_delete']) == [account]

#sprawdzenie czy pojedyńcze konta zostają poprawnie przekazane do usunięcia
@pytest.mark.django_db
def test_account_delete_form_4():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    account_2 = SimpleTrialBalance.objects.create(
        account_name = "account_2",
        account_number = "60020",
        opening_balance = 100,
        activity = 100,
    )

    # przekazujemy konto do usunięcia
    form = AccountDeleteForm(data={
        'accounts_to_delete': [account_1.id, account_2.id] #musi byc w [] bo ModelMultipleChoiceField potzebuje dostać listę wartości, musi byc tez .id <- ponieważ ponownie ModelMultipleChoiceField oczekuje identyfikatorów obiektów a nie samych obiektów
    })
    
    # is_valid musi być wywołane przed cleaned data
    assert form.is_valid()
    
    # sprawdzamy czy wybrane konta faktycznie sa na liscie do usunięcia
    assert list(form.cleaned_data['accounts_to_delete']) == [account_1, account_2]

# sprawdzenie czy wybrane konto zostaje faktycznie usunięte
@pytest.mark.django_db
def test_account_delete_form_4():
    # stworzenie konta:
    account = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # przekazujemy konto do usunięcia
    form = AccountDeleteForm(data={
        'accounts_to_delete': [account.id] #musi byc w [] bo ModelMultipleChoiceField potzebuje dostać listę wartości, musi byc tez .id <- ponieważ ponownie ModelMultipleChoiceField oczekuje identyfikatorów obiektów a nie samych obiektów
    })
    
    # is_valid musi być wywołane przed cleaned data
    assert form.is_valid()
    
    # pobranie konta do usunięcia
    accounts_to_delete = form.cleaned_data['accounts_to_delete']

    # usunięcie konta
    accounts_to_delete.delete()

    #sprawdzamy czy konto faktycznie jest usunięte
    assert not SimpleTrialBalance.objects.filter(id=account.id).exists()

#sprawdzenie czy konta zostają poprawnie usunięte
@pytest.mark.django_db
def test_account_delete_form_5():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    account_2 = SimpleTrialBalance.objects.create(
        account_name = "account_2",
        account_number = "60020",
        opening_balance = 100,
        activity = 100,
    )

    # przekazujemy konta do usunięcia
    form = AccountDeleteForm(data={
        'accounts_to_delete': [account_1.id, account_2.id] #musi byc w [] bo ModelMultipleChoiceField potzebuje dostać listę wartości, musi byc tez .id <- ponieważ ponownie ModelMultipleChoiceField oczekuje identyfikatorów obiektów a nie samych obiektów
    })
    
    # is_valid musi być wywołane przed cleaned data
    assert form.is_valid()
    
    # pobranie kont do usunięcia
    accounts_to_delete = form.cleaned_data['accounts_to_delete']

    # usunięcie kont
    accounts_to_delete.delete()

    #sprawdzamy czy konta faktycznie sa usunięte
    assert not SimpleTrialBalance.objects.filter(id=account_1.id).exists()
    assert not SimpleTrialBalance.objects.filter(id=account_2.id).exists()

# test AccountUpdateSelect
@pytest.mark.django_db
def test_account_update_form_1():
    # formularz gdzie nie przekazujemy żadnego danych
    form = AccountUpdateSelect(data={})
    # wiec formilarz nie jest poprawny
    assert not form.is_valid()

# czy dane sa poprawnie przekazane do formularza
@pytest.mark.django_db
def test_account_update_form_2():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # wypełnienie formularza
    form = AccountUpdateSelect(data={'account_update_select': account_1.id})

    assert form.is_valid()

@pytest.mark.django_db
def test_account_update_form_3():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # wypełnienie formularza
    form = AccountUpdateSelect(data={'account_update_select': account_1.id})

    assert form.is_valid()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 30011 | 0 | 100 | 100"

@pytest.mark.django_db
def test_account_update_form_4():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # wypełnienie formularza
    form = AccountUpdateSelect(data={'account_update_select': account_1.id})

    assert form.is_valid()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__str__() == "account_1 | 30011"

@pytest.mark.django_db
def test_account_update_form_5():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # wypełnienie formularza
    form = AccountUpdateSelect(data={'account_update_select': account_1.id})

    assert form.is_valid()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 30011 | 0 | 100 | 100"

    account_1.activity = 200
    account_1.save()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 30011 | 0 | 200 | 200"

@pytest.mark.django_db
def test_account_update_form_6():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # wypełnienie formularza
    form = AccountUpdateSelect(data={'account_update_select': account_1.id})

    assert form.is_valid()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 30011 | 0 | 100 | 100"

    account_1.account_name = "account_2"
    account_1.save()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_2 | 30011 | 0 | 100 | 100"

@pytest.mark.django_db
def test_account_update_form_7():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # wypełnienie formularza
    form = AccountUpdateSelect(data={'account_update_select': account_1.id})

    assert form.is_valid()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 30011 | 0 | 100 | 100"

    account_1.account_number = "60020"
    account_1.save()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 60020 | 0 | 100 | 100"

@pytest.mark.django_db
def test_account_update_form_8():
    # stworzenie konta:
    account_1 = SimpleTrialBalance.objects.create(
        account_name = "account_1",
        account_number = "30011",
        opening_balance = 0,
        activity = 100,
    )

    # wypełnienie formularza
    form = AccountUpdateSelect(data={'account_update_select': account_1.id})

    assert form.is_valid()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 30011 | 0 | 100 | 100"

    account_1.opening_balance = 50
    account_1.save()

    assert SimpleTrialBalance.objects.get(id=account_1.id).__repr__() == "account_1 | 30011 | 50 | 100 | 150"


# Testy widoków
@pytest.mark.django_db
def test_first_hello(client): # client to specjalne narzędzie do testowania widoków: 'do symulowania żądań HTTP'
    url = reverse("first_hello") #  URL jak w urls.py
    response = client.get(url)

    assert response.status_code == 200 # sprawdza czy strona się ładuje
    assert "first_hello.html" in [x.name for x in response.templates] # sprawdza czy 'first_hello.html' został użyty
