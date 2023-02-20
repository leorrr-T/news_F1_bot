import feedparser
import configparser
import time
import telebot
from aiogram import types
from aiogram.utils.markdown import hlink

s_news = []
try:
    with open('s.txt', 'r', encoding='utf-8') as fr:
        for line in fr:
            x = line[:-1]
            s_news.append(x)
except IOError as e:
    s_news = []

with open('w.txt', 'r', encoding='utf-8') as f:
    word = f.read().splitlines()
    f.close()
with open('ws.txt', 'r', encoding='utf-8') as f:
    words = f.read().splitlines()
    f.close()


class Source(object):
    def __init__(self, config_links):
        self.links = [config_links[i] for i in config_links]
        self.news = []
        self.refresh()

    def refresh(self):
        self.news = []
        for i in self.links:
            data = feedparser.parse(i)
            for element in data['entries']:
                for w in element.title.replace('-', ' ').replace('’', ' ').replace('\'', ' ').replace(':', ' ').replace('–', ' ').replace(',', ' ').split():
                    if w.lower() in word:
                        self.news.append(element)
            for element in data['entries']:
                for w in words:
                    if w in element.title.lower():
                        self.news.append(element)

        # print(str(self.news))
        print('news   - ' + str(len(self.news)))

    def __repr__(self):
        return "<RSS ('%s','%s')>" % (self.links, len(self.news))


def main():
    config = configparser.ConfigParser()
    config.read('./config')
    bot_access_token = config['Telegram']['access_token']
    delay_between_messages = int(config['export_params']['delay_between_messages'])
    pub_pause = int(config['export_params']['pub_pause'])
    bot = telebot.TeleBot(bot_access_token)
    global s_news
    for_publishing = []
    n = 0
    while True:
        src = Source(config['RSS'])
        news = src.news
        for element in news:
            if element.title not in s_news:
                for_publishing.append(element)
                s_news.append(element.title)
        if len(for_publishing) > 0:
            for post in for_publishing:
                bot.send_message(config['Telegram']['chat'], f"<b>{hlink(post.title, post.link)}</b>", parse_mode=types.ParseMode.HTML)
                print('title - ' + post.title)
                time.sleep(delay_between_messages)

        print('to pub - ' + str(len(for_publishing)))
        print('s_news - ' + str(len(s_news)))
        print('n=' + str(n))
        print('--- ----- ---')

        if len(s_news) > 100:
            del s_news[1:55]

        n = n + 1

        if n > 5:
            n = 0
            with open('s.txt', 'w', encoding='utf-8') as fw:
                for item in s_news:
                    fw.write("%s\n" % item)

        for_publishing.clear()

        time.sleep(pub_pause)


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "NEW bot")

    # @bot.message_handler(content_types=["text"])


if __name__ == '__main__':
    main()