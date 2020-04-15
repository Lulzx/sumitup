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

ADMIN = 691609650

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Hi! Send me a link.')


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
    if links == [] and update.message.chat.type == "group":
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
    msg = f"""🔗 *Link:* {url}\n{author}{date}\n🚩 *Title: {title}*\n🗨 *Summarize:* _{summary}_\n"""
    msg += f"""\n🤔 *Reading Time:* {read}\n📑 *Tags:* {tags}\n """
    query = urllib.parse.quote(msg.replace('*', '**').replace('_', '__'))
    share_url = 'tg://msg_url?url=' + query
    button_list = [
        InlineKeyboardButton('Add to reading list', callback_data=1),
        InlineKeyboardButton("📬 Share", url=share_url)
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    update.message.reply_text(msg, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)
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
    updater.start_polling()
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == '__main__':
    main()
