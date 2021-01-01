# import the logging library
import logging
import traceback
from datetime import datetime

from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from django.db import transaction

from fanfics.custom_models import FanficWeb as Fanfic
from notifier.models import Notification
from users.models import CustomUser
from .models import Fanfic as fanfic_model, Chapter

# Get an instance of a logger
logger = logging.getLogger(__name__)


@periodic_task(run_every=crontab(minute=0, hour='*/6'))
def update_chapters_of_fanfics():
    """ Check if some fanfics have been updated, aka have new chapters"""
    fanfics_to_update = fanfic_model.objects.filter(
        complete=False).order_by('last_time_checked')
    how_many = round(fanfics_to_update.count() / 2) + 1
    if how_many > 0:
        fanfics_to_update = fanfics_to_update[:how_many]

        for one_fanfic in fanfics_to_update:
            current_chapters_count = one_fanfic.get_num_of_chapters()
            try:
                with transaction.atomic():
                    fanfic_obj = Fanfic(one_fanfic.web)
                    fanfic_obj.set_appropiate_scraper()
                    page = fanfic_obj.load_page_html()
                    if page is not None:
                        chapters = fanfic_obj.get_chapters()

                        if chapters and len(chapters) > current_chapters_count:
                            # chapters is not empty
                            last_number_chapter = Chapter.objects.filter(
                                fanfic=one_fanfic).order_by(
                                '-num_chapter')
                            if last_number_chapter.exists():
                                last_number_chapter = last_number_chapter. \
                                    first()
                                last_number = last_number_chapter.num_chapter
                                num_chapter_new = last_number + 1

                                if "ficwad" in fanfic_obj.get_site() and \
                                        current_chapters_count == 1:
                                    # it's from ficwad
                                    last_number_chapter.url_chapter = \
                                        chapters[0]['url']
                                    last_number_chapter.save()
                            else:
                                # there weren't any chapters
                                num_chapter_new = 1

                            index_start = current_chapters_count
                            while index_start < len(chapters):
                                # for every new chapter
                                new_chapter = chapters[index_start]
                                Chapter.objects.create(
                                    fanfic=one_fanfic,
                                    title=new_chapter['title'],
                                    num_chapter=num_chapter_new,
                                    url_chapter=new_chapter['url'])
                                index_start += 1
                                num_chapter_new += 1

                            # update word count & status(complete, in progress)
                            word_count = fanfic_obj.get_num_words()
                            status = fanfic_obj.get_status()
                            one_fanfic.num_words = word_count
                            one_fanfic.complete = status
                            one_fanfic.last_time_updated = fanfic_obj. \
                                get_last_time_updated()

            except Exception as e:
                logger.error(
                    "Error in celery task updating chapters {}".format(e))
                logger.error(traceback.print_exc())

            one_fanfic.last_time_checked = datetime.now()
            one_fanfic.save()


@task(name="scrape_and_add_fanfic", max_retries=5)
def scrape_and_add_fanfic(url, current_user):
    """ Add task to queue, this task scrapes the fanfic website
        adds the fanfic to the system with the data. When it's
        done the user is notified so they can configure the data.
    """
    try:
        new_fanfic = Fanfic(url)
        cleaned_url = new_fanfic.get_cleaned_url()
        fanfic_in_sys = fanfic_model.objects.filter(
            web__icontains=cleaned_url)
        url_in_system = fanfic_in_sys.exists()
        number_of_retries_done = int(scrape_and_add_fanfic.request.retries)

        user = CustomUser.objects.get(id=current_user)

        subject = CustomUser.objects.filter(
            username="Fickeeper").first()

        if url_in_system is True:
            # notify user
            already_existing_fanfic = fanfic_in_sys.first()
            send_notification(already_existing_fanfic, user,
                              "has already been added,",
                              already_existing_fanfic.get_url())
        else:
            new_fanfic.set_appropiate_scraper()
            page = new_fanfic.load_page_html()
            if page is None:
                if number_of_retries_done == 5:
                    send_notification(subject, user,
                                      "has encountered a problem trying "
                                      "to add the "
                                      "fanfic you specified,",
                                      url)
                raise Exception("Error fetching fanfic page")
            else:
                is_fanfic = new_fanfic.check_if_is_fanfic_or_chapter()
                if is_fanfic is False:
                    # it's a chapter
                    send_notification(subject, user,
                                      "has encountered a problem trying "
                                      "to add the "
                                      "fanfic you specified,",
                                      url)
                else:
                    created_fanfic = new_fanfic.scrape_and_save()
                    send_notification(subject, user,
                                      "has added successfully the "
                                      "fanfic you specified,",
                                      created_fanfic.get_url())
    except Exception as e:
        logger.error("Error in celery task scraping website {}".format(e))
        logger.error(traceback.print_exc())
        scrape_and_add_fanfic.retry(exc=e,
                                    countdown=60)


def send_notification(subject, target, verb, link):
    """ Send notification """
    Notification.objects.create(
        subject=subject,
        verb=verb,
        target=target,
        link=link,
        in_top_bar=True, in_feed=False)
