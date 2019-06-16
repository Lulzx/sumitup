#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import os
import sys

import chardet
import readtime
import telegram
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from newspaper import Article
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegraph import Telegraph
from lxml.html import fromstring
from lxml.html.clean import clean_html, unicode

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


ADMIN = 691609650


def start(bot, update):
    update.message.reply_text('Hi!')


def find(string):
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url


def to_unicode(s):
    if type(s) is unicode:
        return s
    elif type(s) is str:
        d = chardet.detect(s)
        (cs, conf) = (d['encoding'], d['confidence'])
        if conf > 0.80:
            try:
                return s.decode(cs, errors='replace')
            except Exception as ex:
                pass
    return unicode(''.join([i if ord(i) < 128 else ' ' for i in s]))


def help(bot, update):
    update.message.reply_text('Help!')


# noinspection PyBroadException
def echo(bot, update):
    links = find(update.message.text)
    url = links[0]
    article = Article(url)
    article.download()
    article.parse()
    VALID_TAGS = dict(a=['href', 'title'], aside=[], b=[], blockquote=[], br=[], code=[], em=[], figcaption=[],
                      figure=[],
                      h3=[], h4=[], hr=[], i=[], iframe=[], img=['src'], li=[], ol=[], p=[], pre=[], s=[], strong=[],
                      u=[],
                      ul=[], video=[])
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
    read = readtime.of_text(text)
    html = article.html
    # links = find(html)
    # update_id = update.update_id
    # chat_id = update.message.chat_id
    # filepath = r"C:/Users/Lulzx/Documents/sumitup-master/temp/{}.txt".format(update_id)
    # with open(filepath, "w+") as file:
    #    for link in links:
    #        file.write("{}\n".format(link))
    #    file.close()
    # bot.send_document(chat_id=chat_id, document=open(filepath, 'rb'))
    chat_id = update.message.chat_id
    response = requests.get(url)
    value = response.content
    tree = fromstring(value)
    title = str(tree.findtext('.//title'))
    value = clean_html(value)
    #    value = re.sub(r'[^\x00-\x7F]+', ' ', value)
    #    value = value.replace("\r", "").replace("\t", "")
    soup = BeautifulSoup(value, 'html.parser')
    for comments in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comments.extract()
    [s.extract() for s in soup('style')]
    msg = f"""🔗 *Link:* [ {url} ]\n{author}{date}\n🚩 *Title: {title}*\n🗨 *Summarize:* _{summary}_\n"""
    msg += f"""\n🤔 *Reading Time:* {read}\n📑 *Tags:* {tags}\n """
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN)
    if chat_id != ADMIN:
        bot.send_message(chat_id="{}".format(ADMIN), text='{}'.format(msg), parse_mode=telegram.ParseMode.MARKDOWN)
    new = soup.renderContents()
    while 1:
        old = new
        soup = BeautifulSoup(new, 'html.parser')
        for tag in soup.findAll(True):
            if tag.name not in VALID_TAGS:
                tag.hidden = True
            else:
                tag.attrs = {attr: value for attr, value in tag.attrs.items() if attr in VALID_TAGS[tag.name]}
        new = soup.renderContents()
        if old == new:
            break
    html = new.decode()
    user = update.message.chat.first_name
    telegraph = Telegraph()
    telegraph.create_account(short_name=user, author_name=author)
    response = telegraph.create_page(f'{title}', author_name=f'{author}', html_content=f"{html}")
    link = 'https://telegra.ph/{}'.format(response['path'])
    update.message.reply_text(link)


def error(bot, update):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    # token = sys.argv[1]
    updater = Updater(os.environ.get("TOKEN"))
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_error_handler(error)
    updater.start_polling()
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == '__main__':
    main()
