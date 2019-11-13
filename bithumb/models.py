from django.db import models

# add import
from django.conf import settings
from django.utils import timezone


# User TABLE
class ProgramUser(models.Model):
    userId = models.CharField(max_length=100, primary_key=True)
    userPassword = models.CharField(max_length=100)
    userName = models.CharField(max_length=100)
    userPhone = models.CharField(max_length=100)
    mySchedulerId = models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=5)

    def __str__(self):
        return str(self.userId)

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
    userId = models.ForeignKey(ProgramUser,null=True, on_delete=models.CASCADE)
    schedulerId = models.CharField(max_length=300, blank=True)
    ticker = models.CharField(max_length=100)
    tradeInfo = models.CharField(max_length=100)
    tradeCount = models.FloatField(default=0)
    tradePrice = models.IntegerField(default = 0)
    tradeTime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.userId)

class TradeScheduler(models.Model):
    userId = models.ForeignKey(ProgramUser, null=True, on_delete=models.CASCADE)
    schedulerId = models.CharField(max_length=300, blank=True)
    startTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(default=timezone.now)
    ticker = models.CharField(max_length=100)
    startMoney = models.IntegerField(default=0)
    startTickerQuantity = models.FloatField(default=0)
    endMoney = models.IntegerField(default=0)
    endTickerQuantity = models.FloatField(default=0)
    tradeYield = models.FloatField(default=0)

    def __str__(self):
        return str(self.schedulerId)


class Wallet(models.Model):
    userId = models.ForeignKey(ProgramUser, null=True, on_delete=models.CASCADE)
    monney = models.IntegerField(default=0)
    ticker = models.CharField(max_length=100, null=True)
    tickerQuantity = models.FloatField(default=0)

    def __str__(self):
        return str(self.userId)


class APILicense(models.Model):
    userId = models.ForeignKey(ProgramUser, null=True, on_delete=models.CASCADE)
    bit_publicKey =  models.CharField(max_length=500)
    bit_privateKey = models.CharField(max_length=500)
    tw_publicKey =  models.CharField(max_length=500)
    tw_privateKey = models.CharField(max_length=500)
    tw_number = models.CharField(max_length=500)
    nv_publicKey = models.CharField(max_length=500)
    nv_privateKey = models.CharField(max_length=500)

    def __str__(self):
        return str(self.userId)