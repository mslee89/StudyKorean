# -*- coding: utf-8 -*-
import pymysql
import time
import telepot
from socket import error as SocketError

# 텔레그램 봇 설정
token = '<Telegram Token>'
bot = telepot.Bot(token)

def get_random_words(cursor):
    cursor.execute("SELECT num, k_words, e_words, r_words FROM korean WHERE count = '0' ORDER BY RAND() LIMIT 10;")
    return cursor.fetchall()

def reset_word_count(cursor):
    cursor.execute("UPDATE korean SET count = '0' WHERE num = '1'")

def update_word_count(cursor, num):
    cursor.execute("UPDATE korean SET count = '1' WHERE num = %s;", (num,))

def get_enabled_users(cursor):
    cursor.execute("SELECT user_id FROM user WHERE user_enable = '1';")
    return [row[0] for row in cursor.fetchall()]

def send_message_to_users(users, message):
    for user_id in users:
        try:
            bot.sendMessage(user_id, text=message)
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise

def korea():
    # DB 커넥션 생성
    with pymysql.connect(
        host='<DB IP Address>', user='<DB User>', password='<DB User Password>', db='<DB Name>', charset='utf8'
    ) as conn:
        with conn.cursor() as cursor:
            conn.autocommit(True)
            words = get_random_words(cursor)
            
            if len(words) < 10:
                reset_word_count(cursor)
                words = get_random_words(cursor)
            
            now = time.gmtime(time.time())
            msg = f'*--- {now.tm_year}.{now.tm_mon}.{now.tm_mday} Words of today ---*\n\n'
            
            for count, (num, k_word, e_word, r_word) in enumerate(words, start=1):
                update_word_count(cursor, num)
                translation = e_word if e_word else r_word
                msg += f"{count}.\t{k_word}\t{translation}\n"
            
            msg += "\n\nYou wanna know how to use this bot? Then looking for @HanwooBot in Telegram and enter /help"
            
            users = get_enabled_users(cursor)
            send_message_to_users(users, msg)

if __name__ == "__main__":
    korea()
