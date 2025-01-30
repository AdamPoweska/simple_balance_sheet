from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import SimpleTrialBalance

# wokorzystać potem jako bazę do tworzenia nowego użytkownika
class NameForm(forms.Form): 
    your_name = forms.CharField(label='Your Name', max_length=100)


class TrialBalanceForm(forms.ModelForm):
    class Meta:
        model = SimpleTrialBalance
        exclude = ['closing_balance'] # wykluczenie closing_balance w formularzu, użytkownik nie będzie miał do niego dostępu i przypadkiem go nie nadpisze

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user.groups.filter(name='new_hire_permissions').exists():
            # self.fields['account_name', 'account_number', 'opening_balance'].widget = forms.HiddenInput() # ukrycie określonych pól jeśli użytkownik jest w grupie 'new_hire_permissions"
            self.fields['account_name'].disabled = True # w ten sposób możemy zablokować pole do edycji ale jest odczyt
            self.fields['account_number'].disabled = True # nie możemy przekazać wszytkiego naraz bo django nie obłuży dostępu do wielu pól jednocześnie w liście
            self.fields['opening_balance'].disabled = True

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AccountDeleteForm(forms.Form):
    accounts_to_delete = forms.ModelMultipleChoiceField(
        queryset=SimpleTrialBalance.objects.all(),
        widget=forms.CheckboxSelectMultiple, # do wyboru wielu opcji
        required=False # nie trzeba nic zaznaczać, wtedy wrócimy do listy kont bez usuwania czegokolwiek
    )


class AccountUpdateSelect(forms.Form):
    account_update_select = forms.ModelChoiceField(
        queryset=SimpleTrialBalance.objects.all(),
        widget=forms.RadioSelect, # do wyboru jednej opcji w liście, bez tego pojawi się lista rozwijana
        required=True
    )