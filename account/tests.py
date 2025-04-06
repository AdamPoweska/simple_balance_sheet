import pytest
from django.contrib.auth.models import User, Group, Permission
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
    url = reverse("first_hello") #  reverse() zmienia nazwę widoku (taki jak jest w urls.py) na odpowiadający jej url, podajemy nazwę taka jaka jest w urls.py > name=
    response = client.get(url)

    assert response.status_code == 200 # sprawdza czy strona się ładuje
    assert "first_hello.html" in [x.name for x in response.templates] # sprawdza czy szablon 'first_hello.html' - czyli czy używamy odpowiedniego szablonu

@pytest.mark.django_db
def test_user_login_view_1(client):
    url = reverse("login")
    response = client.get(url)

    assert response.status_code == 200
    assert "registration/login.html" in [t.name for t in response.templates]

@pytest.mark.django_db
def test_user_login_view_2(client, django_user_model):
    # sprawdzamy czy wystąpi 302 - oczekiwanie na przekierowanie
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    client.login(username="user_1", password="pw1234") # logowanie użytkownika

    url = reverse("login")
    response = client.get(url)

    assert response.status_code == 302 # 302 oznacza że zasób do o którego użytkownik próbuje uzyskać dostęp, został tymczasowo przeniesiony na nowy adres URL
    assert response.url == reverse("trial_balance") # sprawdzamy czy przekierowanie działa ale nie podąża za nim automatycznie

@pytest.mark.django_db
def test_user_login_view_3(client, django_user_model):
    # sprawdzamy czy użytkownik zostanie poprawnie przekierowoany po zalogowaniu
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")

    url = reverse("login")
    response = client.post(url, {"username": "user_1", "password": "pw1234"}, follow=True) # musimy użyc follow=, żeby sprawdzić czy użytkownik faktycznie został przekierowny po zalogowaniu

    assert response.status_code == 200 #status po przekierowaniu
    assert response.request["PATH_INFO"] == reverse("trial_balance") # czy użytkownik został poprawnie przekierowany na trail_balance

@pytest.mark.django_db
def test_user_login_view_4(client):
    # test błędnego logowania
    url = reverse("login")
    response = client.post(url, {"username": "user_x", "password": "pwxxx"})

    assert response.status_code == 200 # pozostajemy na stronie, nie ma przekierowania
    error_message = "Please enter a correct username and password. Note that both fields may be case-sensitive."
    assert error_message in response.content.decode() # uzyskanie dostępu do kodu html (pełna treść) w str

@pytest.mark.django_db
def test_user_logout_view(client, django_user_model):
    # sprawdzamy czy użytkownik zostanie poprawnie przekierowoany po wylogowaniu
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")

    url = reverse("login")
    response = client.post(url, {"username": "user_1", "password": "pw1234"}, follow=True) # musimy użyc follow=, żeby sprawdzić czy użytkownik faktycznie został przekierowny po zalogowaniu
    
    #zalogowanie
    assert response.status_code == 200 #status po przekierowaniu
    assert response.request["PATH_INFO"] == reverse("trial_balance") # czy użytkownik został poprawnie przekierowany na trail_balance

    url = reverse("user_logout")
    response = client.post(url, follow=True) #LogoutView działa na post

    # wylogowanie
    assert response.status_code == 200 #status po przekierowaniu
    assert response.request["PATH_INFO"] == reverse("first_hello") # czy użytkownik został poprawnie przekierowany na first_hello

@pytest.mark.django_db
def test_user_register_view_1(client):
    url = reverse("user_registration")
    response = client.post(url, {
        "username": "user_1", 
        "email": "user_1@email.com", 
        "password1": "P@ss!word1234", # hasło musi spełniać standardy django template
        "password2": "P@ss!word1234",
    }, follow=True)

    user = User.objects.filter(username="user_1").first()

    assert user is not None
    assert user.email == "user_1@email.com"

    print(user.groups.all())
    assert user.groups.filter(name="new_hire_permissions").exists()

@pytest.mark.django_db
def test_user_register_view_2(client):
    url = reverse("user_registration")
    response = client.post(url, {
        "username": "user_1", 
        "email": "user_1@email.com", 
        "password1": "P@ss!word1234", # hasło musi spełniać standardy django template
        "password2": "P@ss!word1234",
    }, follow=True)

    user = User.objects.filter(username="user_1").first()

    assert user.email == "user_1@email.com"

@pytest.mark.django_db
def test_user_register_view_3(client):
    url = reverse("user_registration")
    response = client.post(url, {
        "username": "user_1", 
        "email": "user_1@email.com", 
        "password1": "P@ss!word1234", # hasło musi spełniać standardy django template
        "password2": "P@ss!word1234",
    }, follow=True)

    user = User.objects.filter(username="user_1").first()

    print(user.groups.all())
    assert user.groups.filter(name="new_hire_permissions").exists()

@pytest.mark.django_db
def test_account_create_view_1(client, django_user_model):
    # stworzenie użytkownika
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    
    # zalogowanie
    url = reverse("login")
    response = client.post(url, {"username": "user_1", "password": "pw1234"}, follow=True)
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance") #poprwane zalogowanie na trial balance

    # przejście do opcji add account
    url = reverse("user_form")
    response = client.get(url)
    assert response.status_code == 403 # odmowa dostępu
    status_message = "Please contact administrator if access should be added."
    assert status_message in response.content.decode()

@pytest.mark.django_db
def test_account_create_view_2(client, django_user_model):
    # stworzenie użytkownika
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    # dodanie go do grupy
    group, _ = Group.objects.get_or_create(name="all_permissions")
    user.groups.add(group)

    # zalogowanie
    url = reverse("login")
    response = client.post(url, {"username": "user_1", "password": "pw1234"}, follow=True)
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance") #poprwane zalogowanie na trial balance

    # przejście do opcji add account
    url = reverse("user_form")
    response = client.get(url, follow=True)
    assert response.status_code == 200 # przejście na stronę
    # assert response.request["PATH_INFO"] == reverse("trial_balance")
    # status_message = "Please contact administrator if access should be added."
    # assert status_message in response.content.decode()
