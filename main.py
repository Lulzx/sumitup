#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import re
import sys

import readtime
import telegram
from lxml.html import fromstring
from newspaper import Article
import urllib.parse
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from googletrans import Translator
from html.parser import HTMLParser
import emoji
import re
import json
import requests
from readability import Document
from lxml.html import fromstring
from bs4 import BeautifulSoup as bs
from requests.compat import urljoin
from functools import reduce
from html_telegraph_poster import TelegraphPoster

ADMIN = 691609650
text_nodes = 0
text_strings = []
markup = """"""
url = ""
translator = Translator()

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi! Send me a link.')


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag not in ['a','aside','b','blockquote','br','code','em','figcaption','figure','h3','h4','hr','i','iframe','img','li','ol','p','pre','s','strong','u','ul','video']:
            return
        # print("Start tag:", tag)
        global markup
        markup += " <" + tag
        for attr in attrs:
            attribute = ""
            if attr[0] in ['src', 'href']:
                global url
                href = attr[1]
                attribute += urljoin(url, href)
                markup += " {0}='{1}'".format(attr[0], attribute)
            # print("     attr:", attr)
        markup += ">"

    def handle_endtag(self, tag):
        if tag not in ['a','aside','b','blockquote','br','code','em','figcaption','figure','h3','h4','hr','i','iframe','img','li','ol','p','pre','s','strong','u','ul','video']:
            return
        global markup
        markup += "</{}>".format(tag)
        # print("End tag  :", tag)

    def handle_data(self, data):
        global text_nodes
        global text_strings
        global markup
        markup += " {" + str(text_nodes) + "}"
        scheme = [data]
        text_strings.extend(scheme)
        # print("Data     :", data + " ====> {}".format(text_nodes))
        text_nodes += 1



def translate(link):

    global url
    global text_nodes
    global text_strings
    global markup

    dest = "en"
    url = link
    parser = MyHTMLParser()
    response = requests.get(url)
    doc = Document(response.text)
    # tree = fromstring(r.content)
    title = doc.title() # tree.findtext('.//title')
    lang = translator.detect(title).lang
    if lang == 'en':
        # print("The article appears to be in English already.")
        return 'null'
    title = translator.translate(title).text
    content = doc.summary()
    #print(content)
    soup = bs(content, 'lxml')
    text = str(soup.find('body'))
    # text = r.text.split('<body')[1].split('</body>')[0]
    repls = ('h1>', 'h3>'), ('h2>', 'h3>'), ('<h1', '<h3'), ('<h2', '<h3')
    text = reduce(lambda a, kv: a.replace(*kv), repls, text)
    text = emoji.get_emoji_regexp().sub(r'', text) # removing the emojis
    # print(text)
    parser.feed(text)
    # print("text_nodes: ", text_nodes)
    # print(text_strings)
    # print(text)
    # print(markup)
    # print("STARTING TO TRANSLATE...", url)
    translations = translator.translate(text_strings, dest=str(dest))
    final_payload = []
    for translation in translations:
        scheme = [translation.text]
        # print(translation.origin, ' -> ', scheme[0])
        final_payload.extend(scheme)
    markup = markup.format(*final_payload)
    markup = re.sub(r'\s([?.!"](?:\s|$))', r'\1', markup)
    print("\n")
    #print(markup)
    t = TelegraphPoster(access_token='0010fae64146e64e1f145470b866afc43e1f2221834eeffc8f3e4a901ac7')
    article = t.post(title=str(title), author='lulz', text=str(markup))
    x = str(article).replace("'", '"')
    article = json.loads(x)
    text="Your article is ready to read! {}".format(article['url'])
    return text


def find(string):
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url


def help(update, context):
    update.message.reply_text('Help!')


def button(update, context):
    query = update.callback_query
    context.bot.answer_callback_query(query.id, text="The article has been added to your reading list.", show_alert=False)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# noinspection PyBroadException
def process(update, context):
    links = find(update.message.text)
    # handling for groups, when message has no links
    if links == []: #and update.message.chat.type == "supergroup":
        return
    try:
        url = links[0]
    except:
        update.message.reply_text("Oh! Send a valid link.")
    article = Article(url)
    article.download()
    article.parse()
    try:
        author = "✍ *Author:* " + article.authors + "\n"
    except:
        author = ""
    date = "📅 *Publication Date:* "
    try:
        date += str(article.publish_date.strftime('%Y-%m-%d'))
    except:
        if article.publish_date is None:
            date = ""
        else:
            date += str(article.publish_date)
    text = article.text
    article.nlp()
    keywords = article.keywords
    tags = ""
    for keyword in keywords:
        tags += " #" + keyword
    summary = article.summary
    summary_points = ""
    for x in summary.splitlines():
        summary_points += "↦️ " + x + "\n"
    summary = summary_points
    read = readtime.of_text(text)
    # html = article.html
    # links = find(html_content)
    # update_id = update.update_id
    # chat_id = update.message.chat_id
    # filepath = r"C:/Users/Lulzx/Documents/sumitup-master/temp/{}.txt".format(update_id)
    # with open(filepath, "w+") as file:
    #    for link in links:
    #        file.write("{}\n".format(link))
    #    file.close()
    # context.bot.send_document(chat_id=chat_id, document=open(filepath, 'rb'))
    value = article.html
    tree = fromstring(value)
    title = str(tree.findtext('.//title'))
    msg = f"""🔗 *Link:* {url}\n{author}{date}\n🚩 *Title: {title}*\n\n🗨 *Summary:*\n _{summary}_\n"""
    msg += f"""🤔 *Reading Time:* {read}\n""".replace("min", "mins")
    msg += f"""📑 *Tags:* {tags}\n """
    query = urllib.parse.quote(msg.replace('*', '**').replace('_', '__'))
    share_url = 'tg://msg_url?url=' + query
    button_list = [
        InlineKeyboardButton('Add to reading list', callback_data=1),
        InlineKeyboardButton("📬 Share", url=share_url)
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
    lang = translator.detect(title).lang
    if lang != 'en':
        text = translate(url)
        if text == 'null':
            return
        update.message.reply_text(text)
    if update.message.chat_id != ADMIN:
        context.bot.send_message(chat_id="{}".format(ADMIN),
                         text='{}'.format(update.message.from_user.first_name + " *sent:*\n" + msg),
                         parse_mode=telegram.ParseMode.MARKDOWN)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"' % (update, context.error))


def main():
    try:
        token = sys.argv[1]
    except IndexError:
        token = os.environ.get("TOKEN")
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler((CallbackQueryHandler(button)))
    dp.add_handler(MessageHandler(Filters.text, process))
    dp.add_error_handler(error)
    updater.start_polling(clean=True, timeout=99999)
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == '__main__':
    main()
