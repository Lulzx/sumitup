#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import re
import sys
import urllib.parse
from functools import reduce
from html.parser import HTMLParser
from urllib.parse import quote
from urllib.parse import urljoin

import emoji
import nltk
import pytesseract
import readtime
import requests
import telegram
from bs4 import BeautifulSoup as bs
from googletrans import Translator
from html_telegraph_poster import TelegraphPoster
from lxml.html import fromstring
from newspaper import Article
from readability import Document
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, CallbackQueryHandler)

ADMIN: int = 691609650
text_nodes = 0
text_strings = []
markup = """"""
url = ""
translator = Translator()

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

nltk.download('punkt')


def start(update, context):
    update.message.reply_text("""Hi! Send me a link.\n\ncommands

pdf - export url as pdf
scr - screenshot of the webpage
full - full page screenshot of webpage
add - store the passage to ask questions from
ask - followed by question you want to ask (can be used as reply too)""")


class HtmlParser(HTMLParser):
    def error(self, message):
        pass

    def handle_starttag(self, tag, attrs):
        if tag not in [
            'a', 'aside', 'b', 'blockquote',
            'br', 'code', 'em', 'figcaption',
            'figure', 'h3', 'h4', 'hr',
            'i', 'iframe', 'img', 'li',
            'ol', 'p', 'pre', 's',
            'strong', 'u', 'ul', 'video']:
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
        if tag not in [
            'a', 'aside', 'b', 'blockquote',
            'br', 'code', 'em', 'figcaption',
            'figure', 'h3', 'h4', 'hr',
            'i', 'iframe', 'img', 'li',
            'ol', 'p', 'pre', 's',
            'strong', 'u', 'ul', 'video']:
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
    data = {"model": "bidaf-elmo", "passage": passage, "question": question}
    r = requests.post(
        'https://demo.allennlp.org/api/bidaf-elmo/predict', json=data).json()
    return r["best_span_str"]


def add(update, context):
    chat_id = update.message.chat_id
    text = ' '.join(context.args)
    context.bot.send_message(
        chat_id=chat_id, text="Added to queue! processing...")
    links = find(text)
    if not links:  # and update.message.chat.type == "super_group":
        pass
    else:
        link = links[0]
        text = requests.get(link).text
    context.chat_data[chat_id] = text
    context.bot.send_message(chat_id=chat_id, text="Ready! 👍🏻")


def ask(update, context):
    chat_id = update.message.chat_id
    question = ' '.join(context.args)
    if update.message.reply_to_message:
        passage = update.message.reply_to_message.text
    else:
        passage = context.chat_data[chat_id]
    response = qa(question, passage)
    context.bot.send_message(
        chat_id=chat_id, text=response,
        reply_to_message_id=update.message.message_id)


def translate(link):
    global url
    global text_nodes
    global text_strings
    global markup

    dest = "en"
    url = link
    parser = HtmlParser()
    response = requests.get(url)
    doc = Document(response.text)
    # tree = fromstring(r.content)
    title = doc.title()  # tree.findtext('.//title')
    lang = translator.detect(title).lang
    if lang == 'en':
        # print("The article appears to be in English already.")
        return 'null'
    title = translator.translate(title).text
    content = doc.summary()
    # print(content)
    soup = bs(content, 'lxml')
    text = str(soup.find('body'))
    # text = r.text.split('<body')[1].split('</body>')[0]
    repls = ('h1>', 'h3>'), ('h2>', 'h3>'), ('<h1', '<h3'), ('<h2', '<h3')
    text = reduce(lambda a, kv: a.replace(*kv), repls, text)
    text = emoji.get_emoji_regexp().sub(r'', text)  # removing the emojis
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
    # print(markup)
    access_token = os.environ.get("access_token")
    t = TelegraphPoster(
        access_token=access_token)
    article = t.post(title=str(title), author='lulz', text=str(markup))
    x = str(article).replace("'", '"')
    article = json.loads(x)
    text = "Your article is ready to read! {}".format(article['url'])
    return text


