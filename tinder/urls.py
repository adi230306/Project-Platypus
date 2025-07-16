from django.contrib import admin
from django.urls import path, include
from perry.views import home

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('perry.urls')),

]
