from django.db import models

# add import
from django.conf import settings
from django.utils import timezone


# User TABLE
class ProgramUser(models.Model):
    userId = models.CharField(max_length=100, primary_key=True)
    userPassword = models.CharField(max_length=100)
    userName = models.CharField(max_length=50)
    userPhone = models.CharField(max_length=100)
    publicKey = models.CharField(max_length=32)
    privateKey = models.CharField(max_length=32)
    status = models.CharField(max_length=5)

    def __str__(self):
        return self.userId

    def setUserStatus(self):
        print("setUserStatus")
        print(self.userId)
        print(self.userName)

        if self.status == 'N':
            self.status = 'Y'
            self.save()
        elif self.status == 'Y':
            self.status = 'N'
            self.save()

class TradeHistory(models.Model):
    TradeUserId = models.ForeignKey(ProgramUser,null=True, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=50)
    tradeInfo = models.CharField(max_length=50)
    tradePrice = models.IntegerField(default = 0)
    tradeTime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.TradeUserId
