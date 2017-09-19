'''
file: analytics.py
author: Husain Tazarvi
created: Feb 5, 2017
'''

from dashboard.API.query_essentials import query_basic as api
import os.path
import pandas as pd
import numpy as np
import logging


class Analytics(object):
    def __init__(self):
        super(Analytics, self).__init__()
        # UN-COMMENT TO DISABLE LOGGING
        #logging.disable(logging.CRITICAL)

        formatter = logging.Formatter('%(asctime)s <%(funcName)s>: %(message)s')

        self.activity_log = logging.getLogger('ACTIVITY')
        self.activity_log.setLevel(logging.DEBUG)
        #self.activity_handler = logging.FileHandler(os.path.dirname(os.path.abspath(__file__)) + '/activity.log')
        ACTIVITY_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'logs', 'activity.log'))
        self.activity_handler = logging.FileHandler(ACTIVITY_LOG_PATH)
        self.activity_handler.setLevel(logging.DEBUG)
        self.activity_handler.setFormatter(formatter)
        self.activity_log.addHandler(self.activity_handler)

        self.activity_log.debug('Initializing Analytics object')

        # CURRENT & PREVIOUS TIME PERIODS
        # YYYY-MM-DD, or as a relative date (today, yesterday, or NdaysAgo where N is a positive integer)
        self.period_current = {'START': '31daysAgo', 'END': 'yesterday'}
        self.period_previous = {'START': '61daysAgo', 'END': '31daysAgo'}

        # ANALYSIS RESTRICTIONS
        self.restrictions = {"threshold_%": 18, "top_n": 5}

        # TOP_N TRAFFIC SPIKES/DROPS SUMMARY
        # Format (Index = ga:pagePath):
        # |  ga:pagePath   |   ga:pageviews_prev   |   ga:pageviews_prev   |   Delta   |   Delta_%   |
        self.top_n_spikes = None
        self.top_n_drops = None

        # TOP_N TRAFFIC SPIKES/DROPS DETAIL
        # Format (Index = ga:pagePath, ga:source):
        # |  ga:pagePath   |    ga:source  |   ga:pageviews_prev   |   ga:pageviews_prev   |   Delta   |
        self.top_n_spikes_src = None
        self.top_n_drops_src = None

        # AVERAGE SITE BOUNCE RATE
        self.bounce_rate_mean = None

        # TOP N HIGHEST/LOWEST BOUNCE RATES SUMMARY
        # Format (Index = ga:pagePath):
        # | ga:pagePath | ga:bounces | ga:sessions | ga:goalCompletionsAll | bounceRate | goalConversionRateAll | fromAvrg% |
        self.highest_n_br = None
        self.lowest_n_br = None

        # TOP N HIGHEST/LOWEST BOUNCE RATES DETAIL
        # Format (Index = ga:pagePath, ga:source):
        # |ga:pagePath | ga:source | ga:bounces	| ga:sessions | ga:goalCompletionsAll | bounceRate | goalConversionRateAll | fromAvrg% |
        self.highest_n_br_src = None
        self.lowest_n_br_src = None

        # TRAFFIC SOURCE SUMMARY
        # Format (Index = category):
        # | category | ga:sessions_prev | ga:goalCompletionsAll_prev | ga:sessions_curr | ga:goalCompletionsAll_curr | sessionsChangeRate | goalCompletionsChangeRate | goalConversionRateAll_curr | goalConversionRateAll_prev
        self.srcs_summary = None

        # TRAFFIC SOURCE DETAIL
        # Format (Index = category, source):
        # | category | source | ga:sessions_prev | ga:goalCompletionsAll_prev | ga:sessions_curr | ga:goalCompletionsAll_curr | sessionsChangeRate | goalCompletionsChangeRate | goalConversionRateAll_curr | goalConversionRateAll_prev
        self.srcs_detail = None


        # EXECUTIVE OVERVIEW
        # -VISITORS
        self.exec_ov_visitors_delta = None
        self.exec_ov_visitors_delta_perc = None
        # -VISITS
        self.exec_ov_visits_delta = None
        self.exec_ov_visits_delta_perc = None
        #  -PAGEVIEWS
        self.exec_ov_pageviews_delta = None
        self.exec_ov_pageviews_delta_perc = None
        #  -GOAL COMPLETIONS
        self.exec_ov_goals_delta = None
        self.exec_ov_goals_delta_perc = None
        #  -EVENTS
        self.exec_ov_events_delta = None
        self.exec_ov_events_delta_perc = None

        #self.csv_directory = os.path.dirname(os.path.abspath(__file__)) + '/static/csv/'
        self.csv_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'csv'))

    def get_ga_api_context(self, period, dimensions, metrics, sort_key = None, filters = None):
        '''
        Generates a context to query the google analytics API
        See google's Core Reporting API - Common Queries for more details
        https://developers.google.com/analytics/devguides/reporting/core/v3/common-queries

        :param period: The period for the current context
        Structure: A dictionary with start date (key: START) and end date (key: END)
        Date Formats: YYYY-MM-DD, or as a relative date (today, yesterday, or NdaysAgo where N is a positive integer)

        :param dimensions: A string of comma separated dimensions to include in the query
        See google's Dimensions and Metrics Explorer for more detail:
        https://developers.google.com/analytics/devguides/reporting/core/dimsmets

        :param metrics: A string of comma separated metrics to include in the query
        See google's Dimensions and Metrics Explorer for more detail:
        https://developers.google.com/analytics/devguides/reporting/core/dimsmets

        :param sort_key: A string defining the sort parameter (metric/dimension) for the query
        To sort in descending order place a '-' in front of the metric/dimension name

        :param filters: A string of filters to apply to the query

        :return: A dictionary context to be used for a query to google analytics API
        '''
        svc_account = api.get_svc_account()
        creds_path = api.get_client_credentials()
        return {
            #"context_name": "top Spike",
            "api_name": "analytics",
            "api_version": "v3",
            "scope": "https://www.googleapis.com/auth/analytics.readonly",
            "svc_account_email": svc_account,
            "key_file_location": creds_path,
            "st_date": period['START'],
            "end_date": period['END'],
            "api_metric": metrics,
            "api_dimension": dimensions,
            "sort_key": sort_key,
            "api_filter": filters
        }

    def gen_tts_ttd(self):
        '''
        Generates TOP_N TRAFFIC SPIKES/DROPS summary and detail data frames.
        '''
        self.activity_log.debug('Generating tts & ttd summary data')

        #call = d3a.get_client_api_call_context()
        context = self.get_ga_api_context(period = self.period_current,
                                          dimensions = 'ga:pagePath, ga:hostname',
                                          metrics = 'ga:pageviews',
                                          sort_key = '-ga:pageviews'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        page_views_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        page_views_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Append hostname to pagePath
        page_views_previous['ga:pagePath'] = page_views_previous['ga:hostname'].map(str) \
                                             + page_views_previous['ga:pagePath']
        page_views_current['ga:pagePath'] = page_views_current['ga:hostname'].map(str) \
                                            + page_views_current['ga:pagePath']

        # Drop hostname column
        page_views_previous.drop('ga:hostname', axis=1, inplace=True)
        page_views_current.drop('ga:hostname', axis=1, inplace=True)

        # Outer merge: Everything from both periods (previous first)
        page_views_full = page_views_previous.merge(right=page_views_current,
                                                    how='outer',
                                                    on=['ga:pagePath'],
                                                    suffixes=['_prev', '_curr'])

        # Replace all NaN values with zero
        # and Convert page views to numeric
        #page_views_full.fillna(value=0, axis=0, inplace=True)
        page_views_full[['ga:pageviews_prev', 'ga:pageviews_curr']] = page_views_full[
            ['ga:pageviews_prev', 'ga:pageviews_curr']].fillna(0.0).astype(int)

        # Filter infusion soft path (remove everything after ?inf_contact or &inf_contact_key in path
        page_views_full['ga:pagePath'].replace(r"\?inf_contact_key.*|&inf_contact_key.*", r"", regex = True, inplace = True)

        # Sum up unique paths into one row
        page_views_full = page_views_full.groupby('ga:pagePath', as_index=False, sort=False).sum()

        # Add the delta value from prev to curr page views
        page_views_full.loc[:, 'Delta'] = page_views_full['ga:pageviews_curr'] - page_views_full['ga:pageviews_prev']

        # Sort by delta values
        page_views_full.sort_values(['Delta'], ascending=False, inplace=True)

        # Add delta percentage rounded to two dec places
        page_views_full.loc[:, 'Delta_%'] = round((page_views_full['Delta'] / page_views_full['ga:pageviews_prev']) * 100, 2)

        # Replace inf (result of division by 0) with 100
        page_views_full.loc[:, 'Delta_%'] = page_views_full['Delta_%'].replace(np.inf, 100)

        # Filter out by all delta_% less than threshold
        page_views_full = page_views_full[(abs(page_views_full['Delta_%']) >= self.restrictions["threshold_%"])]

        # Filter out topN spikes and topN drops
        self.top_n_spikes = page_views_full.iloc[0:self.restrictions['top_n']].copy()
        self.top_n_drops = page_views_full.iloc[-self.restrictions['top_n']:].copy()

        # Convert negative percentages to positive
        self.top_n_drops.loc[:, 'Delta_%'] = self.top_n_drops['Delta_%'].abs()

        # Re-arrange topN drops to sort by ascending
        self.top_n_drops = self.top_n_drops.sort_values(['Delta'], ascending=True)

        # Set indices
        self.top_n_spikes.set_index(['ga:pagePath'], inplace=True)
        self.top_n_drops.set_index(['ga:pagePath'], inplace=True)

        #################### DETAILED VIEW ####################
        self.activity_log.debug('Generating tts & ttd detailed data')

        # Get page paths for spikes and drops
        spike_paths = self.top_n_spikes.index.tolist()
        drop_paths = self.top_n_drops.index.tolist()

        # Update call for page views by source: current period
        context["st_date"] = self.period_current['START']
        context["end_date"] = self.period_current['END']
        context["api_dimension"] = "ga:pagePath, ga:hostname, ga:source"
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        page_views_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for previous period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']

        values = api.get_results(context)

        # Get data for second period
        page_views_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Append hostname to pagePath
        page_views_previous['ga:pagePath'] = page_views_previous['ga:hostname'].map(str) + page_views_previous['ga:pagePath']
        page_views_current['ga:pagePath'] = page_views_current['ga:hostname'].map(str) + page_views_current['ga:pagePath']

        # Drop hostname column
        page_views_previous.drop('ga:hostname', axis=1, inplace=True)
        page_views_current.drop('ga:hostname', axis=1, inplace=True)

        # Outer merge: Everything from both periods
        page_views_full = page_views_previous.merge(right=page_views_current,
                                                    how='outer',
                                                    on=['ga:pagePath', 'ga:source'],
                                                    suffixes=['_prev', '_curr'], sort=True)

        # Replace all NaN values with zero
        # and Convert page views to numeric
        #page_views_full.fillna(value=0, axis=0, inplace=True)
        page_views_full[['ga:pageviews_prev', 'ga:pageviews_curr']] = page_views_full[
            ['ga:pageviews_prev', 'ga:pageviews_curr']].fillna(0.0).astype(int)

        # Filter infusion soft path (remove everything after ?inf_contact or &inf_contact_key in path
        page_views_full['ga:pagePath'].replace(r"\?inf_contact_key.*|&inf_contact_key.*", r"", regex = True, inplace = True)

        # Sum up unique paths into one row
        page_views_full = page_views_full.groupby(by=['ga:pagePath', 'ga:source'], as_index=False).sum()

        self.top_n_spikes_src = page_views_full[page_views_full['ga:pagePath'].isin(spike_paths)].copy()
        self.top_n_drops_src = page_views_full[page_views_full['ga:pagePath'].isin(drop_paths)].copy()

        # Add the delta value from prev to curr page views
        self.top_n_spikes_src.loc[:, 'Delta'] = self.top_n_spikes_src['ga:pageviews_curr'] - self.top_n_spikes_src[
            'ga:pageviews_prev']
        self.top_n_drops_src.loc[:, 'Delta'] = self.top_n_drops_src['ga:pageviews_curr'] - self.top_n_drops_src[
            'ga:pageviews_prev']

        # Set indices
        self.top_n_spikes_src.set_index(['ga:pagePath', 'ga:source'], inplace=True)
        self.top_n_drops_src.set_index(['ga:pagePath', 'ga:source'], inplace=True)

        '''
        # Remove multi-Index on (path,src), replace with only path index
        top_n_spikes_src.reset_index(inplace=True)
        top_n_spikes_src.set_index(['ga:pagePath'], inplace=True)
        top_n_drops_src.reset_index(inplace=True)
        top_n_drops_src.set_index(['ga:pagePath'], inplace=True)
        '''


    def gen_bouncerate(self):
        '''
        Generates AVERAGE SITE BOUNCE RATE and TOP N HIGHEST/LOWEST BOUNCE RATES summary and detail data frames
        '''
        self.activity_log.debug('Generating bouncerate above avrg paths')

        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:pagePath, ga:hostname',
                                          metrics='ga:pageviews',
                                          sort_key='-ga:pageviews'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        #################### PAGES ABOVE SITE AVRG PAGE VIEWS ####################

        # Get data for current period
        page_views_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Append hostname to pagePath
        page_views_current['ga:pagePath']=page_views_current['ga:hostname'].map(str) + page_views_current['ga:pagePath']

        # Drop hostname column
        page_views_current.drop('ga:hostname', axis=1, inplace=True)

        # Replace all NaN values with zero
        # and Convert page views to numeric
        #page_views_current.fillna(0, inplace=True)
        page_views_current['ga:pageviews'] = page_views_current['ga:pageviews'].fillna(0.0).astype(int)

        # Filter infusion soft path (remove everything after ?inf_contact or &inf_contact_key in path
        page_views_current['ga:pagePath'].replace(r"\?inf_contact_key.*|&inf_contact_key.*", r"", regex=True,
                                                    inplace=True)

        # Set indices
        #page_views_current.set_index(['ga:pagePath'], inplace=True)

        # Sum up unique paths into one row
        page_views_current = page_views_current.groupby('ga:pagePath', as_index=False, sort=False).sum()

        # Computer site average page views
        #avrg_pageviews = page_views_current.loc[:, 'ga:pageviews'].abs().mean()
        avrg_pageviews = page_views_current['ga:pageviews'].abs().mean()

        # Filter out all pages with page views below site average
        page_views_current = page_views_current[page_views_current['ga:pageviews'] >= avrg_pageviews]

        # Sort by page views
        page_views_current.sort_values(['ga:pageviews'], ascending=False, inplace=True)

        # Set indices
        page_views_current.set_index(['ga:pagePath'], inplace=True)

        # Get page paths
        above_avrg_paths = page_views_current.index.tolist()

        #################### BOUNCE RATES ####################
        self.activity_log.debug('Generating bounce rate summary data')

        # Change context for bounce rates
        context['api_metric'] = 'ga:bounces, ga:sessions, ga:goalCompletionsAll'
        context['api_dimension'] = 'ga:pagePath, ga:hostname'
        context['sort_key'] = '-ga:bounces'

        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        bounce_rates_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Append hostname to pagePath
        bounce_rates_current['ga:pagePath'] = bounce_rates_current['ga:hostname'].map(str) \
                                             + bounce_rates_current['ga:pagePath']

        # Drop hostname column
        bounce_rates_current.drop('ga:hostname', axis=1, inplace=True)

        # Replace all NaN values with zero
        # and Convert bounces, sessions, and goal completions to numeric
        #bounce_rates_current.fillna(0, inplace=True)
        bounce_rates_current[['ga:bounces', 'ga:sessions', 'ga:goalCompletionsAll']] = bounce_rates_current[
            ['ga:bounces', 'ga:sessions', 'ga:goalCompletionsAll']].fillna(0.0).astype(int)

        # Filter infusion soft path (remove everything after ?inf_contact or &inf_contact_key in path
        bounce_rates_current['ga:pagePath'].replace(r"\?inf_contact_key.*|&inf_contact_key.*", r"", regex = True, inplace = True)

        # Set indices
        #bounce_rates_current.set_index(['ga:pagePath'], inplace=True)

        # Sum up unique paths into one row
        bounce_rates_current = bounce_rates_current.groupby('ga:pagePath', as_index=False, sort=False).sum()

        # Sort by bounces
        bounce_rates_current.sort_values(['ga:bounces'], ascending=False, inplace=True)

        # Calculate the bounce rate
        bounce_rates_current.loc[:, 'bounceRate'] = round((bounce_rates_current['ga:bounces'] /
                                                           bounce_rates_current['ga:sessions']) * 100, 2)

        # Calculate the percentage of sessions which resulted in a conversion to at least one of the goals.
        bounce_rates_current.loc[:, 'goalConversionRateAll'] = round((bounce_rates_current['ga:goalCompletionsAll'] /
                                                           bounce_rates_current['ga:sessions']) * 100, 2)

        # Calculate the mean bounce rate
        #self.bounce_rate_mean = bounce_rates_current.loc[:, 'bounceRate'].abs().mean()
        self.bounce_rate_mean = round(int(bounce_rates_current['bounceRate'].abs().mean()), 2)

        # Get rows for above average paths
        bounce_rates_current = bounce_rates_current[bounce_rates_current['ga:pagePath'].isin(above_avrg_paths)].copy()

        # Filter out rows with zero sessions
        bounce_rates_current = bounce_rates_current[bounce_rates_current['ga:sessions'] != 0].copy()

        # Sort by bounce rate
        #bounce_rates_current.sort_values(['bounceRate', 'ga:bounces'], ascending=False, inplace=True)

        # Get pages with bounce rates above 75%
        self.highest_n_br = bounce_rates_current[bounce_rates_current['bounceRate'] >= 75].copy()

        # Get pages with bounce rates below 75%
        self.lowest_n_br = bounce_rates_current[bounce_rates_current['bounceRate'] <= 40].copy()

        # Set index to page path
        self.highest_n_br.set_index(['ga:pagePath'], inplace=True)
        self.lowest_n_br.set_index(['ga:pagePath'], inplace=True)

        # Calculate percent above/below average
        self.highest_n_br.loc[:, 'fromAvrg%'] = round(((self.highest_n_br['bounceRate'] - self.bounce_rate_mean) /
                                                                self.bounce_rate_mean) * 100, 2)
        self.lowest_n_br.loc[:, 'fromAvrg%'] = round(((self.lowest_n_br['bounceRate'] - self.bounce_rate_mean) /
                                                               self.bounce_rate_mean) * 100, 2)

        # Sort highest n by bounces
        self.highest_n_br = self.highest_n_br.sort_values(['ga:bounces'], ascending=False)

        # Sort lowest n by sessions
        self.lowest_n_br = self.lowest_n_br.sort_values(['ga:sessions'], ascending=False)

        # Get top n
        self.highest_n_br = self.highest_n_br.iloc[0:self.restrictions['top_n']].copy()
        self.lowest_n_br = self.lowest_n_br.iloc[0:self.restrictions['top_n']].copy()

        # Sort by bounceRate
        self.highest_n_br = self.highest_n_br.sort_values(['bounceRate'], ascending=False)
        self.lowest_n_br = self.lowest_n_br.sort_values(['bounceRate'], ascending=False)

        highest_n_pths = self.highest_n_br.index.tolist()
        lowest_n_pths = self.lowest_n_br.index.tolist()

        #################### BOUNCE RATES DETAIL ####################
        self.activity_log.debug('Generating bouncerate detailed data')

        # Change context for bounce rates by src
        context['api_metric'] = 'ga:bounces, ga:sessions, ga:goalCompletionsAll'
        context['api_dimension'] = 'ga:pagePath, ga:hostname, ga:source'
        context['sort_key'] = '-ga:bounces'

        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        bounce_rates_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Append hostname to pagePath
        bounce_rates_current['ga:pagePath'] = bounce_rates_current['ga:hostname'].map(str) \
                                              + bounce_rates_current['ga:pagePath']

        # Drop hostname column
        bounce_rates_current.drop('ga:hostname', axis=1, inplace=True)

        # Replace all NaN values with zero


        # Replace all NaN values with zero
        # and Convert bounces, session and goal completions to numeric
        #bounce_rates_current.fillna(0, inplace=True)
        #bounce_rates_current.loc[:, ('ga:bounces', 'ga:sessions', 'ga:goalCompletionsAll')] = bounce_rates_current[
        #    ['ga:bounces', 'ga:sessions', 'ga:goalCompletionsAll']].apply(pd.to_numeric)
        bounce_rates_current[['ga:bounces', 'ga:sessions', 'ga:goalCompletionsAll']] = bounce_rates_current[
            ['ga:bounces', 'ga:sessions', 'ga:goalCompletionsAll']].fillna(0.0).astype(int)

        # Filter infusion soft path (remove everything after ?inf_contact or &inf_contact_key in path
        bounce_rates_current['ga:pagePath'].replace(r"\?inf_contact_key.*|&inf_contact_key.*", r"", regex=True,
                                                    inplace=True)

        # Sum up unique paths into one row
        bounce_rates_current = bounce_rates_current.groupby(by=['ga:pagePath', 'ga:source'], as_index=False).sum()

        #bounce_rates_current.reset_index(inplace=True)

        self.highest_n_br_src = bounce_rates_current[bounce_rates_current['ga:pagePath'].isin(highest_n_pths)].copy()
        self.lowest_n_br_src = bounce_rates_current[bounce_rates_current['ga:pagePath'].isin(lowest_n_pths)].copy()

        # Calculate the bounce rate
        self.highest_n_br_src.loc[:, 'bounceRate'] = round((self.highest_n_br_src['ga:bounces'] /
                                                            self.highest_n_br_src['ga:sessions']) * 100, 2)

        self.lowest_n_br_src.loc[:, 'bounceRate'] = round((self.lowest_n_br_src['ga:bounces'] /
                                                            self.lowest_n_br_src['ga:sessions']) * 100, 2)

        # Calculate the percentage of sessions which resulted in a conversion to at least one of the goals.
        self.highest_n_br_src.loc[:, 'goalConversionRateAll'] = round((self.highest_n_br_src['ga:goalCompletionsAll'] /
                                                                       self.highest_n_br_src['ga:sessions']) * 100, 2)
        self.lowest_n_br_src.loc[:, 'goalConversionRateAll'] = round((self.lowest_n_br_src['ga:goalCompletionsAll'] /
                                                                       self.lowest_n_br_src['ga:sessions']) * 100, 2)

        # Calculate percent above/below average
        self.highest_n_br_src.loc[:, 'fromAvrg%'] = round(((self.highest_n_br_src['bounceRate'] - self.bounce_rate_mean) /
                                                       self.bounce_rate_mean) * 100, 2)
        self.lowest_n_br_src.loc[:, 'fromAvrg%'] = round(((self.lowest_n_br_src['bounceRate'] - self.bounce_rate_mean) /
                                                      self.bounce_rate_mean) * 100, 2)

        # Set indices
        self.highest_n_br_src.set_index(['ga:pagePath', 'ga:source'], inplace=True)
        self.lowest_n_br_src.set_index(['ga:pagePath', 'ga:source'], inplace=True)

    def gen_sources(self):
        '''
        Generates TRAFFIC SOURCE summary and detail data frames
        '''
        self.activity_log.debug('Generating source data')
        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:source, ga:medium, ga:hasSocialSourceReferral, ga:socialNetwork',
                                          metrics='ga:sessions, ga:goalCompletionsAll',
                                          sort_key='-ga:sessions'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        sources_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        events_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Outer merge: Everything from both periods (previous first)
        sources_full = events_previous.merge(right=sources_current,
                                            how='outer',
                                            on=['ga:source', 'ga:medium', 'ga:hasSocialSourceReferral', 'ga:socialNetwork'],
                                            suffixes=['_prev', '_curr'])

        sources_full.sort_values('ga:source', ascending=True, inplace=True)

        # Replace all NaN values with zero
        # and Convert sessions and goalCompletions to numeric
        sources_full[['ga:sessions_prev', 'ga:sessions_curr']] = sources_full[['ga:sessions_prev', 'ga:sessions_curr']].fillna(0.0).astype(int)
        sources_full[['ga:goalCompletionsAll_prev', 'ga:goalCompletionsAll_curr']] = sources_full[['ga:goalCompletionsAll_prev', 'ga:goalCompletionsAll_curr']].fillna(0.0).astype(int)

        # Add the delta percentage from prev to curr sessions
        sources_full.loc[:, 'sessionsChangeRate'] = round(((sources_full['ga:sessions_curr'] - sources_full['ga:sessions_prev'])/
                                             sources_full['ga:sessions_prev'])*100, 2)

        # Add the delta percentage from prev to curr goalCompletions
        sources_full.loc[:, 'goalCompletionsChangeRate'] = round(((sources_full['ga:goalCompletionsAll_curr'] - sources_full['ga:goalCompletionsAll_prev']) /
                                                sources_full['ga:goalCompletionsAll_prev']) * 100, 2)

        # Calculate the percentage of sessions which resulted in a conversion to at least one of the goals
        sources_full.loc[:, 'goalConversionRateAll_curr'] = round((sources_full['ga:goalCompletionsAll_curr'] /
                                                              sources_full['ga:sessions_curr']) * 100, 2)
        sources_full.loc[:, 'goalConversionRateAll_prev'] = round((sources_full['ga:goalCompletionsAll_prev'] /
                                                                   sources_full['ga:sessions_prev']) * 100, 2)

        # Replace all NaN values for goalCompletions delta_% and goalConversionRateAll_curr to zero
        # Occurs when BOTH numerator and denominator in the divisions above are zero
        sources_full[['sessionsChangeRate', 'goalCompletionsChangeRate', 'goalConversionRateAll_curr', 'goalConversionRateAll_prev']] = sources_full[
            ['sessionsChangeRate', 'goalCompletionsChangeRate', 'goalConversionRateAll_curr', 'goalConversionRateAll_prev']].fillna(0.0)

        #################### SOCIAL SOURCES ####################
        srcs_social = sources_full[sources_full['ga:hasSocialSourceReferral'] == 'Yes']
        # srcs_social = sources_full[sources_full['ga:hasSocialSourceReferral'].str.contains(r'Yes')]
        # Sum up unique socialNetworks into one row
        srcs_social = srcs_social.groupby('ga:socialNetwork', as_index=False, sort=False).sum()

        # Rename the ga:socialNetwork column to source
        srcs_social.rename(columns = {'ga:socialNetwork':'source'}, inplace=True)

        # Sort by current sessions
        #srcs_social.sort_values('ga:sessions_curr', ascending=False, inplace=True)
        srcs_social = srcs_social.sort_values(['ga:sessions_curr'], ascending=False)

        # Recalculate %change in sessions and goal completions, and the conversion rate due to new grouping
        srcs_social.loc[:, 'sessionsChangeRate'] = round(((srcs_social['ga:sessions_curr'] - srcs_social['ga:sessions_prev'])/
                                                             srcs_social['ga:sessions_prev'])*100, 2)

        # Add the delta percentage from prev to curr goalCompletions
        srcs_social.loc[:, 'goalCompletionsChangeRate'] = round(((srcs_social['ga:goalCompletionsAll_curr'] - srcs_social['ga:goalCompletionsAll_prev']) /
                                                                      srcs_social['ga:goalCompletionsAll_prev']) * 100, 2)

        # Calculate the percentage of sessions which resulted in a conversion to at least one of the goals
        # Calculated for the current and previous period
        srcs_social.loc[:, 'goalConversionRateAll_curr'] = round((srcs_social['ga:goalCompletionsAll_curr'] /
                                                                   srcs_social['ga:sessions_curr']) * 100, 2)
        srcs_social.loc[:, 'goalConversionRateAll_prev'] = round((srcs_social['ga:goalCompletionsAll_prev'] /
                                                                       srcs_social['ga:sessions_prev']) * 100, 2)

        # Replace all NaN values for goalCompletions delta_% and goalConversionRateAll_curr to zero
        # Occurs when BOTH numerator and denominator in the divisions above are zero
        srcs_social[['sessionsChangeRate', 'goalCompletionsChangeRate', 'goalConversionRateAll_curr', 'goalConversionRateAll_prev']] = srcs_social[
            ['sessionsChangeRate', 'goalCompletionsChangeRate', 'goalConversionRateAll_curr', 'goalConversionRateAll_prev']].fillna(0.0)

        # Add the a category column and set it to Social
        srcs_social.insert(0, 'category', 'Social')

        self.srcs_detail = srcs_social

        # Remove social sources from full table
        sources_full = sources_full[sources_full['ga:hasSocialSourceReferral'] == 'No']

        # Drop hasSocialSourceReferral and SocialNetwork columns from full table
        sources_full.drop(['ga:hasSocialSourceReferral', 'ga:socialNetwork'], axis=1, inplace=True)

        #################### ORGANIC SEARCH SOURCES ####################
        srcs_organic_search = sources_full[sources_full['ga:medium'] == 'organic']
        # srcs_organic_search = sources_full[sources_full['ga:medium'].str.contains(r'organic')]

        # Sort by current sessions
        srcs_organic_search = srcs_organic_search.sort_values(['ga:sessions_curr'], ascending=False)

        # Rename the ga:source column to source
        srcs_organic_search.rename(columns={'ga:source': 'source'}, inplace=True)

        # Drop the ga:medium column
        srcs_organic_search.drop('ga:medium', axis=1, inplace=True)

        # Add the a category column and set it to Organic Search
        srcs_organic_search.insert(0, 'category', 'Organic Search')

        # Add to source detail table
        self.srcs_detail = self.srcs_detail.append(srcs_organic_search)

        # Remove organic search sources from full table
        sources_full = sources_full[sources_full['ga:medium'] != 'organic']

        #################### PAID SEARCH SOURCES ####################
        srcs_paid_search = sources_full[(sources_full['ga:medium'] == 'cpc') |
                                             (sources_full['ga:medium'] == 'ppc') |
                                             (sources_full['ga:medium'] == 'paidsearch')]
        #srcs_paid_search = sources_full[sources_full['ga:medium'].str.contains(r'cpc|ppc|paidsearch')]

        # Sort by current sessions
        srcs_paid_search = srcs_paid_search.sort_values(['ga:sessions_curr'], ascending=False)

        # Rename the ga:source column to source
        srcs_paid_search.rename(columns={'ga:source': 'source'}, inplace=True)

        # Drop the ga:medium column
        srcs_paid_search.drop('ga:medium', axis=1, inplace=True)

        # Add the a category column and set it to Paid Search
        srcs_paid_search.insert(0, 'category', 'Paid Search')

        # Add to source detail table
        self.srcs_detail = self.srcs_detail.append(srcs_paid_search)

        # Remove paid search sources from full table
        sources_full = sources_full[(sources_full['ga:medium'] != 'cpc') &
                                    (sources_full['ga:medium'] != 'ppc') &
                                    (sources_full['ga:medium'] != 'paidsearch')]

        #################### DISPLAY SOURCES ####################
        srcs_display = sources_full[(sources_full['ga:medium'] == 'display') |
                                         (sources_full['ga:medium'] == 'cpm') |
                                         (sources_full['ga:medium'] == 'banner)')]
        #srcs_display = sources_full[sources_full['ga:medium'].str.contains(r'display|cpm|banner')]

        # Sort by current sessions
        srcs_display = srcs_display.sort_values(['ga:sessions_curr'], ascending=False)

        # Rename the ga:source column to source
        srcs_display.rename(columns={'ga:source': 'source'}, inplace=True)

        # Drop the ga:medium column
        srcs_display.drop('ga:medium', axis=1, inplace=True)

        # Add the a category column and set it to Display
        srcs_display.insert(0, 'category', 'Display')

        # Add to source detail table
        self.srcs_detail = self.srcs_detail.append(srcs_display)

        # Remove display sources from full table
        sources_full = sources_full[(sources_full['ga:medium'] != 'display') &
                                    (sources_full['ga:medium'] != 'cpm') &
                                    (sources_full['ga:medium'] != 'banner)')]

        #################### REFERRAL SOURCES ####################
        srcs_referral = sources_full[sources_full['ga:medium'] == 'referral']
        #srcs_referral = sources_full[sources_full['ga:medium'].str.contains(r'referral')]

        # Sort by current sessions
        srcs_referral = srcs_referral.sort_values(['ga:sessions_curr'], ascending=False)

        # Rename the ga:source column to source
        srcs_referral.rename(columns={'ga:source': 'source'}, inplace=True)

        # Drop the ga:medium column
        srcs_referral.drop('ga:medium', axis=1, inplace=True)

        # Add the a category column and set it to Referral
        srcs_referral.insert(0, 'category', 'Referral')

        # Add to source detail table
        self.srcs_detail = self.srcs_detail.append(srcs_referral)

        # Remove referral sources from full table
        sources_full = sources_full[sources_full['ga:medium'] != 'referral']

        #################### DIRECT SOURCES ####################
        srcs_direct = sources_full[sources_full['ga:source'] == '(direct)']
        #srcs_direct = sources_full[sources_full['ga:source'].str.contains(r'direct') &
        #                                sources_full['ga:medium'].str.contains(r'none|not set')]

        # Sort by current sessions
        srcs_direct = srcs_direct.sort_values(['ga:sessions_curr'], ascending=False)

        # Rename the ga:source column to source
        srcs_direct.rename(columns={'ga:source': 'source'}, inplace=True)

        # Drop the ga:medium column
        srcs_direct.drop('ga:medium', axis=1, inplace=True)

        # Add the a category column and set it to Direct
        srcs_direct.insert(0, 'category', 'Direct')

        # Add to source detail table
        self.srcs_detail = self.srcs_detail.append(srcs_direct)

        # Remove referral sources from full table
        sources_full = sources_full[sources_full['ga:source'] != '(direct)']

        #################### EMAIL SOURCES ####################
        srcs_email = sources_full[sources_full['ga:medium'] == 'email']

        # Sort by current sessions
        srcs_email = srcs_email.sort_values(['ga:sessions_curr'], ascending=False)

        # Rename the ga:source column to source
        srcs_email.rename(columns={'ga:source': 'source'}, inplace=True)

        # Drop the ga:medium column
        srcs_email.drop('ga:medium', axis=1, inplace=True)

        # Add the a category column and set it to Email
        srcs_email.insert(0, 'category', 'Email')

        # Add to source detail table
        self.srcs_detail = self.srcs_detail.append(srcs_email)

        # Remove referral sources from full table
        sources_full = sources_full[sources_full['ga:medium'] != 'email']

        #################### OTHER SOURCES ####################
        srcs_other = sources_full

        # Sort by current sessions
        srcs_other = srcs_other.sort_values(['ga:sessions_curr'], ascending=False)

        # Rename the ga:source column to source
        srcs_other.rename(columns={'ga:source': 'source'}, inplace=True)

        # Drop the ga:medium column
        srcs_other.drop('ga:medium', axis=1, inplace=True)

        # Add the a category column and set it to Other
        srcs_other.insert(0, 'category', 'Other')

        # Add to source detail table
        self.srcs_detail = self.srcs_detail.append(srcs_other)

        # Set indices
        self.srcs_detail.set_index(['category', 'source'], inplace=True)


        #################### CATEGORY SUMMARY ####################
        catagories = self.srcs_detail.index.levels[0].tolist()

        self.srcs_summary = pd.DataFrame(columns=['ga:sessions_prev', 'ga:goalCompletionsAll_prev', 'ga:sessions_curr', 'ga:goalCompletionsAll_curr'])
        for category in catagories:
            cat_detail = self.srcs_detail.ix[category]
            row = cat_detail[['ga:sessions_prev', 'ga:goalCompletionsAll_prev', 'ga:sessions_curr', 'ga:goalCompletionsAll_curr']].sum()
            row = pd.Series(data=category, index=['category']).append(row)
            self.srcs_summary = self.srcs_summary.append(row, ignore_index=True)

        # Add the delta percentage from prev to curr sessions
        self.srcs_summary.loc[:, 'sessionsChangeRate'] = round(
            ((self.srcs_summary['ga:sessions_curr'] - self.srcs_summary['ga:sessions_prev']) /
             self.srcs_summary['ga:sessions_prev']) * 100, 2)

        # Add the delta percentage from prev to curr goalCompletions
        self.srcs_summary.loc[:, 'goalCompletionsChangeRate'] = round(
            ((self.srcs_summary['ga:goalCompletionsAll_curr'] - self.srcs_summary['ga:goalCompletionsAll_prev']) /
             self.srcs_summary['ga:goalCompletionsAll_prev']) * 100, 2)

        # Calculate the percentage of sessions which resulted in a conversion to at least one of the goals
        self.srcs_summary.loc[:, 'goalConversionRateAll_curr'] = round((self.srcs_summary['ga:goalCompletionsAll_curr'] /
                                                                   self.srcs_summary['ga:sessions_curr']) * 100, 2)
        self.srcs_summary.loc[:, 'goalConversionRateAll_prev'] = round((self.srcs_summary['ga:goalCompletionsAll_prev'] /
                                                                   self.srcs_summary['ga:sessions_prev']) * 100, 2)

        # Replace all NaN values for goalCompletions delta_% and goalConversionRateAll_curr to zero
        # Occurs when BOTH numerator and denominator in the divisions above are zero
        self.srcs_summary[['sessionsChangeRate', 'goalCompletionsChangeRate', 'goalConversionRateAll_curr', 'goalConversionRateAll_prev']] = \
            self.srcs_summary[
            ['sessionsChangeRate', 'goalCompletionsChangeRate', 'goalConversionRateAll_curr', 'goalConversionRateAll_prev']].fillna(0.0)

        # Sort by current sessions
        self.srcs_summary = self.srcs_summary.sort_values(['ga:sessions_curr'], ascending=False)

        # Set index
        self.srcs_summary.set_index(['category'], inplace=True)


    def gen_exec_overview(self):
        '''
        Generates the raw changes and percentage changes in:
        VISITORS(users), VISITS(sessions), PAGEVIEWS, GOAL COMPLETIONS, and EVENTS
        '''
        self.activity_log.debug('Generating executive overview data')

        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:pagePath',
                                          metrics='ga:users, ga:sessions, ga:pageviews, ga:goalCompletionsAll, ga:totalEvents',
                                          sort_key='-ga:users'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        exec_ov_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        exec_ov_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Outer merge: Everything from both periods (previous first)
        exec_ov_full = exec_ov_previous.merge(right=exec_ov_current,
                                          how='outer',
                                          on=['ga:pagePath'],
                                          suffixes=['_prev', '_curr'])

        # Replace all NaN values with zero
        # and Convert page views to numeric
        exec_ov_full[['ga:users_prev', 'ga:users_curr']] = exec_ov_full[
            ['ga:users_prev', 'ga:users_curr']].fillna(0.0).astype(int)
        exec_ov_full[['ga:sessions_prev', 'ga:sessions_curr']] = exec_ov_full[
            ['ga:sessions_prev', 'ga:sessions_curr']].fillna(0.0).astype(int)
        exec_ov_full[['ga:pageviews_prev', 'ga:pageviews_curr']] = exec_ov_full[
            ['ga:pageviews_prev', 'ga:pageviews_curr']].fillna(0.0).astype(int)
        exec_ov_full[['ga:goalCompletionsAll_prev', 'ga:goalCompletionsAll_curr']] = exec_ov_full[
            ['ga:goalCompletionsAll_prev', 'ga:goalCompletionsAll_curr']].fillna(0.0).astype(int)
        exec_ov_full[['ga:totalEvents_prev', 'ga:totalEvents_curr']] = exec_ov_full[
            ['ga:totalEvents_prev', 'ga:totalEvents_curr']].fillna(0.0).astype(int)

        # From prev to curr
        self.exec_ov_visitors_delta = (exec_ov_full['ga:users_prev'].sum(), exec_ov_full['ga:users_curr'].sum())
        self.exec_ov_visits_delta = (exec_ov_full['ga:sessions_prev'].sum(), exec_ov_full['ga:sessions_curr'].sum())
        self.exec_ov_pageviews_delta = (exec_ov_full['ga:pageviews_prev'].sum(), exec_ov_full['ga:pageviews_curr'].sum())
        self.exec_ov_goals_delta = (exec_ov_full['ga:goalCompletionsAll_prev'].sum(), exec_ov_full['ga:goalCompletionsAll_curr'].sum())
        self.exec_ov_events_delta = (exec_ov_full['ga:totalEvents_prev'].sum(), exec_ov_full['ga:totalEvents_curr'].sum())

        # Get the site wide percentage change in page views
        self.exec_ov_visitors_delta_perc = round((self.exec_ov_visitors_delta[1] - self.exec_ov_visitors_delta[0]) /
                                                 (self.exec_ov_visitors_delta[0]) * 100, 2)
        self.exec_ov_visits_delta_perc = round((self.exec_ov_visits_delta[1] - self.exec_ov_visits_delta[0]) /
                                               (self.exec_ov_visits_delta[0]) * 100, 2)
        self.exec_ov_pageviews_delta_perc = round((self.exec_ov_pageviews_delta[1] - self.exec_ov_pageviews_delta[0]) /
                                                  (self.exec_ov_pageviews_delta[0]) * 100, 2)
        self.exec_ov_goals_delta_perc = round((self.exec_ov_goals_delta[1] - self.exec_ov_goals_delta[0]) /
                                              (self.exec_ov_goals_delta[0]) * 100, 2)
        self.exec_ov_events_delta_perc = round((self.exec_ov_events_delta[1] - self.exec_ov_events_delta[0]) /
                                               (self.exec_ov_events_delta[0]) * 100, 2)

    ########## EXECUTIVE OVERVIEW SPLIT INTO PARTS ##########
    #################### NOT IN USE ####################
    def exec_ov_visitors(self):
        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:pagePath',
                                          metrics='ga:users',
                                          sort_key='-ga:users'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        users_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        users_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Outer merge: Everything from both periods (previous first)
        users_full = users_previous.merge(right=users_current,
                                                    how='outer',
                                                    on=['ga:pagePath'],
                                                    suffixes=['_prev', '_curr'])

        # Replace all NaN values with zero
        # and Convert page views to numeric
        users_full[['ga:users_prev', 'ga:users_curr']] = users_full[
            ['ga:users_prev', 'ga:users_curr']].fillna(0.0).astype(int)

        # Add the delta value from prev to curr page views
        users_full.loc[:, 'Delta'] = users_full['ga:users_curr'] - users_full['ga:users_prev']

        # Get site wide change in page views
        self.exec_ov_visitors_delta = users_full['Delta'].sum()

        # Get the site wide percentage change in page views
        self.exec_ov_visitors_delta_perc = round(self.exec_ov_visitors_delta / users_full['ga:users_prev'].sum() *100, 2)

    def exec_ov_visits(self):
        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:pagePath',
                                          metrics='ga:sessions',
                                          sort_key='-ga:sessions'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        sessions_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        sessions_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Outer merge: Everything from both periods (previous first)
        sessions_full = sessions_previous.merge(right=sessions_current,
                                                    how='outer',
                                                    on=['ga:pagePath'],
                                                    suffixes=['_prev', '_curr'])

        # Replace all NaN values with zero
        # and Convert page views to numeric
        sessions_full[['ga:sessions_prev', 'ga:sessions_curr']] = sessions_full[
            ['ga:sessions_prev', 'ga:sessions_curr']].fillna(0.0).astype(int)

        # Add the delta value from prev to curr page views
        sessions_full.loc[:, 'Delta'] = sessions_full['ga:sessions_curr'] - sessions_full['ga:sessions_prev']

        # Get site wide change in page views
        self.exec_ov_visits_delta = sessions_full['Delta'].sum()

        # Get the site wide percentage change in page views
        self.exec_ov_visits_delta_perc = round(self.exec_ov_visits_delta / sessions_full['ga:sessions_prev'].sum() *100, 2)

    def exec_ov_pageviews(self):
        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:pagePath',
                                          metrics='ga:pageviews',
                                          sort_key='-ga:pageviews'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        page_views_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        page_views_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Outer merge: Everything from both periods (previous first)
        page_views_full = page_views_previous.merge(right=page_views_current,
                                                    how='outer',
                                                    on=['ga:pagePath'],
                                                    suffixes=['_prev', '_curr'])

        # Replace all NaN values with zero
        # and Convert page views to numeric
        #page_views_full.fillna(value=0, axis=0, inplace=True)
        page_views_full[['ga:pageviews_prev', 'ga:pageviews_curr']] = page_views_full[
            ['ga:pageviews_prev', 'ga:pageviews_curr']].fillna(0.0).astype(int)

        # Add the delta value from prev to curr page views
        page_views_full.loc[:, 'Delta'] = page_views_full['ga:pageviews_curr'] - page_views_full['ga:pageviews_prev']

        # Get site wide change in page views
        self.exec_ov_pageviews_delta = page_views_full['Delta'].sum()

        # Get the site wide percentage change in page views
        self.exec_ov_pageviews_delta_perc = round(self.exec_ov_pageviews_delta / page_views_full['ga:pageviews_prev'].sum() *100, 2)

    def exec_ov_goalcompletions(self):
        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:pagePath',
                                          metrics='ga:goalCompletionsAll',
                                          sort_key='-ga:goalCompletionsAll'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        goal_compl_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        goal_compl_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Outer merge: Everything from both periods (previous first)
        goal_compl_full = goal_compl_previous.merge(right=goal_compl_current,
                                                how='outer',
                                                on=['ga:pagePath'],
                                                suffixes=['_prev', '_curr'])

        # Replace all NaN values with zero
        # and Convert page views to numeric
        goal_compl_full[['ga:goalCompletionsAll_prev', 'ga:goalCompletionsAll_curr']] = goal_compl_full[
            ['ga:goalCompletionsAll_prev', 'ga:goalCompletionsAll_curr']].fillna(0.0).astype(int)

        # Add the delta value from prev to curr page views
        goal_compl_full.loc[:, 'Delta'] = goal_compl_full['ga:goalCompletionsAll_curr'] - goal_compl_full['ga:goalCompletionsAll_prev']

        # Get site wide change in page views
        self.exec_ov_goals_delta = goal_compl_full['Delta'].sum()

        # Get the site wide percentage change in page views
        self.exec_ov_goals_delta_perc = round(self.exec_ov_goals_delta / goal_compl_full['ga:goalCompletionsAll_prev'].sum() * 100, 2)

    def exec_ov_events(self):
        context = self.get_ga_api_context(period=self.period_current,
                                          dimensions='ga:pagePath',
                                          metrics='ga:totalEvents',
                                          sort_key='-ga:totalEvents'
                                          )
        values = api.get_results(context)

        # Get column names
        headers = values.get('columnHeaders')
        col_names = []
        for header in headers:
            col_names.append(header.get('name'))

        # Get data for current period
        events_current = pd.DataFrame(values.get("rows"), columns=col_names)

        # Update call for second period
        context["st_date"] = self.period_previous['START']
        context["end_date"] = self.period_previous['END']
        values = api.get_results(context)

        # Get data for previous period
        events_previous = pd.DataFrame(values.get("rows"), columns=col_names)

        # Outer merge: Everything from both periods (previous first)
        events_full = events_previous.merge(right=events_current,
                                                    how='outer',
                                                    on=['ga:pagePath'],
                                                    suffixes=['_prev', '_curr'])

        # Replace all NaN values with zero
        # and Convert page views to numeric
        events_full[['ga:totalEvents_prev', 'ga:totalEvents_curr']] = events_full[
            ['ga:totalEvents_prev', 'ga:totalEvents_curr']].fillna(0.0).astype(int)

        # Add the delta value from prev to curr page views
        events_full.loc[:, 'Delta'] = events_full['ga:totalEvents_curr'] - events_full['ga:totalEvents_prev']

        # Get site wide change in page views
        self.exec_ov_events_delta = events_full['Delta'].sum()

        # Get the site wide percentage change in page views
        self.exec_ov_events_delta_perc = round(self.exec_ov_events_delta / events_full['ga:totalEvents_prev'].sum() * 100, 2)

    def get_top_spikes_smry(self):
        return self.top_n_spikes

    def get_top_drops_smry(self):
        return self.top_n_drops

    def get_top_spikes_src(self):
        return self.top_n_spikes_src

    def get_top_drops_src(self):
        return self.top_n_drops_src

    def get_br_smry(self):
        return self.highest_n_br

    def tts_ttd_summary_csv(self):
        self.top_n_spikes.to_csv(os.path.join(self.csv_directory, 'top_traffic_changes', 'tts_summary.csv'))
        self.top_n_drops.to_csv(os.path.join(self.csv_directory, 'top_traffic_changes', 'ttd_summary.csv'))

    def tts_ttd_detailed_csv(self):
        self.top_n_spikes_src.to_csv(os.path.join(self.csv_directory, 'top_traffic_changes', 'tts_detailed.csv'))
        self.top_n_drops_src.to_csv(os.path.join(self.csv_directory, 'top_traffic_changes', 'ttd_detailed.csv'))

    def bounce_rates_summary_csv(self):
        self.highest_n_br.to_csv(os.path.join(self.csv_directory, 'bounce_rates', 'highest_br_summary.csv'))
        self.lowest_n_br.to_csv(os.path.join(self.csv_directory, 'bounce_rates', 'lowest_br_summary.csv'))

    def bounce_rates_detailed_csv(self):
        self.highest_n_br_src.to_csv(os.path.join(self.csv_directory, 'bounce_rates', 'highest_br_detailed.csv'))
        self.lowest_n_br_src.to_csv(os.path.join(self.csv_directory, 'bounce_rates', 'lowest_br_detailed.csv'))

    def sources_csv(self):
        self.srcs_summary.to_csv(os.path.join(self.csv_directory, 'sources', 'srcs_summary.csv'))
        self.srcs_detail.to_csv(os.path.join(self.csv_directory, 'sources', 'srcs_detail.csv'))


'''
if __name__ == '__main__':
    anal_test = Analytics()

    anal_test.gen_tts_ttd()
    anal_test.gen_bouncerate()
    anal_test.gen_sources()

    anal_test.tts_ttd_summary_csv()
    anal_test.tts_ttd_detailed_csv()
    anal_test.bounce_rates_summary_csv()
    anal_test.bounce_rates_detailed_csv()
    anal_test.sources_csv()
'''