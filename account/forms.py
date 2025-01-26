from django import forms
from .models import SimpleTrialBalance

# wokorzystać potem jako bazę do tworzenia nowego użytkownika
class NameForm(forms.Form): 
    your_name = forms.CharField(label='Your Name', max_length=100)

class TrialBalanceForm(forms.ModelForm):
    class Meta:
        model = SimpleTrialBalance
        exclude = ['closing_balance'] # wykluczenie closing_balance w formularzu, użytkownik nie będzie miał do niego dostępu i przypadkiem go nie nadpisze

