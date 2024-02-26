from django.contrib import admin
from .models import *

admin.site.register(UserProfile)
admin.site.register(UserQueries)
admin.site.register(TaskerAccounts)
admin.site.register(UserTransactions)
admin.site.register(UserNotifications)
admin.site.register(AccountPerformance)
