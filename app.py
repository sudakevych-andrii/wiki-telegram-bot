import wikipediaapi
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import token
import mongoengine as me
from models import User, Query


class SearchInfoBot:
    def __init__(self, token):
        self._token = token
        self._bot = TeleBot(self._token)
        self._wiki = wikipediaapi.Wikipedia('ru')
        self._kb = InlineKeyboardMarkup()

        @self._bot.message_handler(commands=["start"])
        def _start(message):
            self._start_method(message)

        @self._bot.message_handler(content_types=['text'])
        def _summary(message):
            self._summary_method(message)

        self._bot.polling()

    @staticmethod
    def _create_user(chat_id):
        try:
            User.objects.create(chat_id=chat_id)
        except me.NotUniqueError:
            pass

    @staticmethod
    def _save_query(chat_id, query):
        query_doc = Query(query=query)
        query_doc.save()
        user_doc = User.objects.get(chat_id=chat_id)
        user_doc.queries.append(query_doc)
        user_doc.save()

    def _get_wiki_page(self, query):
        return self._wiki.page(query)

    def _get_summary(self, query):
        if self._get_wiki_page(query).exists():
            return self._get_wiki_page(query).summary
        else:
            return False

    def _get_url(self, query):
        return self._get_wiki_page(query).fullurl

    def _remove_chat_button(self):
        self._kb.keyboard.clear()

    def _start_method(self, message):
        self._remove_chat_button()
        self._bot.send_message(message.chat.id, 'Search in wikipedia. Enter your query.')
        self._create_user(message.chat.id)

    def _summary_method(self, message):
        self._remove_chat_button()
        if self._get_summary(message.text):
            button_link = InlineKeyboardButton(text='Link to article in wikipedia', url=self._get_url(message.text))
            self._kb.add(button_link)
            self._bot.send_message(message.chat.id, self._get_summary(message.text), reply_markup=self._kb)
        else:
            self._bot.send_message(message.chat.id, 'No results')
        self._save_query(message.chat.id, message.text)


if __name__ == '__main__':
    search_info_bot = SearchInfoBot(token)

