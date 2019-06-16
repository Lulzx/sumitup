def welp(bot, update):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string
    response = telegraph.create_page('{}'.format(title), author_name=author, html_content="{}".format(html))
    link = 'https://telegra.ph/{}'.format(response['path'])
    update.message.reply_text(link)
