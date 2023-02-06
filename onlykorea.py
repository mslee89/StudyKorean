# -*- coding: utf-8 -*-
import pymysql, time, telepot, sys
from socket import error as SocketError

# 텔레그램 봇 선택
token = '<Telegram Token>'
bot = telepot.Bot(token)


def Korea():
    # DB 커넥션 생성
    korea_conn = pymysql.connect(host='<DB IP Address>', user='<DB User>', password='<DB User Password>', db='<DB Name>', charset='utf8')
    korea_conn.autocommit(True)
    cur = korea_conn.cursor()

    # count 값이 0 인 경우 최대 10까지 조회
    rand_sel_sql = "select num,k_words,e_words,r_words from korean where count = '0' order by rand() limit 10;"
    cur.execute(rand_sel_sql)
    rows = cur.fetchall()

    # 만약 데이터가 10개가 되지 않는다면 모든 값을 초기화시켜서 전송
    if len(rows) == 10:
        pass
    else:
        init_count_sql = "UPDATE korean SET count = '0' WHERE num = '1'"
        cur.execute(init_count_sql)
        # Korea()

    # count 값과 현재 시간값 초기화
    count = 0
    now = time.gmtime(time.time())

    # 오늘의 단어 메시지 구성
    msg = '*--- %s.%s.%s Words of today ---*\n\n' % (now.tm_year, now.tm_mon, now.tm_mday)

    # 전송 할 메시지 구성. 이 항목에 포함된 단어는 초기화 될 때까지 비활성화
    for i in rows:
        update_count_sql = "UPDATE korean SET count = '1' WHERE num = %s;" % i[0]
        cur.execute(update_count_sql)
        count += 1
        if type(i[2]) == type(None):
            msg += "%s.\t%s\t %s\n" % (count, i[1], i[3])
        elif type(i[3]) == type(None):
            msg += "%s.\t%s\t %s\n" % (count, i[1], i[2])
    msg += "\n\nYou wanna know how to use this bot? Then looking for @HanwooBot in telegraf and enter /help"

    # 전송 할 유저 찾기
    user = "select user_id from user where user_enable = '1';"
    cur.execute(user)
    user_rows = cur.fetchall()

    # 각 유저에게 정리된 메시지를 전송
    #  for num in range(0, int(str(len(user_rows)))):
    #    for account in user_rows[int(num)]:
    #      try:
    #        bot.sendMessage(account, text='%s' % msg)
    #        #sys.exit(0)
    #      except SocketError as e:
    #        if e.errno != errno.ECONNRESET:
    #          raise
    #      pass
    for account in user_rows:
        try:
            bot.sendMessage(account[0], text='%s' % msg)
            print
            account[0]
        except SocketError as e:
            if e.errno != errno.ECONNRESET:
                raise
        pass

    korea_conn.close()

sys.setrecursionlimit(2000)
Korea()