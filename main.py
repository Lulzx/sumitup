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


def qa(question, passage):
    data = {"model":"bidaf-elmo","passage": passage ,"question": question}
    r = requests.post('https://demo.allennlp.org/api/bidaf-elmo/predict', json=data).json()
    return r["best_span_str"]


def add(update, context):
    chat_id = update.message.chat_id
    text = ' '.join(context.args)
    context.bot.send_message(chat_id=chat_id, text="Added to queue! processing...")
    links = find(text)
    if links == []: #and update.message.chat.type == "supergroup":
        pass
    else:
        url = links[0]
        text = requests.get(url).text
    context.chat_data[chat_id] = text
    context.bot.send_message(chat_id=chat_id, text="Ready! 👍🏻")


def ask(update, context):
    chat_id = update.message.chat_id
    question = ' '.join(context.args)
    try:
        passage = update.message.reply_to_message.text
    except:
        passage = context.chat_data[chat_id]
    response = qa(question, passage)
    context.bot.send_message(chat_id=chat_id, text=response, reply_to_message_id=update.message.message_id)

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


def screenshot(update, context):
    chat_id = update.message.chat_id
    url = context.args[0]
    photo = "https://api.microlink.io/?url={}&waitUntil=networkidle2&screenshot=true&meta=false&embed=screenshot.url".format(url)
    context.bot.send_photo(chat_id=chat_id, photo=photo)


def fullshot(update, context):
    chat_id = update.message.chat_id
    url = context.args[0]
    file = "https://api.microlink.io/?url={}&waitUntil=networkidle2&screenshot=true&meta=false&embed=screenshot.url&fullPage=true".format(url)
    context.bot.send_document(chat_id=chat_id, document=file)


def pdf(update, context):
    chat_id = update.message.chat_id
    url = context.args[0]
    file = "https://api.microlink.io/?url={}&pdf&embed=pdf.url&scale=1&margin=0.4cm".format(url)
    context.bot.send_document(chat_id=chat_id, document=file)


def technologies(update, context):
    chat_id = update.message.chat_id
    link = context.args[0]
    url = "https://api.microlink.io/?url={}&meta=false&insights.lighthouse=false&insights.technologies=true".format(link)
    result = requests.get(url).json()

    tech_list = result['data']['insights']['technologies']
    len_tech = len(tech_list)
    string = ""
    if len_tech > 1:
        for n, tech in enumerate(tech_list):
            if n < len_tech - 1:
                string += "├ " + str(tech['name']) + ' - ' + str(tech['categories'][0]) + "\n"
            else:
                string += "└ " + str(tech['name']) + ' - ' + str(tech['categories'][0])
    else:
        string += "└ "+ str(tech_list[0]['name']) + ' - ' + str(tech_list[0]['categories'][0]) + "\n"

    context.bot.send_message(chat_id=chat_id, text="<b>Detected {} technologies behind the site:</b>\n{}".format(len_tech, string), parse_mode=telegram.ParseMode.HTML)


def help(update, context):
    update.message.reply_text("""commands

pdf - export url as pdf
scr - screenshot of the webpage
full - full page screenshot of webpage
add - store the passage to ask questions from
ask - followed by question you want to ask (can be used as reply too)""")


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
    value = article.html
    tree = fromstring(value)
    title = str(tree.findtext('.//title'))
    lang = translator.detect(title).lang
    if lang != 'en':
        text = translate(url)
        if text == 'null':
            return
        update.message.reply_text(text)
        url = find(text)[0]
        article = Article(url)
        article.download()
        article.parse()
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
    dp.add_handler(CommandHandler("scr", screenshot))
    dp.add_handler(CommandHandler("full", fullshot))
    dp.add_handler(CommandHandler("pdf", pdf))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("ask", ask))
    dp.add_handler(CommandHandler("tech", technologies))
    dp.add_handler(MessageHandler(Filters.text, process))
    dp.add_error_handler(error)
    updater.start_polling(clean=True, timeout=99999)
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == '__main__':
    main()
