from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from datetime import datetime, timedelta
from django.http import JsonResponse
import time
import random
import string


def generate_transaction_id():
    # Get current timestamp
    timestamp = int(time.time())

    # Generate random characters
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    # Combine timestamp and random characters
    transaction_id = f'{timestamp}{random_chars}'

    return transaction_id


def home(request):
    return render(request, 'home.html')


def contact(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        if email and message:
            messages.success(request,
                             'Thank you for your feedback. Your message has been'
                             ' received.Check your email inbox for our reply')

            username = 'anonymous'
            if request.user.is_authenticated:
                username = request.user.username

            uq = UserQueries(
                message=message,
                email=email,
                username=username,
            )
            uq.save()

    return render(request, 'contact.html')


def get_week_dates():
    today = datetime.today()
    days_to_subtract = (today.weekday()) % 7
    monday = today - timedelta(days=days_to_subtract)
    sunday = monday + timedelta(days=6)
    week_dates = []
    current_date = monday
    while current_date <= sunday:
        week_dates.append(current_date)
        current_date += timedelta(days=1)

    return week_dates


def getAccntPerformance(account):
    val = []
    for i in get_week_dates():
        ap = AccountPerformance.objects.filter(account=account).order_by('-pk')
        if len(ap) == 0:
            for j in range(7):
                val.append(0)
            break
        else:
            available = False
            for r in ap:
                if r.dateUpdated.day == i.day and r.dateUpdated.month == i.month:
                    val.append(r.amountGained)
                    available = True
                    break
            if not available:
                val.append(0)

    return val


@csrf_exempt
def getPerformance(request):
    resultType = ''
    val = ''
    isActive = ''
    accntBal = 0
    if request.method == 'POST':
        accnt = request.POST.get('selectedAccount', '')
        if accnt:
            accountDetails = TaskerAccounts.objects.filter(accountEmail=accnt).first()
            if accountDetails:
                val = getAccntPerformance(accountDetails)
                accntBal = accountDetails.accountBalanceHold
                isActive = accountDetails.accountStatus
                resultType = 'success'

    return JsonResponse({'accntBal': accntBal, 'values': val, 'resultType': resultType, 'isActive': isActive})


@csrf_exempt
def withdrawBalance(request):
    message = ''
    resultType = ''
    new_bal = ''
    if request.method == 'POST':
        amt = request.POST.get('with_amt', '')
        if amt:
            up = UserProfile.objects.filter(username=request.user.username).first()
            if up:
                accntbal = up.balanceActual
                if accntbal >= int(amt):
                    up.balanceActual -= int(amt)
                    up.withdrawPending += int(amt)
                    up.save()
                    message = 'Withdrawal request submitted successfully.'
                    resultType = 'success'
                    new_bal = accntbal - int(amt)

                    ut = UserTransactions(
                        user=up,
                        transactionAmount=int(amt),
                        transactionId=generate_transaction_id()
                    )
                    ut.save()
                    un = UserNotifications(
                        notifiedUser=up,
                        notificationSubject='WITHDRAWAL REQUEST RECEIVED',
                        notificationMessage=f'Your request to withdraw ${amt} has been received and is being processed.'
                                            f' Your new account balance now stands at ${new_bal}'

                    )
                    un.save()

    return JsonResponse({'newBal': new_bal, 'resultType': resultType, 'message': message})


def dashboard(request):
    up = UserProfile.objects.filter(username=request.user.username).first()
    current_date = datetime.now()

    start_of_week = current_date - timedelta(days=current_date.weekday())

    end_of_week = start_of_week + timedelta(days=6)
    st = f"{start_of_week.day} {start_of_week.strftime('%b')}"
    en = f"{end_of_week.day} {end_of_week.strftime('%b')}"

    lastAccnt = TaskerAccounts.objects.filter(owner=up).last()
    context = {
        'profile': up,
        'myAccounts': TaskerAccounts.objects.filter(owner=up).order_by('-pk'),
        'lastAccountPerformance': getAccntPerformance(lastAccnt),
        'lastAccount': lastAccnt,
        'week': f'{st} - {en}',
        'transactions': UserTransactions.objects.filter(user=up).order_by('-pk'),
        'notifications': UserNotifications.objects.filter(notifiedUser=up).order_by('-pk'),

    }

    return render(request, 'dashboard.html', context)


@csrf_exempt
def changePaypalEmail(request):
    message = 'Failed to update PayPal. Try again later'
    pp_email = ''
    resultType = ''
    if request.method == 'POST':
        pp_email = request.POST.get('paypal_email', '')
        if pp_email:
            up = UserProfile.objects.filter(username=request.user.username).first()
            if up:
                up.paypalEmail = pp_email
                up.save()
                message = f"Your Paypal email has been successfully updated to {pp_email}"
                resultType = 'success'
                un = UserNotifications(
                    notifiedUser=up,
                    notificationSubject='PAYPAL EMAIL CHANGED',
                    notificationMessage=f'Your paypal email was successfully updated to {pp_email}.'
                                        f' If this was not you, kindly contact us as soon as possible.'

                )
                un.save()
    return JsonResponse({'message': message, 'email': pp_email, 'resultType': resultType})


@csrf_exempt
def uploadRemoAccount(request):
    message = 'Failed to upload account. Try again later'
    resultType = ''
    if request.method == 'POST':
        remo_email = request.POST.get('remo_email', '')
        remo_pass = request.POST.get('remo_pass', '')
        if remo_email:
            upl = TaskerAccounts.objects.filter(accountEmail=remo_email).first()
            if upl:
                message = 'An account with the provided details already exists.'
            else:
                up = UserProfile.objects.filter(username=request.user.username).first()
                if up:
                    ta = TaskerAccounts(
                        owner=up,
                        accountEmail=remo_email,
                        accountPassword=remo_pass,
                        accountStatus='pending')
                    ta.save()
                    message = 'Account uploaded successfully and is under review.'

                    resultType = 'success'
                    un = UserNotifications(
                        notifiedUser=up,
                        notificationSubject='ACCOUNT UPLOADED SUCCESSFULLY',
                        notificationMessage=f'You have successfully added an account {remo_email} under your profile for us to manage.'
                                            f' We will review and set up the account accordingly. Once this is successful,'
                                            f' we will allocate taskers after which you will be able to earn from this account.'

                    )
                    un.save()

    return JsonResponse({'message': message, 'resultType': resultType})


@csrf_exempt
def accountPerformance(request):
    resultType = ''
    withdrawn = 0
    currentBal = 0
    weekAccum = 0
    if request.method == 'POST':
        remo_email = request.POST.get('remo_email', '')
        if remo_email:
            upl = TaskerAccounts.objects.filter(accountEmail=remo_email).first()
            if upl:
                up = UserProfile.objects.filter(username=request.user.username).first()
                if up:
                    resultType = 'success'

    return JsonResponse(
        {'withdrawn': withdrawn,
         'resultType': resultType,
         'currentBal': currentBal,
         'weekAccum': weekAccum,
         })


def loginP(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')
    return render(request, 'login.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        firstname = request.POST.get('fname', '')
        lastname = request.POST.get('lname', '')
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        paypal_email = request.POST.get('p_email', '')
        phone_number = request.POST.get('phone_number', '')
        country = request.POST.get('country', '')
        dial_code = request.POST.get('dial_code', '')
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            messages.error(request, 'Username or email already taken')
        else:
            up = UserProfile(
                firstname=firstname,
                lastname=lastname,
                username=username,
                email=email,
                paypalEmail=paypal_email,
                phoneNumber=phone_number,
                country=country,
                dialCode=dial_code,
            )
            User.objects.create_user(
                username=username,
                password=password,
                email=email,
            )
            up.save()
            return redirect('login')

    return render(request, 'register.html')


def logoutP(request):
    logout(request)
    return render(request, 'home.html')
