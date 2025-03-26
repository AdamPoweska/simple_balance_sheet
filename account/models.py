# Create your models here.
from django.db import models

class SimpleTrialBalance(models.Model):
    account_name = models.CharField(max_length=30)
    account_number = models.IntegerField()
    opening_balance = models.IntegerField()
    activity = models.IntegerField()
    closing_balance = models.IntegerField(editable=False) # (1) editable=False - uniemożliwa ręczne wprowadzanie pola, (2) to pole zostanie excludowane na poziomie formularza

    def save(self, *args, **kwargs): # nadpisanie metody save, spowoduje zapisanie closing_blanace w bazie danych
        self.closing_balance = self.opening_balance + self.activity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.account_name} | {self.account_number}"
    
    def __repr__(self):
        return f"{self.account_name} | {self.account_number} | {self.opening_balance} | {self.activity} | {self.closing_balance}"
