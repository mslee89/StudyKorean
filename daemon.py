# -*- coding: utf-8 -*-
import time
import random
import logging
import pymysql
import telepot
from telepot.loop import MessageLoop

# Telegram Bot Token
token = '<Telegram Token>'
bot = telepot.Bot(token)

# Database Connection Function
def get_db_connection():
    return pymysql.connect(
        host='<DB IP Address>',
        user='<DB User>',
        password='<DB User Password>',
        db='<DB Name>',
        charset='utf8',
        autocommit=True
    )

# Quiz Function
def quiz(chat_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT num FROM korean ORDER BY num DESC LIMIT 1;')
            max_num = cur.fetchone()[0]
            random_num = random.randint(1, max_num)

            cur.execute('SELECT k_words FROM korean WHERE num = %s;', (random_num,))
            question = cur.fetchone()[0]

            cur.execute('SELECT r_words FROM korean WHERE num = %s;', (random_num,))
            answer = cur.fetchone()[0]

            if answer == 'NULL':
                cur.execute('SELECT e_words FROM korean WHERE num = %s;', (random_num,))
                answer = cur.fetchone()[0]
                bot.sendMessage(chat_id, text=f"What is {question} ?\nTell me in English")
            else:
                bot.sendMessage(chat_id, text=f"What is {question} ?\nTell me in Russian")

# Command Handler
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type != 'text':
        return
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            command = msg['text']
            
            if command == '/registry':
                cur.execute("INSERT INTO user (user_id) SELECT %s FROM DUAL WHERE NOT EXISTS (SELECT user_id FROM user WHERE user_id = %s) LIMIT 1;", (chat_id, chat_id))
                bot.sendMessage(chat_id, text="Your ID registration completed." if cur.rowcount else "Your ID is already registered.")
            
            elif command == '/enable':
                cur.execute("UPDATE user SET user_enable = '1' WHERE user_id = %s;", (chat_id,))
                bot.sendMessage(chat_id, text="The message receiving alarm Enabled." if cur.rowcount else "The message receiving alarm already Enabled.")
            
            elif command == '/disable':
                cur.execute("UPDATE user SET user_enable = '0' WHERE user_id = %s;", (chat_id,))
                bot.sendMessage(chat_id, text="The message receiving alarm Disabled." if cur.rowcount else "The message receiving alarm already Disabled.")
            
            elif command == '/init':
                if chat_id == <관리자 Chat_ID>:
                    cur.execute("UPDATE korean SET count = '0' WHERE count = '1';")
                    bot.sendMessage(chat_id, text="Initialization completed.")
                else:
                    bot.sendMessage(chat_id, text="You are not an admin.")
            
            elif command == '/help':
                help_msg = """
/registry   - Register your ID to receive alarms
/enable     - Enable alarms
/disable    - Disable alarms
/id         - Show your chat ID
/help       - Show this help message
/init       - Reset all words (Admin only)
/quiz       - Start a quiz
"""
                bot.sendMessage(chat_id, text=help_msg)
            
            elif command == '/id':
                bot.sendMessage(chat_id, text=f"Your ID is {chat_id}")
            
            elif command == '/quiz':
                quiz(chat_id)

# Start Bot
MessageLoop(bot, on_chat_message).run_as_thread()
logging.basicConfig()
while True:
    time.sleep(1)
