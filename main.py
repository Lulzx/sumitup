#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
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
from lxml.html.clean import clean_html, unicode

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Hi!')


def find(string):
    url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return url


VALID_TAGS = dict(a=['href', 'title'], aside=[], b=[], blockquote=[], br=[], code=[], em=[], figcaption=[], figure=[],
                  h3=[], h4=[], hr=[], i=[], iframe=[], img=['src'], li=[], ol=[], p=[], pre=[], s=[], strong=[], u=[],
                  ul=[], video=[])


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


def sanitize_html(value, valid_tags=None):
    if valid_tags is None:
        valid_tags = VALID_TAGS
    response = requests.get(f'{value}')
    value = response.content
    value = clean_html(value)
#    value = re.sub(r'[^\x00-\x7F]+', ' ', value)
#    value = value.replace("\r", "").replace("\t", "")
    soup = BeautifulSoup(value, 'html.parser')
    for comments in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comments.extract()
    [s.extract() for s in soup('style')]
    new = soup.renderContents()
    while 1:
        old = new
        soup = BeautifulSoup(new, 'html.parser')
        for tag in soup.findAll(True):
            if tag.name not in valid_tags:
                tag.hidden = True
            else:
                tag.attrs = {attr: value for attr, value in tag.attrs.items() if attr in valid_tags[tag.name]}
        new = soup.renderContents()
        if old == new:
            break
    new = new.decode()
    return new


def help(bot, update):
    update.message.reply_text('Help!')


# noinspection PyBroadException
def echo(bot, update):
    links = find(update.message.text)
    url = links[0]
    article = Article(url)
    article.download()
    article.parse()
    title = article.title
    try:
        author = "✍ *Author:* " + article.authors + "\n"
    except:
        author = ""
    date = "📅 *Publication Date:* "
    try:
        date += str(article.publish_date.strftime('%Y-%m-%d'))
    except:
        if article.publish_date is not None:
            date += str(article.publish_date)
        else:
            date = ""
    text = article.text
    update_id = update.update_id
    chat_id = update.message.chat_id
    article.nlp()
    keywords = article.keywords
    tags = ""
    for keyword in keywords:
        tags += " #" + keyword
    summary = article.summary
    read = readtime.of_text(text)
    text = f"""🔗 *Link:* [ {url} ]\n{author}{date}\n🚩 *Title: {title}*\n🗨 *Summarize:* _{summary}_\n"""
    text += f"""\n🤔 *Reading Time:* {read}\n📑 *Tags:* {tags}\n """
    update.message.reply_text(text, parse_mode=telegram.ParseMode.MARKDOWN)
    html = article.html
    links = find(html)
    filepath = r"C:/Users/Lulzx/Documents/sumitup-master/temp/{}.txt".format(update_id)
    with open(filepath, "w+") as file:
        for link in links:
            file.write("{}\n".format(link))
        file.close()
    bot.send_document(chat_id=chat_id, document=open(filepath, 'rb'))
    # image = article.top_image
    telegraph = Telegraph()
    html = sanitize_html(url)
    user = update.message.chat.first_name
    telegraph.create_account(short_name=user, author_name=author)
    response = telegraph.create_page('{}'.format(title), author_name=author, html_content="{}".format(html))
    link = 'https://telegra.ph/{}'.format(response['path'])
    update.message.reply_text(link)


def error(bot, update):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    token = sys.argv[1]
    updater = Updater(token)
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
