import asyncio
import requests
import feedparser
import configparser
import time
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.markdown import hlink
from aiogram.dispatcher.filters import Text

config = configparser.ConfigParser()
config.read('./config')
bot_access_token = config['Telegram']['access_token']
net_timeout = int(config['export_params']['net_timeout'])
delay_between_messages = int(config['export_params']['delay_between_messages'])
pub_pause = int(config['export_params']['pub_pause'])
headers = {'content-type': 'application/rss+xml', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

bot = Bot(token=bot_access_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

e = []
s_news = []
news = []

r = 1
te = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M %d.%m.%Y')
tc = '2012-12-21 12:21:12'
tp = f'not yet since {te}'
s = 'working'

try:
    with open('s.txt', 'r', encoding='utf-8') as fr:
        for line in fr:
            x = line[:-1]
            s_news.append(x)
except IOError as e:
    s_news = []

t = len(s_news)

with open('w.txt', 'r', encoding='utf-8') as f:
    word = f.read().splitlines()
    f.close()
with open('ws.txt', 'r', encoding='utf-8') as f:
    words = f.read().splitlines()
    f.close()


def refresh():
    global news
    news = []
    config_links = config['RSS']
    links = [config_links[i] for i in config_links]
    for i in links:
        try:
            # print(i)
            try:
                resp = requests.get(i, timeout=net_timeout, headers=headers)
            except requests.ReadTimeout:
                print('timeout - ' + i)
                e.append(f'timeout - {tc} - {i}')
                continue
            data = feedparser.parse(resp.content)
            for element in data['entries']:
                for w in element.title.replace('-', ' ').replace('’', ' ').replace('\'', ' ').replace(':', ' ').replace(
                        '–', ' ').replace(',', ' ').split():
                    if w.lower() in word:
                        news.append(element)
            for element in data['entries']:
                for w in words:
                    if w in element.title.lower():
                        news.append(element)
        except Exception as er:
            print(er)
            e.append(f'Exception - {tc}')
            continue

    print('news_1 - ' + str(len(news)))

    config_links2 = config['RSS2']
    links2 = [config_links2[i] for i in config_links2]

    for i in links2:
        try:
            # print(i)
            try:
                resp = requests.get(i, timeout=net_timeout, headers=headers)
            except requests.ReadTimeout:
                print('timeout - ' + i)
                e.append(f'timeout - {tc} - {i}')
                continue
            data = feedparser.parse(resp.content)
            for element in data['entries']:
                news.append(element)
        except Exception as er:
            print(er)
            e.append(f'Exception - {tc}')
            continue

    print('news_2 - ' + str(len(news)))


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    start_buttons = ["Start channel", "Is alive", "Stop channel"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Starting", reply_markup=keyboard)


@dp.message_handler(Text(equals="Is alive"))
async def is_alive(message: types.Message):
    await message.answer('s_news - ' + str(len(s_news)) + ', ' + 'news - ' + str(len(news)))
    await message.answer('last check ' + tc + ',\nlast post    ' + tp + '\nStatus:       ' + s)
    nn = f'errors since {te} - {str(len(e))}'
    for post in e:
        nn = nn + '\n' + str(post)
    await message.answer(nn)


@dp.message_handler(Text(equals="Start channel"))
async def start_ch(message: types.Message):
    global r
    global s
    r = 1
    s = 'working'
    await message.answer("Start NEWSing")
    loop.create_task(get_f_news())


@dp.message_handler(Text(equals="Stop channel"))
async def stop_ch(message: types.Message):
    global r
    global s
    r = 0
    s = 'NOT working'
    await message.answer("STOP newsing")


async def get_f_news():
    for_publishing = []
    global t
    global tc
    global tp
    global te

    while r == 1:
        tc = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M')
        print('time   - ' + tc)
        refresh()

        print('s_news_A - ' + str(len(s_news)))

        for element in news:
            if element['title'] not in s_news:
                for_publishing.append(element)
                s_news.append(element['title'])

        print('s_news_B - ' + str(len(s_news)))

        if len(for_publishing) > 0:
            print('to Pub - ' + str(len(for_publishing)))
            for post in for_publishing:
                print(post['title'])
                n = f"<b>{hlink(post['title'], post['link'])}</b>"
                time.sleep(delay_between_messages)

                # await bot.send_message(config['Telegram']['chat'], n)
            tp = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M  %d.%m.%Y')

        for_publishing.clear()

        if len(s_news) > t:
            with open('s.txt', 'w', encoding='utf-8') as fw:
                for item in s_news:
                    fw.write("%s\n" % item)
            print('writing to file')
            t = len(s_news)

        print('t - ' + str(t))
        print('err since ' + te + ' - ' + str(len(e)))
        print('--- ---- ---')

        if len(e) > 21:
            e.clear()
            te = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M %d.%m.%Y')

        if len(s_news) > 199:
            del s_news[1:100]
            t = len(s_news)

        await asyncio.sleep(pub_pause)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(get_f_news())
    executor.start_polling(dp)
