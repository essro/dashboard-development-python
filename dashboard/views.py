import json
import numpy as np
import pandas as pd
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from dashboard.analysis.analytics import Analytics

""" @file views.py
    @author Justin Chambers
    @author Husain Tasarvi
    @author Joseph Ravenna
    @date 20170430
    @description This file contains the DashboardView class implementation
"""


class DashboardView(LoginRequiredMixin, TemplateView):
    """ @brief DashboardView
        @description Constructor and Operations for the DashboardView class
    """
    def __init__(self):
        """ @brief DashboardView constructor
            @description Initializes an instance of the DashboardView, complete with elements
        """
        # print('Start DashboardView Constructor')
        super(DashboardView, self).__init__()

        # login URL
        self.login_url = '/login/'

        self.redirect_field_name = '/login/'

        # ----- GET DASHBOARD TEMPLATE -----
        self.template_name = "dashboard/dashboard.html"

        # ----- DEFAULT PREFS ------
        self.prefs = {
            'username': 'Joe Shmoe',
            'acct_list': ['Account 1', 'Account 2', 'Account 3'],
            'current_start_date': '30daysAgo',
            'current_end_date': 'today',
            'prev_start_date': '60daysAgo',
            'prev_end_date': '30daysAgo'
        }

        # ----- DEFAULT ELEMENT CONTAINER ------
        self.generic_element_content = {
            'title': 'Dashboard Element Title',
            'icon': '/dashboard/static/img/ic_check_circle.svg',
            'container_type': 'generic',
            'container': [],
            'position': 0,
            'block_id': 'zz'
        }

        self.analysis = None
        self.analysis_layer_exists = False

        print('End DashboardView Constructor\n\n')

    def get_context_data(self, **kwargs):
        """ @brief get_context_data
            @description function receives the HTML request and generates the context variables
                        to be attached to the HTML response
            @param kwargs: the pointer to the HTML request 
            @return context: the HTML response containing all the dashboard data
        """
        print('Start get_context_data')
        if 'view' not in kwargs:
            self.analysis = Analytics()
            # print('Init XO...')
            self.analysis.gen_exec_overview()
            # print('Init TTS/TTD...')
            self.analysis.gen_tts_ttd()
            # print('Init BR...')
            self.analysis.gen_bouncerate()
            # print('Init SRCS...')
            self.analysis.gen_sources()
            self.analysis_layer_exists = True
            context = super(DashboardView, self).get_context_data(**kwargs)
            context['preferences'] = self.prefs
            context['username'] = self.prefs['username']
            context['page_title'] = 'Nerd Vision, v1'
            context['menu_title'] = 'Nerd Vision: ' + self.prefs['username']
            context['menu_icon'] = 'img/ic_menu.svg'
            context['date_range_icon'] = 'img/ic_date_range.svg'
            context['elements'] = self.init_elements()
        else:
            context = kwargs
        # print('End get_context_data (returning context)\n\n')
        return context

    def init_elements(self):
        """ @brief init_elements
            @description function initializes all 5 of the dashboard elements
            @return the list of elements 
        """
        # print('CALL init_elements\n\n')
        return [
            self.init_exec_overview(),
            self.init_top_spikes(),
            self.init_top_drops(),
            self.init_bounce_rates(),
            self.init_sources()
        ]

    def init_exec_overview(self):
        """ @brief init_exec_overview
            @description function initializes the Executive Overview element
            @return xo_content: a dictionary containing key, value pairs for the XO element
        """
        # print('Start init_exec_overview')
        xo_content = self.generic_element_content.copy()
        xo_content['title'] = 'Executive Overview'
        xo_content['position'] = 0
        xo_content['block_id'] = 'xo'
        xo_content['container_type'] = 'carousel'
        icon_loc = '/dashboard/static/img/'

        # ---- VISITORS ----
        # Generate visitors executive overview data
        value_vstrs = str(self.analysis.exec_ov_visitors_delta[0]) + ' to ' + str(self.analysis.exec_ov_visitors_delta[1])
        percent_vstrs = str(abs(self.analysis.exec_ov_visitors_delta_perc)) + '%'

        if self.analysis.exec_ov_visitors_delta_perc >= 0:
            direction_vstrs = 'up'
            card_id_vstrs = 'card-up'
            icon_vstrs = icon_loc + 'ic_account_circle.svg'
        else:
            direction_vstrs = 'down'
            card_id_vstrs = 'card-down'
            icon_vstrs = icon_loc + 'ic_account_circle_red.svg'

        # ---- VISITS ----
        # Generate visits executive overview data
        value_vst = str(self.analysis.exec_ov_visits_delta[0]) + ' to ' + str(self.analysis.exec_ov_visits_delta[1])
        percent_vst = str(abs(self.analysis.exec_ov_visits_delta_perc)) + '%'

        if self.analysis.exec_ov_visits_delta_perc >= 0:
            direction_vst = 'up'
            card_id_vst = 'card-up'
            icon_vst = icon_loc + 'ic_visits.svg'
        else:
            direction_vst = 'down'
            card_id_vst = 'card-down'
            icon_vst = icon_loc + 'ic_visits_red.svg'

        # ---- PAGEVIEWS ----
        # Generate pageviews executive overview data
        value_pv = str(self.analysis.exec_ov_pageviews_delta[0]) + ' to ' + str(self.analysis.exec_ov_pageviews_delta[1])
        percent_pv = str(abs(self.analysis.exec_ov_pageviews_delta_perc)) + '%'

        if self.analysis.exec_ov_pageviews_delta_perc >= 0:
            direction_pv = 'up'
            card_id_pv = 'card-up'
            icon_pv = icon_loc + 'ic_pgviews.svg'
        else:
            direction_pv = 'down'
            card_id_pv = 'card-down'
            icon_pv = icon_loc + 'ic_pgviews_red.svg'

        # ---- GOAL COMPLETIONS ----
        # Generate goal completions executive overview data
        value_gc = str(self.analysis.exec_ov_goals_delta[0]) + ' to ' + str(self.analysis.exec_ov_goals_delta[1])
        percent_gc = str(abs(self.analysis.exec_ov_goals_delta_perc)) + '%'

        if self.analysis.exec_ov_goals_delta_perc >= 0:
            direction_gc = 'up'
            card_id_gc = 'card-up'
            icon_gc = icon_loc + 'ic_check_circle.svg'
        else:
            direction_gc = 'down'
            card_id_gc = 'card-down'
            icon_gc = icon_loc + 'ic_check_circle_red.svg'

        # ---- EVENTS ----
        # Generate events executive overview data
        value_evt = str(self.analysis.exec_ov_events_delta[0]) + ' to ' + str(self.analysis.exec_ov_events_delta[1])
        percent_evt = str(abs(self.analysis.exec_ov_events_delta_perc)) + '%'

        if self.analysis.exec_ov_events_delta_perc >= 0:
            direction_evt = 'up'
            card_id_evt = 'card-up'
            icon_evt = icon_loc + 'ic_date_range.svg'
        else:
            direction_evt = 'down'
            card_id_evt = 'card-down'
            icon_evt = icon_loc + 'ic_date_range_red.svg'

        xo_content['container'] = [
            {
                'icon': icon_vstrs,
                'name': "Visitors",
                'value': value_vstrs,
                'percent': percent_vstrs,
                'direction': direction_vstrs,
                'timeframe': "month",
                'card_id': card_id_vstrs
            },
            {
                'icon': icon_vst,
                'name': "Visits",
                'value': value_vst,
                'percent': percent_vst,
                'direction': direction_vst,
                'timeframe': "month",
                'card_id': card_id_vst
            },
            {
                'icon': icon_pv,
                'name': "Pageviews",
                'value': value_pv,
                'percent': percent_pv,
                'direction': direction_pv,
                'timeframe': "month",
                'card_id': card_id_pv
            },
            {
                'icon': icon_gc,
                'name': "Goals",
                'value': value_gc,
                'percent': percent_gc,
                'direction': direction_gc,
                'timeframe': "month",
                'card_id': card_id_gc
            },
            {
                'icon': icon_evt,
                'name': "Events",
                'value': value_evt,
                'percent': percent_evt,
                'direction': direction_evt,
                'timeframe': "month",
                'card_id': card_id_evt
            }
        ]

        # print('End init_exec_overview (returning xo_content)\n\n')

        return xo_content

    def update_time_frame(self):
        """ @brief update_time_frame
            @description function should detect an update in time frames, then update the dashboard
                        data accordingly and push the new data to the front end
            @description THIS FUNCTION IS NOT IMPLEMENTED, AS THE FEATURE IS PART OF THE FUTURE WORK
            @description NOTE: The algorithm in commented pseudocode is provided below
        """
        '''
            get request
                check if user has requested updated data

                get preferences data from pref model
                get changes from UI layer (request? update? ...)

                if no change
                    do nothing
                if change
                    test if change is valid (is date range valid?)
                    if no
                        return error
                    if yes
                        update pref model
                        pass pref model data to generate fcn

        '''

    def init_top_spikes(self):
        """ @brief init_top_spikes
            @description function initializes the Top Traffic Spike Element
            @return ts_content: a dictionary containing key, value pairs for the TTS element
        """

        # print('Start init_top_spikes')
        tts = self.analysis.get_top_spikes_smry()
        tts_paths = tts.index.tolist()

        summary_strings = []

        # ANONYMIZED PATHS
        # path_suffix = 1

        for path in tts_paths:

            # ANONYMIZED PATHS
            # anonymized_path = 'spike_page ' + str(path_suffix)
            # path_suffix += 1
            # string = str(tts.ix[path]['Delta_%']) + '% increase in page visits to ' + anonymized_path
            # END ANONYMIZED

            # ACTUAL PATHS
            string = str(tts.ix[path]['Delta_%']) + '% increase in page visits to ' + path
            # END ACTUAL

            summary_strings.append(string)

        ts_content = {
            'title': 'Top Traffic Spikes',
            'icon': '/dashboard/static/img/trend_up.svg',
            'container_type': 'accordion',
            'container': []
        }

        for index in range(len(summary_strings)):
            detail_params = {
                'path': tts_paths[index],
                'type': 'spike',
                'chart_type': 'column-detail',
                'chart_colors': ['#AAAAAA', '#3D9970']
            }
            chart_id = 'tts_' + str(index)
            summary_detail = self.init_summary_detail(summary_strings[index], chart_id, detail_params)
            ts_content['container'].append(summary_detail)

        print('End init_top_spikes (returning ts_content)\n\n')

        return ts_content

    def init_top_drops(self):
        """ @brief init_top_spikes
            @description function initializes the Top Traffic Drops Element
            @return td_content: a dictionary containing key, value pairs for the TTD element
        """

        # print('Start init_top_drops')
        ttd = self.analysis.get_top_drops_smry()
        ttd_paths = ttd.index.tolist()

        summary_strings = []

        # ANONYMIZED PATHS
        # path_suffix = 1

        for path in ttd_paths:

            # ANONYMIZED PATHS
            # anonymized_path = 'drop_page ' + str(path_suffix)
            # path_suffix += 1
            # string = str(ttd.ix[path]['Delta_%']) + '% increase in page visits to ' + anonymized_path
            # END ANONYMIZED

            # ACTUAL PATHS
            string = str(ttd.ix[path]['Delta_%']) + '% increase in page visits to ' + path
            # END ACTUAL

            summary_strings.append(string)

        td_content = {
            'title': 'Top Traffic Drops',
            'icon': '/dashboard/static/img/trend_down.svg',
            'container_type': 'accordion',
            'container': []
        }

        for index in range(len(summary_strings)):
            detail_params = {
                'path': ttd_paths[index],
                'type': 'drop',
                'chart_type': 'column-detail',
                'chart_colors': ['#AAAAAA', '#FF4136']
            }
            chart_id = 'ttd_' + str(index)
            summary_detail = self.init_summary_detail(summary_strings[index], chart_id, detail_params)
            td_content['container'].append(summary_detail)

        print('End init_top_drops (returning td_content)\n\n')
        return td_content

    def init_summary_detail(self, summary_str, detail_chart_id, det_params):
        """ @brief init_summary_detail
            @description function initializes the container for summary and detail data for corresponding
                        TTS and TTD items
            @param summary_str: the summary string for the item
            @param detail_chart_id: unique id of the item for chart generation purposes
            @param det_params: a dictionary of chart parameters 
            @return pairing: a dictionary containing the summary and detail for the item
        """
        pairing = {
            'rec_div_id': str(detail_chart_id) + '-modal',
            'rec_container': {
                        'title': str(detail_chart_id) + ' Placeholder Reccommendation',
                        'problem': 'This is a short synopsis of the problem.',
                        'motivation': 'This is why it is good or bad.',
                        'recommendation': 'This is what we think you should do about it.'
                    },
            'chart_summary': summary_str,
            'chart_data': json.dumps(self.build_detail(det_params)),
            'chart_tag': detail_chart_id,
            'chart_div': '<div id="' + detail_chart_id + '"></div>',
            'chart_title': 'Page Views by Referral Source (Previous Month vs. Current Month)',
            'chart_type': det_params['chart_type'],
            'chart_x_lbl': '',
            'chart_y_lbl': 'Page Views',
            'chart_colors': det_params['chart_colors']
        }
        return pairing

    def build_detail(self, params):
        """ @brief build_detail
            @description function generates the detail chart data used by each TTS and TTD detail item
            @param params: a dictionary containing item type data (to distinguish between TTS and TTD items)
            @return: raw_data: a JSON literal dictionary ready for dumping to charts
        """
        raw_data = {'cols': [{'id': 'src',
                              'label': 'Referral Source',
                              'type': 'string'},
                             {'id': 'views_prev',
                              'label': 'Previous Page Views',
                              'type': 'number'},
                             {'id': 'views_curr',
                              'label': 'Current Page Views',
                              'type': 'number'}],
                    'rows': []}

        tts_detail = None

        if params['type'] == 'spike':
            tts_detail = self.analysis.get_top_spikes_src().ix[(params['path'],)]
            tts_detail.sort_values(['Delta'], ascending=False, inplace=True)
        elif params['type'] == 'drop':
            tts_detail = self.analysis.get_top_drops_src().ix[(params['path'],)]
            tts_detail.sort_values(['Delta'], ascending=True, inplace=True)

        srcs = tts_detail.index.tolist()

        for src in srcs:
            data = {'c': [{'v': src},
                          {'v': np.asscalar(tts_detail.ix[src]['ga:pageviews_prev']),
                           'f': np.asscalar(tts_detail.ix[src]['ga:pageviews_prev'])},
                          {'v': np.asscalar(tts_detail.ix[src]['ga:pageviews_curr']),
                           'f': np.asscalar(tts_detail.ix[src]['ga:pageviews_curr'])}
                          ]
                    }

            raw_data['rows'].append(data)

        return raw_data

    def fill_srcs(self):
        """ @brief fill_srcs
            @description function generates the category- and source-level detail for the Traffic Sources element
            @return: rows: a list of category- and source-level dictionaries
        """
        srcs_summary = self.analysis.srcs_summary
        srcs_detail = self.analysis.srcs_detail

        categories = srcs_summary.index.tolist()

        up = '\u2206'
        down = '\u2207'
        inf = '\u221E'

        sessions_change_rate_str = None
        goal_change_rate_str = None

        rows = []
        for category in categories:

            cat_detail = srcs_detail.ix[category]

            # Get list of sources for current category
            sources = cat_detail.index.tolist()

            # Build detail
            detail_rows = []
            for source in sources:

                # Format sessions change rate
                if cat_detail.ix[source]['sessionsChangeRate'] == np.inf:
                    sessions_change_rate_str = inf
                else:
                    if cat_detail.ix[source]['sessionsChangeRate'] < 0:
                        sessions_change_rate_str = down + ' ' + str('{:.2f}%'.format(abs(cat_detail.ix[source]['sessionsChangeRate'])))
                    else:
                        sessions_change_rate_str = up + ' ' + str('{:.2f}%'.format(cat_detail.ix[source]['sessionsChangeRate']))

                # Format goal completions change rate
                if cat_detail.ix[source]['goalCompletionsChangeRate'] == np.inf:
                    goal_change_rate_str = inf
                else:
                    if cat_detail.ix[source]['goalCompletionsChangeRate'] < 0:
                        goal_change_rate_str = down + ' ' + str('{:.2f}%'.format(abs(cat_detail.ix[source]['goalCompletionsChangeRate'])))
                    else:
                        goal_change_rate_str = up + ' ' + str('{:.2f}%'.format(cat_detail.ix[source]['goalCompletionsChangeRate']))

                tmp_row = {
                    'source': source,
                    'sessions': str('{:.0f}'.format(cat_detail.ix[source]['ga:sessions_curr'])),
                    'sessions_delta_p': sessions_change_rate_str,
                    'goal_completions': str('{:.0f}'.format(cat_detail.ix[source]['ga:goalCompletionsAll_curr'])),
                    'goal_completions_delta_p': goal_change_rate_str,
                    'conversion_rate_curr': str('{:.2f}%'.format(cat_detail.ix[source]['goalConversionRateAll_curr'])),
                    'conversion_rate_prev': str('{:.2f}%'.format(cat_detail.ix[source]['goalConversionRateAll_prev']))
                }
                detail_rows.append(tmp_row)

            # Format sessions change rate
            if srcs_summary.ix[category]['sessionsChangeRate'] == np.inf:
                sessions_change_rate_str = inf
            else:
                if srcs_summary.ix[category]['sessionsChangeRate'] < 0:
                    sessions_change_rate_str = down + ' ' + str('{:.2f}%'.format(abs(srcs_summary.ix[category]['sessionsChangeRate'])))
                else:
                    sessions_change_rate_str = up + ' ' + str('{:.2f}%'.format(srcs_summary.ix[category]['sessionsChangeRate']))

            # Format goal completions change rate
            if srcs_summary.ix[category]['goalCompletionsChangeRate'] == np.inf:
                goal_change_rate_str = inf
            else:
                if srcs_summary.ix[category]['goalCompletionsChangeRate'] < 0:
                    goal_change_rate_str = down + ' ' + str('{:.2f}%'.format(abs(srcs_summary.ix[category]['goalCompletionsChangeRate'])))
                else:
                    goal_change_rate_str = up + ' ' + str('{:.2f}%'.format(srcs_summary.ix[category]['goalCompletionsChangeRate']))

            tmp_row = {
                'group_name': category,
                'sessions': str('{:.0f}'.format(srcs_summary.ix[category]['ga:sessions_curr'])),
                'sessions_delta_p': sessions_change_rate_str,
                'goal_completions': str('{:.0f}'.format(srcs_summary.ix[category]['ga:goalCompletionsAll_curr'])),
                'goal_completions_delta_p': goal_change_rate_str,
                'conversion_rate_curr': str('{:.2f}%'.format(srcs_summary.ix[category]['goalConversionRateAll_curr'])),
                'conversion_rate_prev': str('{:.2f}%'.format(srcs_summary.ix[category]['goalConversionRateAll_prev'])),
                'src_detail': detail_rows
            }
            rows.append(tmp_row)

        return rows

    def init_sources(self):
        """ @brief init_sources
            @description function initializes the Traffic Sources element
            @return: srcs_content: a dictionary containing key, value pairs for the SRCS element
        """
        srcs_content = self.generic_element_content.copy()
        srcs_content['title'] = 'Traffic Sources'
        srcs_content['position'] = 4
        srcs_content['block_id'] = 'srcs'
        srcs_content['container_type'] = 'list'
        srcs_content['container'] = {
            'columns': ['Source',
                        'Sessions (curr)',
                        '% Change (Sessions)',
                        'Goal Completions (curr)',
                        '% Change (Completions)',
                        'Conversion Rates (curr)',
                        'Conversion Rates (prev)'
                        ],
            'rows': self.fill_srcs()
        }
        return srcs_content

    def init_bounce_rates(self):
        """ @brief init_bounce_rates
            @description function initializes the Bounce Rates element
            @return: br_content: a dictionary containing key, value pairs for the BR element
        """

        # print('Start init_bounce_rates')

        br_content = self.generic_element_content.copy()
        br_content['title'] = 'Bounce Rates'
        br_content['icon'] = '/dashboard/static/img/ic_lightbulb.svg'
        br_content['position'] = 3
        br_content['block_id'] = 'br'
        br_content['container_type'] = 'accordion_v2'
        br_content['container'] = self.fill_br()

        print('End init_bounce_rates (returning br_content)\n\n')
        return br_content


    def fill_br(self):
        """ @brief fill_br
            @description function initializes the Bounce Rates element
            @return: br_content: a dictionary containing key, value pairs for the BR element
        """

        # Create the JSON columns for the chart
        br_raw_data = {
            'cols': [
                {'id': 'ppath','label': 'Full Page URL','type': 'string'},
                {'id': 'br_curr','label': 'Bounce Rate','type': 'number'},
                {'type': 'string', 'p': {'role': 'style'}}
                ],
            'rows': []}

        # Get the dataframe of high bounce rates
        br_data_high = self.analysis.highest_n_br
        br_data_high.to_csv('br_data_hight.csv')

        # Get the dataframe of low bounce rates
        br_data_low = self.analysis.lowest_n_br
        br_data_low.to_csv('br_data_low.csv')

        # Put them in a list of dataframes
        dfs = [br_data_high, br_data_low]

        # Concatenate the dataframes into one dataframe
        #br_data = pd.concat(dfs)
        br_data = br_data_high.append(br_data_low)
        br_data.to_csv('br_data.csv')

        # Get the referral sources dataframe of high bounce rates
        br_rs_data_high = self.analysis.highest_n_br_src

        # Get the referral sources dataframe of low bounce rates
        br_rs_data_low = self.analysis.lowest_n_br_src

        # Put them in a list of dataframes
        dfs_rs = [br_rs_data_high, br_rs_data_low]

        # Concatenate the dataframes into one dataframe
        #br_rs_data = pd.concat(dfs_rs)
        br_rs_data = br_rs_data_high.append(br_rs_data_low)
        br_rs_data.to_csv('br_rs_data.csv')

        # Assign br data to variables
        paths = br_data.index.tolist()

        path_suffix = 1

        br_detail = []
        short_names = []

        # Put the chart data & detail together
        for path in paths:
            s_name = 'page ' + str(path_suffix)
            short_names.append(s_name)
            off_avg = np.asscalar(br_data.ix[path]['fromAvrg%'])
            if off_avg > 0:
                recommendation_tag = 'How to fix this...'
                style = 'color: #bd342d'
            else:
                recommendation_tag = 'How to improve this...'
                style = 'color: #3D9970'

            srcs = br_rs_data.ix[(path,)]
            srcs_list = srcs.index.tolist()
            src_data_list = []

            for src in srcs_list:
                rs_container = {
                    'src_name': src,
                    'src_bounce_rate': "{:.1f}%".format(srcs.ix[src]['bounceRate']),
                    'src_off_average': "{:.1f}%".format(srcs.ix[src]['fromAvrg%']),
                    'src_conversion_rate': "{:.1f}%".format(srcs.ix[src]['goalConversionRateAll'])
                }
                src_data_list.append(rs_container)

            chart_data = {
                'c': [
                    # ANONYMIZED PATH
                    # {'v': s_name, 'f': s_name},
                    # ACTUAL PATH
                    {'v': path, 'f': path},
                    {'v': np.asscalar(br_data.ix[path]['fromAvrg%']), 'f': np.asscalar(br_data.ix[path]['bounceRate'])},
                    {'v': style},
                    ]}

            detail = {
                'short_name': s_name,
                # ANONYMIZED PATH
                # 'long_name': s_name,
                # ACTUAL PATH
                'long_name': path,
                'bounce_rate': "{:.1f}%".format(np.asscalar(br_data.ix[path]['bounceRate'])),
                'off_average': "{:.1f}%".format(off_avg),
                'conversion_rate': "{:.1f}%".format(np.asscalar(br_data.ix[path]['goalConversionRateAll'])),
                'show_hide_tag': '<a class="show-hide-srcs" href="#"></a>',
                'rec_tag': recommendation_tag,
                'rec_container': {
                        'title': s_name + ' Placeholder Reccommendation',
                        'problem': 'This is a short synopsis of the problem.',
                        'motivation': 'This is why it is good or bad.',
                        'recommendation': 'This is what we think you should do about it.'
                    },
                'srcs_container': {
                    # ANONYMIZED PATH
                    # 'url': s_name,
                    # ACTUAL PATH
                    'url': path,
                    'srcs_data': src_data_list
                }
            }
            br_raw_data['rows'].append(chart_data)
            br_detail.append(detail)
            path_suffix += 1

        # Put the summary text string together
        site_wide_avg = np.asscalar(br_data.ix[0]['bounceRate'] - br_data.ix[0]['fromAvrg%'])
        swa_str = str("{:.2f}".format(site_wide_avg)) + '% Average Bounce Rate for pages connected to this web presence'

        # Put the y-ticks together
        upper_factor = (100 - site_wide_avg) / 2
        lower_factor = site_wide_avg / 2
        tmp_ticks = [str("{:.2f}".format(0)),
                     str("{:.2f}".format(lower_factor)),
                     str("{:.2f}".format(site_wide_avg)),
                     str("{:.2f}".format(site_wide_avg + upper_factor)),
                     str("{:.2f}".format(100))]

        # print(swa_str)

        br_container = {
            'chart_summary':  swa_str,
            'chart_data': json.dumps(br_raw_data),
            'chart_tag': 'br-summary',
            'chart_div': '<div id="br-summary"></div>',
            'chart_title': 'Extraordinary Bounce Rates by Page URL (Current Month)',
            'chart_type': 'column-summary',
            'chart_x_lbl': '',
            'chart_x_ticks': short_names,
            'chart_y_lbl': '- lower --- ' + "{:.2f}".format(site_wide_avg) + '% --- higher +',
            'chart_y_ticks': tmp_ticks,
            'chart_colors': ['#AAAAAA', '#FF4136'],
            'page_detail': br_detail,
            'page_detail_columns': [
                "Page", "Bounce Rate", "Above/Below Average", "Conversion Rate",
                "Show/Hide Sources", "Recommendations"
            ]
        }

        return br_container

    def init_top_n(self):
        """ @brief init_top_n
            @description function initializes the Top N Pages element
            @description NOTE: THIS ELEMENT IS NOT INCLUDED IN DASHBOARD VERSION 1
            @return: tn_content: a dictionary containing key, value pairs for the TNP element
        """

        # print('Start init_top_n')

        tn_content = self.generic_element_content.copy()
        tn_content['title'] = 'Top 10 Pages'
        tn_content['icon'] = '/dashboard/static/img/ic_lightbulb.svg'
        tn_content['position'] = 6
        tn_content['block_id'] = 'tp10'
        tn_content['container_type'] = 'list'
        tn_content['container'] = {}

        # print('End init_top_n (returning tn_content)\n\n')

        return tn_content
