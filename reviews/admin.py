from django.contrib import admin
from django.db.models import Q

from common.models import Review, FandomFanfic


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'fanfic', 'score', 'date',
                    'text')
    list_filter = ('user', 'fanfic')

    search_fields = ('user__username', 'text')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_search_results(self, request, queryset, search_term):
        """ When searching of filtering"""
        queryset, use_distinct = super(ReviewAdmin,
                                       self).get_search_results(request,
                                                                queryset,
                                                                search_term)
        if search_term:
            # The user has searched something
            filter_by_fanfic = False
            reviews = None
            if "fanfic__id__exact" in request.GET:
                # filter by fanfic
                fanfic_id_filter = request.GET.get("fanfic__id__exact")
                if fanfic_id_filter:
                    filter_by_fanfic = True
                    reviews = Review.objects.filter(
                        fanfic__id=fanfic_id_filter)

            if "user__id__exact" in request.GET:
                # filter by user
                user_id_filter = request.GET.get("user__id__exact")
                if user_id_filter:
                    if reviews:
                        reviews = reviews.filter(user__id=user_id_filter)
                    else:
                        reviews = Review.objects.filter(
                            user__id=user_id_filter)

            if filter_by_fanfic is False:
                fanfics = FandomFanfic.objects.filter(
                    Q(fanfic__name__icontains=search_term) | Q(
                        fandom__name__icontains=search_term)).values_list(
                    'fanfic__id', flat=True)

                if reviews:
                    reviews = reviews.filter(fanfic__id__in=fanfics)
                else:
                    reviews = Review.objects.filter(fanfic__id__in=fanfics)
                queryset = queryset | reviews
                queryset = queryset.distinct()

        return queryset, use_distinct
