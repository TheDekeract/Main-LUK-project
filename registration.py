import telebot
import psycopg2

TOKEN = 'боря, тут токен'
conn = psycopg2.connect(database="Test", user="postgres", password="kursovaya", host="localhost", port="5432")
cursor = conn.cursor()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Начальный монолог")

@bot.message_handler(func=lambda message: True)
def register(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    # Запись данных
    try:
        cursor.execute("INSERT INTO people (unicours, notif) VALUES (%s, %s)", (user_id, username))
        conn.commit()
        bot.send_message(chat_id, f"Отлично {username}, теперь ты будешь знать все свое расписание и тебе придется ходить на пары!!!!!")
    except (Exception, psycopg2.Error) as error:
        print("Разрыв петарды", error)
        conn.rollback()
        bot.send_message(chat_id, "На пары можешь не ходить, расписания нет")

bot.polling()
