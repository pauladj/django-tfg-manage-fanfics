# import the logging library
import logging
import traceback

from celery.schedules import crontab
from celery.task import periodic_task
from django.db import transaction

# Get an instance of a logger
from analyzer.custom_models import Recommender

logger = logging.getLogger(__name__)


@periodic_task(run_every=crontab(minute=0, hour='*/72'))
def run_recommender_system():
    """ Update the recommender data """
    try:
        with transaction.atomic():
            recommender_system = Recommender()
            recommender_system.start()

    except Exception as e:
        logger.error(
            "Error in celery task creating recommender {}".format(e))
        logger.error(traceback.print_exc())
