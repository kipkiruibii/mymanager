from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('manager_admin/', admin.site.urls),
    path('', include('mymanager_app.urls'))
]
