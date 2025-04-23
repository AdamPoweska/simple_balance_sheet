import pytest
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse

from account.models import SimpleTrialBalance
from account.forms import *

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
