import logging
import re

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect
from common.models import Fanfic as fanfic_model

# Create your views here.
from common.models import Review
from common.utils import CustomError
from common.views import BaseView

# Get an instance of a logger
from notifier.models import Notification

logger = logging.getLogger(__name__)


class ReviewView(LoginRequiredMixin, BaseView):
    """ Manage review """

    def get(self, request, review_id=None):
        """ Get edit page for review """
        if review_id is None:
            raise PermissionDenied()
        review = get_object_or_404(Review, id=review_id)
        fanfic = review.fanfic

        if review.user != request.user:
            # It's not the same user
            raise PermissionDenied()

        return render(request, 'review.html', context={
            'fanfic': fanfic, 'text': review.text, 'stars': int(review.score),
            'edit': 'edit'})

    def put(self, request, review_id=None):
        """ Update review """
        if "review_id" is None:
            raise PermissionDenied()
        try:
            with transaction.atomic():
                user = self.request.user
                review = get_object_or_404(Review, id=review_id)
                text = request.POST.get("text")
                stars = int(request.POST.get("stars"))

                if stars < 0 or stars > 5:
                    raise PermissionDenied()

                if not text:
                    # is empty, return error message
                    raise CustomError("The text cannot be empty")
                else:
                    pattern = re.compile(r'<[^>]+>')
                    text_without_html = pattern.sub('', text)
                    text_without_html = text_without_html.replace(
                        "&nbsp;", "").replace(" ", "")
                    if len(text_without_html) == 0:
                        raise CustomError("The text cannot be empty")

                if len(text) > 7000:
                    # text too long, return error message
                    raise CustomError("The text is too long. It should be "
                                      "less than 7000 characters.")

                # update the review
                review.text = text
                review.score = stars
                review.save()

                # recalculate fanfic score
                fanfic_new_score = Review.objects.filter(
                    fanfic=review.fanfic).aggregate(Avg(
                    'score'))
                fanfic_new_score = round(fanfic_new_score['score__avg'], 2)
                fanfic = review.fanfic
                fanfic.average_score = fanfic_new_score
                fanfic.save()

                # redirect to the fanfic page
                logger.info("Review updated for user {}".format(user))
                messages.success(request, "The review has been successfully "
                                          "updated.")
                return redirect('reviews:reviews', review_id=review_id)
        except CustomError as e:
            messages.error(request, e)
            logger.error("Error updating review {}".format(e))
            return render(request, 'review.html',
                          context={'text': text, 'fanfic': review.fanfic,
                                   'stars': int(review.score), 'edit': 'edit'})
        except Exception as e:
            messages.error(request,
                           "There was an unexpected error trying to\
                            update the review.")
            logger.error("Error updating review {}".format(e))
            return render(request, 'review.html',
                          context={'text': text, 'fanfic': review.fanfic,
                                   'stars': int(review.score), 'edit': 'edit'})


class ReviewsView(LoginRequiredMixin, BaseView):
    """ Manage reviews """

    def get(self, request, review_id=None):
        """ See a review """
        if review_id is None:
            raise PermissionDenied()
        review = get_object_or_404(Review, id=review_id)
        fanfic = review.fanfic

        return render(request, 'review.html', context={
            'fanfic': fanfic, 'review': review})

    def post(self, request):
        """ Create new review """
        if "fanfic_id" not in request.POST:
            raise PermissionDenied()

        try:
            with transaction.atomic():
                user = self.request.user
                fanfic_id = request.POST.get("fanfic_id")

                fanfic = get_object_or_404(fanfic_model, id=fanfic_id)

                text = request.POST.get("text")
                stars = int(request.POST.get("stars"))

                if stars < 0 or stars > 5:
                    raise PermissionDenied()

                if Review.objects.filter(user=user,
                                         fanfic=fanfic).exists() is True:
                    # this user already has a review, error msg
                    raise CustomError("You already have "
                                      "posted a review for this fanfic.")

                if not text:
                    # is empty, return error message
                    raise CustomError("The text cannot be empty")
                else:
                    pattern = re.compile(r'<[^>]+>')
                    text_without_html = pattern.sub('', text)
                    text_without_html = text_without_html.replace(
                        "&nbsp;", "").replace(" ", "")
                    if len(text_without_html) == 0:
                        raise CustomError("The text cannot be empty")

                if len(text) > 7000:
                    # text too long, return error message
                    raise CustomError("The text is too long. It should be "
                                      "less than 7000 characters.")

                # create the review
                review = Review.objects.create(text=text, score=stars,
                                               fanfic=fanfic,
                                               user=user)

                # recalculate fanfic score
                fanfic_new_score = Review.objects.filter(
                    fanfic=fanfic).aggregate(Avg(
                    'score'))
                fanfic_new_score = round(fanfic_new_score['score__avg'], 2)
                fanfic.average_score = fanfic_new_score
                fanfic.save()

                # create notification
                Notification.objects.create(
                    subject=fanfic, verb="has reviewed", target=user,
                    link=review.get_url(),
                    reverse=True,
                    in_top_bar=False, in_feed=True)

                # redirect to the fanfic page
                logger.info("Review created for user {}".format(user))
                messages.success(request, "The review has been successfully "
                                          "created.")
                return redirect('fanfics:fanfic', fanfic_id=fanfic_id)

        except CustomError as e:
            messages.error(request, e)
            logger.error("Error creating review {}".format(e))
            if not fanfic:
                raise PermissionDenied()
            return render(request, 'review.html',
                          context={'text': text, 'fanfic': fanfic,
                                   'stars': int(stars)})
        except Exception as e:
            messages.error(request,
                           "There was an unexpected error trying to\
                            save the review.")
            logger.error("Error creating review {}".format(e))
            if not fanfic:
                raise PermissionDenied()
            return render(request, 'review.html',
                          context={'text': text, 'fanfic': fanfic,
                                   'stars': int(review.score)})

    def delete(self, request, review_id=None):
        """ Delete a review """
        if review_id is None:
            raise PermissionDenied()

        try:
            with transaction.atomic():
                review = get_object_or_404(Review, id=review_id)
                fanfic = review.fanfic
                if review.user != request.user:
                    raise PermissionDenied()
                review.delete()

                messages.success(request, "The review has been successfully "
                                          "deleted")
                return redirect(fanfic.get_url())
        except CustomError as e:
            messages.error(request, e)
            logger.error("Error deleting review {}".format(e))
            return redirect('reviews:reviews', review_id=review_id)
        except Exception as e:
            messages.error(request,
                           "There was an unexpected error trying to\
                            delete the review.")
            logger.error("Error deleting review {}".format(e))
            return redirect('reviews:reviews', review_id=review_id)
