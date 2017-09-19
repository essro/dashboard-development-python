from django.test import TestCase
from django.core.urlresolvers import resolve
from dashboard.views import DashboardView

""" @file views.py
    @author Joseph Ravenna
    @date 20170430
    @description This file contains implementations of the testing classes
"""

# Create your tests here.
'''class SmokeTest(TestCase):

    def test_bad_maths(self):
        self.assertEqual(1+1, 3)'''


class DashboardTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/dashboard/')
        self.assertEqual(found.func, DashboardView)
