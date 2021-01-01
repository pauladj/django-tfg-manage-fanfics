import datetime
import logging
import re

import requests
from bs4 import BeautifulSoup
from django.db import transaction

from common.models import (Fanfic as fanfic_model, Fandom, FandomFanfic, Type,
                           Character,
                           CharacterFanfic, Chapter)
from common.utils import clean_string
from fickeep.settings import FANFIC_PASSWORD, FANFIC_USERNAME

logger = logging.getLogger(__name__)


class Fetcher():

    @staticmethod
    def fetch_page(url, auth_url, cookie_name):
        """ Get the html of the url """
        connect_timeout = 30.0
        read_timeout = 100.0
        cookies = None
        try:
            if auth_url is not None:
                data = {'username': FANFIC_USERNAME,
                        'password': FANFIC_PASSWORD}
                r = requests.post(auth_url, data=data)
                session_cookie = r.cookies.get(cookie_name)

                cookies = {cookie_name: session_cookie}

            page = requests.get(url, cookies=cookies,
                                timeout=(connect_timeout, read_timeout)).text
            page_html = BeautifulSoup(page, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error("Error fetching the page of the fanfic {}".format(e))
            page_html = None
        return page_html


class Scraper:
    def __init__(self):
        self.page_html = None

    def set_page_html(self, page_html):
        """ Set the page html """
        self.page_html = page_html

    def get_page_html(self):
        """ Get the page html """
        return self.page_html


class AvengersFanfictionScraper(Scraper):

    def get_title_and_author(self):
        """ Parse html to get title and author """
        title = self.get_page_html().find('h1').get_text(strip=True)
        page_html = self.get_page_html().find('div', id='sidebar')
        author = page_html.find('h3').get_text(strip=True)
        return title, author

    def get_fandom_and_media_type(self):
        """ Get the fandom and media type """
        return "Avengers", "movies"

    def get_language(self):
        """ Get language """
        return

    def get_genres(self):
        """ Get genres """
        return []

    def get_status(self):
        """ Get status """
        return False

    def get_last_time_updated(self):
        """ Get last time updated """
        return

    def get_chapters(self):
        """ Get the chapters """
        page_html = self.get_page_html().find('div', id="chapters")
        chapters = []
        if page_html:
            chapters_html = page_html.find_all('ol')
            if chapters_html:
                chapters_html = chapters_html[0].find_all('li')

                cont = 1
                for li in chapters_html:
                    chapter_obj = {}
                    chapter_obj["title"] = li.find_all('h3')[0].text
                    chapter_obj["num"] = cont
                    chapter_obj["url"] = li.find_all(
                        'h3')[0].find_all('a')[0]['href']
                    chapters.append(chapter_obj)
                    cont += 1

        return chapters

    def get_num_words(self):
        """ Get number of words """
        return

    def get_rating(self):
        """ Get rating """
        return

    def get_characters(self):
        """ Get characters """
        return []

    def get_auth_data(self):
        """ Get data to send log in data """
        return None, None

    def check_if_is_fanfic_or_chapter(self):
        """ Check if the url is a fanfic or a chapter """
        page_html = self.get_page_html().find('div', id="chapter")
        if page_html is None:
            # does not exists, so it's a fanfic
            return True
        return False


class FicWadScraper(Scraper):

    def get_title_and_author(self):
        page_html = self.get_page_html().find('div', id="story")
        title = page_html.find('h4').text.lstrip().rstrip()
        author_with_by = page_html.find_all('span', 'author')[0].text
        author = author_with_by.split('by ', 1)[1].lstrip().rstrip()
        return title, author

    def get_fandom_and_media_type(self):
        """ Get the fandom and media type """
        page_html = self.get_page_html().find('div', id="story")
        info = page_html.find_all('p', 'meta')[0].text  # first occurrence

        regex = re.search('(Category:(?P<fandom>.*?)-).*', info)
        fandom = regex.group('fandom')  # exception if no fandom
        fandom = fandom.rstrip().lstrip()
        if len(fandom) == 0:
            fandom = 'other'

        info = page_html.find_all('h2')[0].text  # first occurrence

        regex = re.search('.*?>(?P<type>.*?)>.*?', info)
        media_type = regex.group('type')
        media_type = media_type.strip().lower()

        if "anime" in media_type:
            media_type = "anime"
        elif (media_type == "books" or media_type == "cartoons" or
              media_type == "comics" or media_type == "games" or
              media_type == "movies" or media_type == "tv"):
            pass
        elif media_type == "theatre":
            media_type = "plays"
        else:
            media_type = "other"

        return fandom, media_type

    def get_language(self):
        return

    def get_genres(self):
        """ Get genres """
        page_html = self.get_page_html().find('div', id="story")
        info = page_html.find_all('p', 'meta')[0].text  # first occurrence

        regex = re.search('(Genres:(?P<genres>.*?)- ).*', info)
        if regex:
            info = regex.group('genres')
            info = info.strip().lower()

            if "sci-fi" in info and "fantasy" not in info:
                info = info.replace("sci-fi", "fantasy")
            genres = info.split(",")
            genres_list = []
            for genre in genres:
                if fanfic_model.is_genre_option(genre) is True:
                    genres_list.append(genre)
            return genres
        return []

    def get_status(self):
        """ Get status """
        page_html = self.get_page_html().find('div', id="story")
        info = page_html.find_all('p', 'meta')[0].text  # first occurrence

        regex = re.search('Complete', info)
        if regex:
            return True
        else:
            return False

    def get_last_time_updated(self):
        """ Get last time updated """
        page_html = self.get_page_html().find('div', id="story")
        info = page_html.find_all('p', 'meta')[0].text  # first occurrence
        date = None
        regex = re.search('(Updated:(?P<updated>.*?) -).*', info)
        if regex:  # the story has been updated
            date = regex.group('updated').rstrip().lstrip()
            date = date.strip()
        else:  # the story has not been updated
            regex = re.search('(Published:(?P<published>.*?) -).*', info)
            if regex:
                date = regex.group('published').rstrip().lstrip()
                date = date.strip()

        if date is None:
            return

        if "hour" in date or "minute" in date or "second" in date:
            date_time_obj = datetime.datetime.now()
        else:
            date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date_time_obj

    def get_chapters(self):
        """ Get the chapters """
        chapters_html = self.get_page_html().find('div', id="chapters")
        if chapters_html:
            chapters_html = chapters_html.find_all('ul', 'storylist')[0]
            chapters_html = chapters_html.find_all('li')
        else:
            # just one chapter
            chapters_html = self.get_page_html().find_all('div', 'storylist')

        chapters = []
        cont = 1
        for li in chapters_html:
            chapter_obj = {}
            chapter_obj["title"] = li.find_all('h4')[0].text.lstrip().rstrip()
            chapter_obj["num"] = cont
            chapter_obj["url"] = "https://ficwad.com" + li.find_all(
                'h4')[0].find_all(
                'a')[0]['href'].rstrip().lstrip()
            chapters.append(chapter_obj)
            cont += 1

        return chapters

    def get_num_words(self):
        """ Get number of words """
        page_html = self.get_page_html().find('div', id="story")
        info = page_html.find_all('p', 'meta')[0].text  # first occurrence
        words = None
        regex = re.search('.*- (?P<words>\d+).*words.*', info)
        if regex:  # the story has been updated
            words = regex.group('words')
            words = words.strip()

        return words

    def get_rating(self):
        """ Get rating """
        page_html = self.get_page_html().find('div', id="story")
        info = page_html.find_all('p', 'meta')[0].text  # first occurrence

        rating = None
        warning = None
        regex = re.search('(Rating:(?P<rating>.*?) -).*', info)
        if regex:
            rating = regex.group('rating')
            rating = rating.strip().lower()

        regex = re.search('(Warnings:(?P<warnings>.*?) -).*', info)
        if regex:
            warning = regex.group('warnings')
            warning = rating.strip().lower()
            regex = re.search('\[([X|V|R|Y])\]', warning)
            if regex:
                rating = "M"
                return rating

        if rating == "g":
            rating = "K"
        elif rating == "pg":
            rating = "K+"
        elif rating == "pg-13":
            rating = "T"
        elif rating == "r" or rating == "nc-17":
            rating = "M"

        return rating

    def get_characters(self):
        """ Get characters """
        page_html = self.get_page_html().find('div', id="story")
        info = page_html.find_all('p', 'meta')[0].text  # first occurrence

        characters = []
        regex = re.search('(Characters:(?P<characters>.*?)-).*', info)
        if regex:
            characters = regex.group('characters').rstrip().lstrip()
            characters = characters.split(",")
        return characters

    def get_auth_data(self):
        """ Get site data to send log in data """
        return "https://ficwad.com/account/login", "ficwad2_session"

    def check_if_is_fanfic_or_chapter(self):
        """ Check if the url is a fanfic or a chapter """
        page_html = self.get_page_html().find_all('form', class_="chapterlist")
        if len(page_html) > 0:
            # exists, so it's a chapter
            return False
        return True


class ArchiveOfOurOwnScraper(Scraper):

    def get_title_and_author(self):
        title = self.get_page_html().find_all('h2', 'title')[0].get_text(strip=True)
        author = self.get_page_html().find_all('h3', 'byline')[0].get_text(strip=True)
        return title, author

    def get_fandom_and_media_type(self):
        """ Get the fandom and media type """
        info = self.get_page_html().select('dd.fandom.tags')[0].find_all(
            'ul')[0].find_all('li')
        media_type = None
        for li in info:
            one_fandom = li.select('a')[0].text.rstrip().lstrip()

            if "(tv)" in one_fandom.lower():
                media_type = "tv"
            elif "movie" in one_fandom.lower():
                media_type = "movies"
            elif "series" in one_fandom.lower():
                media_type = "books"
                one_fandom = re.sub(r"\s+[S|s]eries.*", "", one_fandom)

            one_fandom = re.sub(r"\s*-\s*.*", "", one_fandom)

            if media_type is not None:
                return one_fandom, media_type

        media_type = "other"
        fandom = info[0].select('a')[0].text.lower().rstrip().lstrip()
        fandom = re.sub(r"\s*-\s*.*", "", fandom)
        return fandom, media_type

    def get_language(self):
        """ Get the language """
        language = self.get_page_html().select('dd.language')[0].text.strip()
        return language

    def get_genres(self):
        """ Get genres """
        genres_list = []
        genres = self.get_page_html().select('dd.freeform.tags')
        if genres:
            genres = genres[0].find_all('ul', 'commas')[0].find_all('li')

        for li in genres:
            genre = li.find('a').text.strip().lower()
            if fanfic_model.is_genre_option(genre) is True:
                genres_list.append(genre)
        return genres_list

    def get_status(self):
        """ Get status """
        status = self.get_page_html().select('dl.stats')[0].find_all(
            'dd', 'chapters')[0].text.strip()
        if "?" in status:
            return False
        else:
            return True

    def get_last_time_updated(self):
        """ Get last time updated """
        info = self.get_page_html().select('dl.stats')[0]

        if "Updated" in info:
            # the story has been updated
            date = info.select('dd.status')[0].text.strip()
        else:
            # the story has not been updated
            date = info.select('dd.published')[0].text.strip()

        if date is None:
            return

        date_time_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date_time_obj

    def get_chapters(self):
        """ Get the chapters """
        chapters = []
        chapters_html = self.get_page_html().find('select', id="selected_id")
        if chapters_html is None:
            # there is one chapter only´
            chapter_obj = {}
            title, author = self.get_title_and_author()
            chapter_obj["title"] = title.lstrip().rstrip()
            chapter_obj["num"] = 1
            chapter_obj["url"] = None
            chapters.append(chapter_obj)
            return chapters

        chapters_html = chapters_html.find_all('option')
        url = self.get_page_html().find('ul', id='chapter_index')
        url = ("https://archiveofourown.org" +
               re.sub(r"\/\d+$", "", url.select('form')[0]['action']) + "/")

        for li in chapters_html:
            chapter_obj = {}
            chapter_text = li.text

            regex = re.search('^(?P<num>\d+)\.(?P<name>.*)$', chapter_text)

            chapter_obj["title"] = regex.group('name').lstrip().rstrip()
            chapter_obj["num"] = regex.group('num').strip()
            chapter_obj["url"] = url + li['value']
            chapters.append(chapter_obj)

        return chapters

    def get_num_words(self):
        """ Get number of words """
        info = self.get_page_html().select('dl.stats')[0]
        number_of_words = info.find_all('dd', 'words')
        if number_of_words:
            number_of_words = number_of_words[0].text.strip()
        else:
            number_of_words = None
        return number_of_words

    def get_rating(self):
        """ Get rating """
        rating_text = self.get_page_html().select(
            'dd.rating.tags')[0].text.rstrip().lstrip().lower()

        rating = None
        if "general" in rating_text:
            rating = "K"
        elif "teen" in rating_text:
            rating = "T"
        elif "mature" in rating_text:
            rating = "M"

        return rating

    def get_characters(self):
        """ Get characters """
        return []

    def get_auth_data(self):
        """ Get url to send log in data """
        return ("https://archiveofourown.org/users/login",
                "_otwarchive_session")

    def check_if_is_fanfic_or_chapter(self):
        """ Check if the url is a fanfic or a chapter """
        # it doesn't matter here
        return True


class FanficWeb:

    def __init__(self, url):
        self.url = url
        self.scraper = None
        self.page_html = None

    def get_cleaned_url(self):
        """ Transform the url to remove the protocol and last slash """
        url = re.compile(r"https?://(www\.)?")
        url = url.sub('', self.url).strip().strip('/')
        site = self.get_site()
        if "archiveofourown" in site:
            regex = re.compile(r"(\/chapters.*)?")
            url = regex.sub('', url).strip().strip('/')
        return url

    def load_page_html(self):
        """ Get the html of the url """

        auth_url, cookie_name = self.scraper.get_auth_data()

        self.page_html = Fetcher.fetch_page(self.url, auth_url, cookie_name)
        self.scraper.set_page_html(self.page_html)
        return self.page_html

    def get_title_and_author(self):
        """ Get title and author """
        title, author = self.scraper.get_title_and_author()
        return title, author

    def get_fandom_and_media_type(self):
        fandom, media_type = self.scraper.get_fandom_and_media_type()
        return fandom, media_type

    def get_language(self):
        """ Get language """
        language = self.scraper.get_language()
        return language

    def get_characters(self):
        """ Get characters """
        characters = self.scraper.get_characters()
        return characters

    def get_genres(self):
        """ Get genres """
        genres = self.scraper.get_genres()
        return genres

    def get_status(self):
        """ Get status """
        status = self.scraper.get_status()
        return status

    def get_last_time_updated(self):
        """ Get last time updated """
        last_time_updated = self.scraper.get_last_time_updated()
        return last_time_updated

    def get_chapters(self):
        """ Get the chapters """
        chapters = self.scraper.get_chapters()
        return chapters

    def get_num_words(self):
        """ Get number of words """
        num_words = self.scraper.get_num_words()
        return num_words

    def get_rating(self):
        """ Get rating """
        num_words = self.scraper.get_rating()
        return num_words

    def scrape_and_save(self):
        """ Scrape the fanfic's fields and save them """
        with transaction.atomic():
            new_fanfic = fanfic_model()
            fandom_fanfic_relation = FandomFanfic()

            self.title, self.author = self.get_title_and_author()
            new_fanfic.name = self.title
            new_fanfic.author = self.author

            new_fanfic.web = self.url

            new_fanfic.save()

            self.fandom, self.media_type = self.get_fandom_and_media_type()
            type_obj = Type.objects.get(name=self.media_type)

            if self.media_type == "other":
                fandom_in_system = Fandom.objects.filter(
                    name__icontains=self.fandom)
            else:
                fandom_in_system = Fandom.objects.filter(
                    name__icontains=self.fandom, type=type_obj)

            if fandom_in_system.exists():
                fandom = fandom_in_system.first()
            else:
                new_fandom = Fandom()
                new_fandom.name = self.fandom
                new_fandom.type = type_obj
                new_fandom.save()
                fandom = new_fandom

            fandom_fanfic_relation.fanfic = new_fanfic
            fandom_fanfic_relation.fandom = fandom
            fandom_fanfic_relation.is_primary = True
            fandom_fanfic_relation.save()

            self.language = self.get_language()
            new_fanfic.language = self.language

            self.genres = self.get_genres()
            for genre in self.genres:
                new_fanfic.add_genre(genre)

            self.status = self.get_status()
            new_fanfic.complete = self.status

            self.characters = self.get_characters()
            for character in self.characters:
                character_obj = Character.objects.filter(
                    name_surname__icontains=character,
                    fandom=fandom_fanfic_relation.fandom)

                new_character_fanfic_relation = CharacterFanfic()
                if character_obj.exists():
                    character_obj = character_obj.first()

                    if not CharacterFanfic.objects.filter(
                            character=character_obj,
                            fanfic=new_fanfic).exists():
                        new_character_fanfic_relation.character = \
                            character_obj
                else:
                    new_character = Character()
                    new_character.name_surname = character
                    new_character.fandom = fandom_fanfic_relation. \
                        fandom
                    new_character.save()
                    character_obj = new_character

                new_character_fanfic_relation.character = character_obj
                new_character_fanfic_relation.fanfic = new_fanfic
                new_character_fanfic_relation.save()

            self.last_time_updated = self.get_last_time_updated()
            new_fanfic.last_time_updated = self.last_time_updated

            self.chapters = self.get_chapters()  # array
            for chapter in self.chapters:
                new_chapter = Chapter()
                new_chapter.title = chapter['title']
                new_chapter.num_chapter = chapter["num"]
                if chapter["url"] is None:
                    chapter["url"] = self.url
                new_chapter.url_chapter = chapter["url"]
                new_chapter.fanfic = new_fanfic
                new_chapter.save()

            self.num_words = self.get_num_words()
            new_fanfic.num_words = self.num_words

            self.rating = self.get_rating()
            new_fanfic.rating = self.rating

            # save it again
            new_fanfic.save()
            return new_fanfic

    def check_if_is_fanfic_or_chapter(self):
        """ Check if the url is a fanfic or a chapter """
        return self.scraper.check_if_is_fanfic_or_chapter()

    def get_site(self):
        """ Get the site name of url """
        allowed_sites = ["ficwad.com", "avengersfanfiction.com",
                         "archiveofourown.org"]
        for site in allowed_sites:
            if site in self.url:
                return site
        return None

    def check_url_format(self):
        """ Check if url format is ok """
        site = self.get_site()
        if site is not None:
            regex = re.search('https?:\/\/w{0,3}\.?' + site, self.url)
            if regex:
                if site == "ficwad.com" and "story" in str(self.url):
                    return True
                elif (site == "avengersfanfiction.com" and
                      "Story" in str(self.url)):
                    return True
                elif (site == "archiveofourown.org" and "works" in str(
                        self.url)):
                    return True
        return False

    def check_if_online(self):
        """ check if 200 """
        try:
            connect_timeout = 20.0
            read_timeout = 5.0
            r = requests.get(self.url,
                             timeout=(connect_timeout,
                                      read_timeout))
            if r.status_code == 200:
                return True
            return False
        except Exception:
            return False

    def url_without_errors(self):
        """ Check if a url is completely correct """
        clean_url_fanfic = clean_string(self.url)

        if "view_full_work" in clean_url_fanfic:
            # ao3
            self.url = clean_url_fanfic.replace(
                "?view_full_work=true", "")

        if clean_url_fanfic is None:
            # bad written url
            return "Error: Sorry, are you sure the url is correct?"

        format_ok = self.check_url_format()
        if format_ok is False:
            # wrong site or error in url
            return "Error: Sorry, are you sure the url is valid?"

        return self.url

    def set_appropiate_scraper(self):
        """ Set the appropiate scraper for the url """
        site = self.get_site()
        scraper = None
        if "ficwad" in site:
            scraper = FicWadScraper()
        elif "avengers" in site:
            scraper = AvengersFanfictionScraper()
        elif "archiveofourown" in site:
            scraper = ArchiveOfOurOwnScraper()
        self.scraper = scraper
