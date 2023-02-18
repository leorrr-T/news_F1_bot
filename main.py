# This is a sample Python script.
import feedparser
import configparser
import time
import telebot


class Source(object):
    def __init__(self, config_links):
        self.links = [config_links[i] for i in config_links]
        self.news = []
        self.refresh()

    def refresh(self):
        self.news = []
        for i in self.links:
            data = feedparser.parse(i)
            self.news += data['entries']

    def __repr__(self):
        return "<RSS ('%s','%s')>" % (self.links, len(self.news))


def main():
    config = configparser.ConfigParser()
    config.read('./config')
    bot_access_token = config['Telegram']['access_token']
    telegram_bot(bot_access_token)


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    config = configparser.ConfigParser()
    config.read('./config')
    delay_between_messages = int(config['export_params']['delay_between_messages'])
    pub_pause = int(config['export_params']['pub_pause'])

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "NEW bot")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        src = Source(config['RSS'])
        src.refresh()
        news = src.news
        line = [i for i in news]
        for_publishing = list(set(line) & set(news))
        for post in for_publishing:
            bot.send_message(config['Telegram']['chat'], post)
            print(post)
            time.sleep(delay_between_messages)
        # time.sleep(pub_pause)

    bot.polling()


if __name__ == '__main__':
    main()

# bot.polling(none_stop=True)
# def print_hi(name):
# Use a breakpoint in the code line below to debug your script.
#    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
