import pytest
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse

from account.models import SimpleTrialBalance
from account.forms import *

# User with all accessess
@pytest.fixture
def user_all_permissions(django_user_model):
    user = django_user_model.objects.create_user(username="user_all_perm", password="pw1234")
    group, _ = Group.objects.get_or_create(name="all_permissions")

    perms = Permission.objects.all()
    group.permissions.set(perms)

    user.groups.add(group)

    return user

# User with basic accessess
@pytest.fixture
def user_basic_permissions(django_user_model):
    user = django_user_model.objects.create_user(username="user_basic_perm", password="pw5678")
    return user

# Testy widoków
@pytest.mark.django_db
def test_first_hello(client): # client to specjalne narzędzie do testowania widoków: 'do symulowania żądań HTTP'
    url = reverse("first_hello") #  reverse() zmienia nazwę widoku (taki jak jest w urls.py) na odpowiadający jej url, podajemy nazwę taka jaka jest w urls.py > name=
    response = client.get(url)

    assert response.status_code == 200 # sprawdza czy strona się ładuje
    assert "first_hello.html" in [x.name for x in response.templates] # sprawdza czy szablon 'first_hello.html' - czyli czy używamy odpowiedniego szablonu

@pytest.mark.django_db
def test_login_error_1(client, django_user_model):
    '''
    Próba zalogowania z błędnym hasłem.
    '''
    # stworzenie użytkownika
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    # dodanie go do grupy
    group, _ = Group.objects.get_or_create(name="all_permissions")
    user.groups.add(group)

    # zalogowanie
    url = reverse("login")
    response = client.post(url, {"username": "user_1", "password": "pw5555"}, follow=True) # błędne hasło
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("login") #poprwane zalogowanie na trial balance

    assert response.status_code == 200 # odmowa dostępu
    status_message = "Forgot password?"
    assert status_message in response.content.decode()

@pytest.mark.django_db
def test_login_error_2(client, django_user_model):
    '''
    Próba zalogowania z błędnym loginem.
    '''
    # stworzenie użytkownika
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    # dodanie go do grupy
    group, _ = Group.objects.get_or_create(name="all_permissions")
    user.groups.add(group)

    # zalogowanie
    url = reverse("login")
    response = client.post(url, {"username": "user_xyz", "password": "pw1234"}, follow=True) # błędny login
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("login") #poprwane zalogowanie na trial balance

    assert response.status_code == 200 # odmowa dostępu
    status_message = "Forgot password?"
    assert status_message in response.content.decode()

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

@pytest.mark.django_db
def test_account_create_view_3(client, django_user_model):
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

@pytest.mark.django_db
def test_account_create_view_4(client, django_user_model):
    '''
    Poprawne przejście na user form - bez wybranych opcji.
    '''
    # stworzenie użytkownika
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    # dodanie go do grupy
    group, _ = Group.objects.get_or_create(name="all_permissions")
    user.groups.add(group)

    # zalogowanie
    url = reverse("login")
    response = client.post(url, {"username": "user_1", "password": "pw1234"}, follow=True)
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance") #poprawne zalogowanie na trial balance

    # przejście na user_form - dostępne opcje 
    url = reverse("user_form")
    response = client.get(url)
    assert response.status_code == 200 # przejście na stronę
    assert response.request["PATH_INFO"] == reverse("user_form")

@pytest.mark.django_db
def test_account_create_view_5(client, django_user_model):
    '''
    Poprawne przejście na user form - opcja "Add account".
    '''
    # stworzenie użytkownika
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    # dodanie go do grupy
    group, _ = Group.objects.get_or_create(name="all_permissions")
    user.groups.add(group)

    # zalogowanie
    url = reverse("login")
    response = client.post(url, {"username": "user_1", "password": "pw1234"}, follow=True)
    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance") #poprawne zalogowanie na trial balance

    # przejście na user_form - dostępne opcje 
    url = reverse("user_form")
    response = client.post(reverse("user_form"), {
        'name': 'Add account', 
        'class': 'AccountCreateView',
    }, follow=True)

    assert response.status_code == 200 # przejście na stronę
    assert response.request["PATH_INFO"] == reverse("user_form")

    # upewniamy się że w htmlu jest "FORM:" - obecne tylko w tej templatce
    status_message = "FORM:"
    assert status_message in response.content.decode()

