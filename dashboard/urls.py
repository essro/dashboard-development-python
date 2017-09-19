from django.conf.urls import url
from dashboard.views import DashboardView

""" @file urls.py
    @author Justin Chambers
    @author Joseph Ravenna
    @date 20170430
    @description This file contains the dashboard app url routing patterns used by the Django framework
"""

urlpatterns = [
    url(r'^$', DashboardView.as_view(), name='dashboard'),
]
