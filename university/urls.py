from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('registration.urls', namespace='registration')),
    path('', include('equations.urls', namespace='equations')),

]

handler400 = 'error_handling.views.handler400'
handler403 = 'error_handling.views.handler403'
handler404 = 'error_handling.views.handler404'
handler500 = 'error_handling.views.handler500'