@pytest.mark.django_db
def test_account_create_view_6(client, django_user_model):
    '''
    Testowanie pełnego workflow.
    Użytkownik z wszystkimi uprawnieniami.
    Poprawne przejście na user form - opcja "Add account".
    Dodanie nowego konta.
    Przejście na widok SimpleTrialBalance.
    Upewnienie się, że konto zostało poprawnie zapisane.
    '''

    # stworzenie użytkownika
    user = django_user_model.objects.create_user(username="user_1", password="pw1234")
    # dodanie go do grupy
    group, _ = Group.objects.get_or_create(name="all_permissions")
    user.groups.add(group)

    # zalogowanie
    url = reverse("login")
    response = client.post(url, {
        "username": "user_1", 
        "password": "pw1234"
    }, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance") #poprawne zalogowanie na trial balance

    # przejście na user_form - wybranie opcji AccountCreateView 
    url = reverse("user_form")
    response = client.post(reverse("user_form"), {
        'name': 'Add account', 
        'class': 'AccountCreateView',
    }, follow=True)

    assert response.status_code == 200 # przejście na stronę
    assert response.request["PATH_INFO"] == reverse("user_form")

    # upewniamy się że w htmlu jest "FORM:" - obecne tylko w tej templatce
    status_message = "FORM:"
    assert status_message in response.content.decode()

    response = client.post(reverse("user_form"), {
        "account_name": "account_1",
        "account_number": "30011",
        "opening_balance": 0,
        "activity": 100,
    }, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance")

    # upewniamy się że w htmlu jest "Simple Trial Balance" - oznacza to poprawny powrót na stronę główną
    status_message = "Simple Trial Balance"
    assert status_message in response.content.decode()

    # upewniamy się, że konto zostało poprawnie stworzone
    db_contents = str(SimpleTrialBalance.objects.all())
    new_account = "[account_1 | 30011 | 0 | 100 | 100]"
    assert new_account in db_contents

@pytest.mark.django_db
def test_account_create_view_7(client, django_user_model, user_all_permissions):
    # zalogowanie użytkownika do trial balance
    # client.login(username="user_all_perm", password="pw1234")
    client.force_login(user_all_permissions)

    url = reverse("trial_balance")
    response = client.get(url, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance") #poprawne zalogowanie na trial balance

@pytest.mark.django_db
def test_account_create_view_8(client, django_user_model, user_all_permissions):
    # zalogowanie użytkownika do form - dodawanie konta
    client.force_login(user_all_permissions)

    url = reverse("user_form")
    response = client.get(url, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("user_form") #poprawne zalogowanie na user_form

@pytest.mark.django_db
def test_account_create_view_9(client, user_all_permissions):
    """
    Sprawdzamy czy poprawnie dodajemy konto
    """
    client.force_login(user_all_permissions)

    client.post(reverse("user_form"), {
        "account_name": "account_1",
        "account_number": "30011",
        "opening_balance": 0,
        "activity": 100,
    }, follow=True)

    response = client.get(reverse("trial_balance"))
    assert "Simple Trial Balance" in response.content.decode()

    db_contents = str(SimpleTrialBalance.objects.all())
    new_account = "[account_1 | 30011 | 0 | 100 | 100]"
    assert new_account in db_contents

@pytest.mark.django_db
def test_account_delete(client, user_all_permissions):
    """
    Testujemy usuwanie konta.
    """
    client.force_login(user_all_permissions)

    #tworzymy dwa konta
    account1 = SimpleTrialBalance.objects.create(account_name="account1", account_number=100100, opening_balance=0, activity=0)
    account2 = SimpleTrialBalance.objects.create(account_name="account2", account_number=200200, opening_balance=0, activity=0)

    # wyświetlenie delete_account
    response = client.get(reverse("delete_account"))
    assert response.status_code == 200
    assert "Select accounts to delete" in response.content.decode()

    # usunięcie jednego z kont
    response = client.post(reverse("delete_account"), {
        "accounts_to_delete": [account1.id] 
    }, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance")

    # czy konto_1 jest usunięte a konto_2 nadal istnieje
    accounts = SimpleTrialBalance.objects.all()
    assert account1 not in accounts
    assert account2 in accounts

@pytest.mark.django_db
def test_account_update(client, user_all_permissions):
    """
    Testujemy zmienianie konta.
    """
    client.force_login(user_all_permissions)

    #tworzymy konto
    account1 = SimpleTrialBalance.objects.create(account_name="account1", account_number=100100, opening_balance=0, activity=0)
    
    # wyświetlenie update_account
    update_account = reverse("update_account", args=[account1.id])
    response = client.get(update_account)
    assert response.status_code == 200
    assert "Update account:" in response.content.decode()

    # wprowadzamy zmiany w koncie
    response = client.post((update_account), {
        "account_name": account1.account_name,
        "account_number": account1.account_number,
        "opening_balance": account1.opening_balance,
        "activity": 100, # zmieniamy tylko activity
    }, follow=True)

    assert response.status_code == 200
    assert response.request["PATH_INFO"] == reverse("trial_balance")

    db_contents = str(SimpleTrialBalance.objects.all())
    new_account = "[account1 | 100100 | 0 | 100 | 100]"
    assert new_account in db_contents