def find(string):
    link = re.findall(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return link


def screenshot(update, context):
    chat_id = update.message.chat_id
    link = context.args[0]
    photo = f"https://api.microlink.io/?url={link}&waitUntil=networkidle2&screenshot=true&meta=false&embed=screenshot.url"
    context.bot.send_photo(chat_id=chat_id, photo=photo)


def full_screenshot(update, context):
    chat_id = update.message.chat_id
    link = context.args[0]
    file = f"https://api.microlink.io/?url={link}&waitUntil=networkidle2&screenshot=true&meta=false&embed=screenshot.url&fullPage=true"
    context.bot.send_document(chat_id=chat_id, document=file)


def pdf(update, context):
    chat_id = update.message.chat_id
    link = context.args[0]
    file = f"https://api.microlink.io/?url={link}&pdf&embed=pdf.url&scale=1&margin=0.4cm"
    context.bot.send_document(chat_id=chat_id, document=file)


def technologies(update, context):
    chat_id = update.message.chat_id
    link = f"https://api.microlink.io/?url={context.args[0]}&meta=false&insights.lighthouse=false&insights.technologies=true"
    result = requests.get(link).json()

    tech_list = result['data']['insights']['technologies']
    len_tech = len(tech_list)
    string = ""
    if len_tech > 1:
        for n, tech in enumerate(tech_list):
            if n < len_tech - 1:
                string += "├ " + str(tech['name']) + \
                          ' - ' + str(tech['categories'][0]) + "\n"
            else:
                string += "└ " + str(tech['name']) + \
                          ' - ' + str(tech['categories'][0])
    else:
        string += "└ " + str(tech_list[0]['name']) + \
                  ' - ' + str(tech_list[0]['categories'][0]) + "\n"

    context.bot.send_message(chat_id=chat_id, text="<b>Detected {} technologies behind the site:</b>\n{}".format(
        len_tech, string), parse_mode=telegram.ParseMode.HTML)


def help_response(update, context):
    update.message.reply_text("""commands

pdf - export url as pdf
scr - screenshot of the webpage
full - full page screenshot of webpage
add - store the passage to ask questions from
ask - followed by question you want to ask (can be used as reply too)""")


def wolfram(update, context):
    chat_id = update.message.chat_id
    text = context.args[0]
    user_question = quote(text, safe='')
    wolfram_key = os.environ.get("WOLFRAM_KEY")
    link = f'http://api.wolframalpha.com/v2/query?appid={wolfram_key}&input={user_question}'
    answer = requests.get(link)
    soup = bs(answer.text, 'html.parser')
    images = soup.find_all('subpod')
    for image in images:
        image_url = image.find('img')['src']
        context.bot.send_photo(chat_id=chat_id, photo=image_url)


def alternative(update, context):
    query = ' '.join(context.args)
    print(query)
    response = fetch(query)
    print(response)
    update.message.reply_text(response)


def fetch(query):
    post = ""
    pltoshow = ""
    altshow = ""
    tagshow = ""
    searched = query
    urlsearched = "http://alternativeto.net/browse/search/?q=" + searched + "&ignoreExactMatch=true"
    searchedpage = requests.get(urlsearched)
    searchedtree = fromstring(searchedpage.content)
    searchedlink = searchedtree.xpath('//a[@data-link-action="Search"]/@href')
    link = "http://alternativeto.net" + searchedlink[0]
    page = requests.get(link)
    tree = fromstring(page.content)
    title = tree.xpath('//h1[@itemprop="name"]/text()')
    tags = tree.xpath('//span[@class="label label-default"]/text()')
    platforms = tree.xpath('//li[@class="label label-default "]/text()')
    # image = tree.xpath('//div[@class="image-wrapper"]/img[@src]')
    alternativs = tree.xpath('//a[@data-link-action="Alternatives"]/text()')
    creatorwebsite = tree.xpath('//a[@class="ga_outgoing"]/@href')
    try:
        post += "{}[{}]\n".format(title[0], creatorwebsite[0]) + "\n"
    except IndexError:
        post += title[0]
    print(post)
    for x, platform in enumerate(platforms):
        if x is len(platforms) - 1:
            pltoshow += "└ " + platform + "\n"
        else:
            pltoshow += "├ " + platform + "\n"
    post += "Platforms: " + "\n" + pltoshow + "\n"
    print(post)
    for y, alternative in enumerate(alternativs):
        if y is len(alternativs) - 1:
            altshow += "└ " + alternative + "\n"
        else:
            altshow += "├ " + alternative + "\n"
    post += "Alternatives: " + "\n" + altshow + "\n"
    print(post)
    for z, tag in enumerate(tags):
        tagshow += "#" + tag + "\n"
    post += "genres:" + "\n" + tagshow
    print(post)
    return post


def button(update, context):
    query = update.callback_query
    context.bot.answer_callback_query(
        query.id, text="The article has been added to your reading list.", show_alert=False)


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


# noinspection PyBroadException
def process(update, context):
    if update.message:
        text = update.message.text
    else:
        return
    links = find(text)
    # handling for groups, when message has no links
    if not links:  # and update.message.chat.type == "super_group":
        return
    link = links[0]
    # try:
    #     link = links[0]
    # except:
    #     update.message.reply_text("Oh! Send a valid link.")
    article = Article(link)
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
        text = translate(link)
        if text == 'null':
            return
        update.message.reply_text(text)
        link = find(text)[0]
        article = Article(link)
        article.download()
        article.parse()
    text = article.text
    soup = bs(value, 'lxml')
    outline = ""
    for heading in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        heading_text = heading.text.strip()
        if heading.name in ["h1", "h2"]:
            heading_text = f"*{heading_text}*"
        outline += int(heading.name[1:]) * ' ' + '- ' + heading_text + '\n'
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
    msg = f"""🔗 *Link:* {link}\n{author}{date}\n🚩 *Title: {title}*\n\n🗨 *Summary:*\n _{summary}_\n"""
    msg += f"""🎋 *Outline: * \n{outline}\n"""
    msg += f"""🤔 *Reading Time:* {read}\n""".replace("min", "mins")
    msg += f"""📑 *Tags:* {tags}\n """
    query = urllib.parse.quote(msg.replace('*', '**').replace('_', '__'))
    share_url = 'tg://msg_url?url=' + query
    button_list = [
        InlineKeyboardButton('Add to reading list', callback_data=1),
        InlineKeyboardButton("📬 Share", url=share_url)
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    update.message.reply_text(
        msg, parse_mode=telegram.ParseMode.MARKDOWN, reply_markup=reply_markup)

    if update.message.chat_id != ADMIN:
        context.bot.send_message(chat_id="{}".format(ADMIN),
                                 text='{}'.format(
                                     update.message.from_user.first_name + " *sent:*\n" + msg),
                                 parse_mode=telegram.ParseMode.MARKDOWN)


def ocr(update, context):
    chat_id = update.message.chat.id
    file_id = update.message.photo[-1].file_id
    file_name = file_id + ".png"
    picture = context.bot.get_file(file_id).download('./data/{}'.format(file_name))
    try:
        text = pytesseract.image_to_string('./data/{}'.format(file_name))
        if text == "":
            if update.message.chat.type == "supergroup":
                return  # won't show error messages in groups
            text = "sorry, unable to extract text from your image."
    except:
        text = "sorry, an error has occured while processing your image."
    context.bot.send_message(chat_id=chat_id, text=text)


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
    dp.add_handler(CommandHandler("help", help_response))
    dp.add_handler((CallbackQueryHandler(button)))
    dp.add_handler(MessageHandler(Filters.photo, ocr))
    dp.add_handler(CommandHandler("scr", screenshot))
    dp.add_handler(CommandHandler("full", full_screenshot))
    dp.add_handler(CommandHandler("pdf", pdf))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("ask", ask))
    dp.add_handler(CommandHandler("wolfram", wolfram))
    dp.add_handler(CommandHandler("alt", alternative))
    dp.add_handler(CommandHandler("tech", technologies))
    dp.add_handler(MessageHandler(Filters.text, process))
    dp.add_error_handler(error)
    updater.start_polling(clean=True, timeout=99999)
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == '__main__':
    main()
