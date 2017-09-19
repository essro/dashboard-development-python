from django.db import models

""" @file models.py
    @author Justin Chambers
    @author Joseph Ravenna
    @date 20170430
    @description This file contains implementations of the Django-specific Presentation and UI classes
    @description NOTE: These classes are not used in the V1 prototype but are listed so that they can be fully
                        implemented in later releases
"""


class Page(models.Model):
    path = models.CharField(max_length=50)
    views = models.IntegerField()

    def __str__(self):
        return self.path


class Source(models.Model):
    name = models.CharField(max_length=30)
    path = models.CharField(max_length=50)
    views = models.IntegerField()

    def __str__(self):
        return self.name

    def Meta(self):
        unique_together = [
            ("name", "path"),
        ]


class SummaryDataTable(models.Model):
    page_path = models.CharField(max_length=30)
    raw_delta = models.IntegerField
    percent_delta = models.FloatField

    def __str__(self):
        return self.page_path + "," + self.raw_delta

    def Meta(self):
        ordering = ('raw_delta', 'percent_delta',)


class UserPreferences(models.Model):
    username = models.CharField(max_length=30)
    user_id = models.CharField(max_length=20)
    client_list = [models.CharField(max_length=30)]
    current_start_date = models.IntegerField
    current_end_date = models.IntegerField
    prev_start_date = models.IntegerField
    prev_end_date = models.IntegerField


class Element:
    def __init__(self,
                 name,
                 rank,
                 size,
                 components):
        self.name = name
        self.rank = rank
        self.size = size
        self.components = components

    def get_name(self):
        return self.name

    def get_rank(self):
        return self.rank

    def get_size(self):
        return self.size

    def get_components(self):
        return self.components


class Component:
    def __init__(self,
                 chart_type,
                 icon_location,
                 data_summary,
                 data_detail):
        self.chart_type = chart_type
        self.icon = icon_location
        self.data_summary = data_summary
        self.data_detail = data_detail

    def get_chart_type(self):
        return self.chart_type

    def get_icon(self):
        return self.icon

    def get_summary(self):
        return self.data_summary

    def get_detail(self):
        return self.data_detail


class Dashboard:
    def __init__(self,
                 id_usr,
                 id_session):
        self.usr = id_usr
        self.session = id_session
        self.elements = {}

    def get_user_id(self):
        return self.usr

    def get_session_id(self):
        return self.session
