"""ScholarDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from CreateQ import views as CreateQ_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^new/',CreateQ_view.new_survey,name = 'home'),
    url(r'^list/',CreateQ_view.list_survey,name = 'list'),
    url(r'^list/json',CreateQ_view.list_survey_json,name = 'list_json')
]
