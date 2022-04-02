from django.urls import path, include

urlpatterns = [
    path('', include('sso.urls_user_sign')),

]