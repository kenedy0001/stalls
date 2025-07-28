"""
URL configuration for rooms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from room.views import dashboard,book_room,  signup_view, login_view, logout_view, send_verification_code, verify_account, reset_password
from testapi.views import contact_list,contact_create,contact_update,contact_delete
urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('',dashboard, name='dashboard'),
    path('book/room/<int:room_id>/', book_room, name='book_room'), 
    path('logout/', logout_view, name='logout'),
    path('send-code/', send_verification_code, name='send_code'),
    path('verify/', verify_account, name='verify_account'),
    path('reset-password/', reset_password, name='reset_password'),
    path('', contact_list, name='contact_list'),
    path('create/', contact_create, name='contact_create'),
    path('update/<int:pk>/', contact_update, name='contact_update'),
    path('delete/<int:pk>/', contact_delete, name='contact_delete'),
]