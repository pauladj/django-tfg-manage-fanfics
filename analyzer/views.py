from datetime import datetime, timedelta

import pandas as pd
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
# Create your views here.
from matplotlib.ticker import MaxNLocator

from common.models import FandomFanfic, FanficList
from common.views import BaseView


class AnalyticsView(BaseView):

    def get(self, request):
        """ See analytics dashboard """
        if request.user.is_superuser is False:
            raise PermissionDenied()

        try:
            times_added_fandoms_image_path = \
                self.number_of_times_added_fandoms_image()
            times_added_genres_image_path = \
                self.number_of_times_added_genre_image()
            return render(
                request, 'analytics-dashboard.html',
                {
                    'times_added_fandoms': times_added_fandoms_image_path,
                    'times_added_genres': times_added_genres_image_path})
        except Exception:
            messages.error(request, 'There is not enough data to create the '
                                    'graphs.')
            return render(request, 'analytics-dashboard.html',
                          {'error': True})

    def number_of_times_added_fandoms_image(self):
        """ Generate the graph times added /fandom last month"""
        last_month = datetime.today() - timedelta(days=30)

        fanfic_lists_data = FanficList.objects.filter(
            date__gte=last_month).exclude(
            list__user__gender__isnull=True).values(
            'fanfic__id', 'list__user__gender')
        fandom_fanfics_data = FandomFanfic.objects.filter(
            is_primary=True).values('fanfic__id', 'fandom__name')

        if fanfic_lists_data.count() > 0 and fandom_fanfics_data.count() > 0:
            df_fanfic_lists = pd.DataFrame.from_records(fanfic_lists_data)
            df_fandom_fanfics = pd.DataFrame.from_records(fandom_fanfics_data)

            merged = pd.merge(df_fandom_fanfics, df_fanfic_lists,
                              on='fanfic__id',
                              how='left')
            merged.columns = ['fandom', 'fanfic_id', 'gender']
            merged.dropna(axis=0, how='any', inplace=True)

            pivot_table = merged.pivot_table(index='fandom', columns='gender',
                                             values='fanfic_id',
                                             aggfunc='count').fillna(0)

            path = "media/analytics/times_added_fandoms.png"
            ax = pivot_table.plot(kind='bar')
            ax.set_ylabel("Number of fanfics added to lists")
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            figure = ax.figure
            figure.savefig(path,
                           bbox_inches="tight")
            return "/" + path
        else:
            raise Exception()

    def number_of_times_added_genre_image(self):
        """ Generate the graph times added /genre last month"""
        last_month = datetime.today() - timedelta(days=30)

        fanfic_lists_data = FanficList.objects.filter(
            date__gte=last_month).exclude(
            list__user__gender__isnull=True)
        data = fanfic_lists_data.values(
            'fanfic__id', 'list__user__gender')

        if fanfic_lists_data.count() > 0 and data.count() > 0:
            one = fanfic_lists_data.values('fanfic__id', 'fanfic__genre1')
            two = fanfic_lists_data.values('fanfic__id', 'fanfic__genre2')
            three = fanfic_lists_data.values('fanfic__id', 'fanfic__genre3')
            four = fanfic_lists_data.values('fanfic__id', 'fanfic__genre4')

            data = pd.DataFrame.from_records(data)
            one = pd.DataFrame.from_records(one)
            two = pd.DataFrame.from_records(two)
            three = pd.DataFrame.from_records(three)
            four = pd.DataFrame.from_records(four)

            data.columns = ['fanfic_id', 'gender']
            one.columns = ['genre', 'fanfic_id']
            two.columns = ['genre', 'fanfic_id']
            three.columns = ['genre', 'fanfic_id']
            four.columns = ['genre', 'fanfic_id']

            genres = one.append(two).append(three).append(four)
            genres.drop_duplicates(inplace=True)

            merged = pd.merge(data, genres, on='fanfic_id',
                              how='inner')

            column = merged['genre']
            column.replace('adv', 'adventure', inplace=True)
            column.replace('ang', 'angst', inplace=True)
            column.replace('dra', 'drama', inplace=True)
            column.replace('fri', 'friendship', inplace=True)
            column.replace('gen', 'general', inplace=True)
            column.replace('hum', 'humor', inplace=True)
            column.replace('hur', 'hurt/comfort', inplace=True)
            column.replace('mys', 'mystery', inplace=True)
            column.replace('rom', 'romance', inplace=True)
            column.replace('tra', 'tragedy', inplace=True)
            column.replace('hor', 'horror', inplace=True)
            column.replace('fan', 'fantasy', inplace=True)

            merged.dropna(axis=0, how='any', inplace=True)

            pivot_table = merged.pivot_table(index='genre', columns='gender',
                                             values='fanfic_id',
                                             aggfunc='count').fillna(0)

            path = "media/analytics/times_added_genres.png"
            ax = pivot_table.plot(kind='bar')
            ax.set_ylabel("Number of fanfics added to lists")
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            figure = ax.figure
            figure.savefig(path,
                           bbox_inches="tight")
            return "/" + path
        else:
            raise Exception()
