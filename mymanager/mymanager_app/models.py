from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timezone


class UserQueries(models.Model):
    message = models.TextField(default='message')
    email = models.TextField(default='email')
    username = models.TextField(default='username')

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    firstname = models.TextField(default='firstname')
    lastname = models.TextField(default='lastname')
    username = models.TextField(default='username')
    email = models.TextField(default='email')
    paypalEmail = models.TextField(default='paypal_email')
    phoneNumber = models.TextField(default='phone number')
    country = models.TextField(default='country')
    dialCode = models.TextField(default='dial_code')
    balanceActual = models.IntegerField(default=0)
    balanceWeek = models.IntegerField(default=0)
    withdrawSuccess = models.IntegerField(default=0)
    withdrawPending = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class TaskerAccounts(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    accountEmail = models.TextField(default='eml')
    accountPassword = models.TextField(default='passwrd')
    accountBalanceHold = models.IntegerField(default=0)
    accountBalance = models.IntegerField(default=0)
    accountStatus = models.TextField(default='pending')
    dateCreated = models.DateTimeField(default=datetime.now(timezone.utc))

    def __str__(self):
        return self.accountEmail


class UserTransactions(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    transactionType = models.TextField(default='withdrawal')
    transactionId = models.TextField(default='transcid')
    transactionAmount = models.IntegerField(default=0)
    transactionStatus = models.TextField(default='pending')
    transactionDate = models.DateTimeField(default=datetime.now(timezone.utc))

    def __str__(self):
        return f'{self.user.username}| {self.transactionStatus} {self.transactionAmount}'


class UserNotifications(models.Model):
    notifiedUser = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    notificationSubject = models.TextField(default='subject')
    notificationMessage = models.TextField(default='content')
    notificationDate = models.DateTimeField(default=datetime.now(timezone.utc))

    def __str__(self):
        return f'{self.notifiedUser.username}| {self.notificationSubject}'


class AccountPerformance(models.Model):
    account = models.ForeignKey(TaskerAccounts, on_delete=models.CASCADE, null=True)
    amountGained = models.IntegerField(default=0)
    dateUpdated = models.DateTimeField(default=datetime.now(timezone.utc))

    def __str__(self):
        return f'{self.account.accountEmail}'
