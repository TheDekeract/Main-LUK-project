import psycopg2
from datetime import datetime
import time
import telebot
import threading

TOKEN = '6496955434:AAHbsCqh97HcRaWsYvCniZYHUeZ2qZlSyA4'
bot = telebot.TeleBot(TOKEN)

def proverkaschedule(conn):
    try:
        cursor = conn.cursor()
        current_time = datetime.now().time()
        sql_query = "SELECT day_of_week_and_date, time_range FROM schedule"
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        if not rows:
            print("В базе данных отсутствуют данные о расписании.")
            return

        found_match = False

        for row in rows:
            time_range = row[1].strip()
            start_time_str, end_time_str = time_range.split('-')
            start_time = datetime.strptime(start_time_str.strip(), '%H.%M').time()
            end_time = datetime.strptime(end_time_str.strip(), '%H.%M').time()

            if start_time <= current_time <= end_time:
                found_match = True
                print("Обнаружено соответствие в расписании. Начинается отсчет времени до отправки сообщения.")
                threading.Thread(target=otschet, args=(10,)).start()
                threading.Timer(10, otpravkasoobchenii, args=(conn,)).start()
                break

        if not found_match:
            print("Соответствие в расписании не найдено. Повторная проверка через некоторое время...")
            time.sleep(10)
            proverkaschedule(conn)

    except psycopg2.Error as e:
        print("Ошибка при работе с базой данных:", e)

def otschet(seconds):
    for i in range(seconds, 0, -1):
        print(f"Осталось {i} секунд до отправки сообщения...")
        time.sleep(1)

def otpravkasoobchenii(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_p, unicours FROM people")
            rows = cursor.fetchall()
            for row in rows:
                id_p = row[0]
                message = row[1]
                # Отправляем сообщение каждому пользователю на основе их id_p
                bot.send_message(chat_id=id_p, text=message)
                print("Сообщение успешно отправлено пользователю с id_p =", id_p)
    except Exception as e:
        print("Ошибка при отправке сообщения:", e)

if __name__ == "__main__":
    dbname = "Test"
    user = "postgres"
    password = "kyrsovaya"
    host = "localhost"
    port = "5432"

    with psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port) as conn:
        proverkaschedule(conn)