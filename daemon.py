# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
from telepot.loop import MessageLoop
import pymysql, telepot, time, random
from time import sleep
import logging
from socket import error as SocketError
import errno, sys

token = '<Telegram Token>'
bot = telepot.Bot(token)


def quiz(msg):
    telegram_conn = pymysql.connect(host='<DB IP Address>', user='<DB User>', password='<DB User Password>', db='<DB Name>', charset='utf8')
    telegram_conn.autocommit(True)
    cur = telegram_conn.cursor()
    content_type, chat_type, chat_id = telepot.glance(msg)

    GET_NUM = 'SELECT num FROM korean ORDER BY num DESC LIMIT 1;'
    RESULT_NUM = cur.execute(GET_NUM)
    NUM = cur.fetchall()
    RANDOM_NUM = random.randrange(1, NUM[0][0])

    GET_QUESTION = 'SELECT k_words FROM korean WHERE num = %s;' % RANDOM_NUM
    RESULT_QUESTION = cur.execute(GET_QUESTION)
    QUESTION = cur.fetchall()

    GET_ANSWER = 'SELECT r_words FROM korean WHERE num = %s;' % RANDOM_NUM
    RESULT_ANSWER = cur.execute(GET_ANSWER)
    ANSWER = cur.fetchall()
    if ANSWER[0][0] == 'NULL':
        GET_ANSWER = 'SELECT e_words FROM korean WHERE num = %s;' % RANDOM_NUM
        RESULT_ANSWER = cur.execute(GET_ANSWER)
        ANSWER = cur.fetchall()
        bot.sendMessage(chat_id, text="What is %s ?\nTell me in English" % QUESTION[0][0])
        sys.exit(0)
    else:
        bot.sendMessage(chat_id, text="What is %s ?\nTell me in Russian" % QUESTION[0][0])
        sys.exit(0)

    FINISHED = 0
    bot.sendMessage(chat_id, text=ANSWER[0][0])
    while FINISHED == 1:
        time.sleep(1)
        if content_type == ANSWER[0][0]:
            FINISHED = 1
            bot.sendMessage(chat_id, text="Right!")
        else:
            bot.sendMessage(chat_id, text="Wrong!")


def on_chat_message(msg):
    telegram_conn = pymysql.connect(host='<DB IP Address>', user='<DB User>', password='<DB User Password>', db='<DB Name>', charset='utf8')
    telegram_conn.autocommit(True)
    cur = telegram_conn.cursor()
    content_type, chat_type, chat_id = telepot.glance(msg)

    help_msg = '''
/registry   - Registry an your id to receive an alarm
/enable     - Enable alarm 
/disable    - Disable alarm
/id           - show your chat id
/help         - print this help message
/init         - Initialization all words (Only admin)
  '''

    if content_type == 'text':
        if msg['text'] == '/registry':
            sql_registry = "INSERT INTO user (user_id) SELECT '%s' FROM DUAL WHERE NOT EXISTS (SELECT user_id FROM user WHERE user_id = '%s') LIMIT 1;" % (
            chat_id, chat_id)
            result = cur.execute(sql_registry)
            if result == 0:
                bot.sendMessage(chat_id, text="Your ID is already registered.")
            else:
                bot.sendMessage(chat_id, text="Your ID registration completed.")
        if msg['text'] == '/enable':
            sql_enable = "UPDATE user SET user_enable = '1' WHERE user_id = '%s';" % chat_id
            result = cur.execute(sql_enable)
            if result == 0:
                bot.sendMessage(chat_id, text="The message receiving alarm already Enabled.")
            else:
                bot.sendMessage(chat_id, text="The message receiving alarm Enabled.")
        if msg['text'] == '/disable':
            sql_disable = "UPDATE user SET user_enable = '0' WHERE user_id = '%s';" % chat_id
            result = cur.execute(sql_disable)
            if result == 0:
                bot.sendMessage(chat_id, text="The message receiving alarm already Disabled.")
            else:
                bot.sendMessage(chat_id, text="The message receiving alarm Disabled.")
        if msg['text'] == '/init':
            if chat_id == <관리자 Chat_ID>:
                sql_init = "UPDATE korean SET count = '0' WHERE count = '1';"
                cur.execute(sql_init)
                bot.sendMessage(chat_id, text="Initialization completed.")
            else:
                bot.sendMessage(chat_id, text="You are not a admin.")
        if msg['text'] == '/help':
            bot.sendMessage(chat_id, text="%s" % help_msg)
        if msg['text'] == '/id':
            bot.sendMessage(chat_id, text="Your ID is %s" % chat_id)
        if msg['text'] == '/msg':
            bot.sendMessage(chat_id, text=msg)
        if msg['text'] == '/quiz':
            quiz(msg)

    telegram_conn.close()

MessageLoop(bot, on_chat_message).run_as_thread()

logging.basicConfig()

while True:
    time.sleep(1)