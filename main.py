import asyncio
import psycopg2
import telebot
import re
from telebot.async_telebot import AsyncTeleBot

# Указываем токен вашего бота, который вы получили у BotFather Создаем экземпляр бота
bot = AsyncTeleBot('6942842247:AAGliFh74a5cKTCeFQ3TY_1VxgaZpbAbrUs')

conn = psycopg2.connect(
        dbname="luk",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
cur = conn.cursor()

user_state = {}

# Обработчик команды /start
@bot.message_handler(commands=['start', 'menu'])
async def handle_start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lessons0 = telebot.types.KeyboardButton('📖Расписание')
    settings0 = telebot.types.KeyboardButton('⚙️Настройки')
    findname0 = telebot.types.KeyboardButton('👨🏻‍💼Поиск преподавателя')
    help0 = telebot.types.KeyboardButton('🆘Помощь')
    username = message.from_user.first_name
    markup.add(lessons0, settings0)
    markup.add(findname0, help0)
    await bot.send_message(message.chat.id, f"Приветствую, {username}! Я чат бот с расписанием! Что тебя интересует?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '📖Расписание')
async def lessons(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mylessons = telebot.types.KeyboardButton('🗓Моё расписание')
    alllessons = telebot.types.KeyboardButton('📚Расписание курса')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(mylessons, alllessons)
    markup.add(menu)
    await bot.send_message(message.chat.id, 'Выберите расписание', reply_markup=markup)

def search_group(group_name):
    cur.execute("SELECT id_group FROM groups WHERE name_group LIKE %s", (f"%{group_name}%",))
    group_ids = cur.fetchall()
    if group_ids:
        schedule_rows = []
        for group_id in group_ids:
            cur.execute("""
                SELECT
                    schedule.day_of_week_and_date,
                    schedule.time_range,
                    disciplines.name_discipline,
                    schedule.lesson_type,
                    teachers.full_name,
                    audiences.room_number
                FROM
                    schedule
                    JOIN disciplines ON schedule.id_discipline = disciplines.id_discipline
                    JOIN teachers ON schedule.id_teacher = teachers.id_teacher
                    JOIN audiences ON schedule.id_audience = audiences.id_audience
                WHERE
                    schedule.id_group = %s
            """, (group_id[0],))
            schedule_rows.extend(cur.fetchall())
        return schedule_rows
    else:
        return None

@bot.message_handler(func=lambda message: message.text == '🗓Моё расписание')
async def find_group_schedule(message):
    user_state[message.chat.id] = {'waiting_for_group': True}
    await bot.send_message(message.chat.id, "Для поиска введите название группы:")

def validate_group_format(group_name):
    pattern = r'^[А-ЯЁа-яё]{3,4}\-[0-9]{3}\-[0-9]{2}\-[0-9]{2}$'  # Паттерн для проверки формата группы
    return re.match(pattern, group_name) is not None


@bot.message_handler(
    func=lambda message: message.chat.id in user_state and user_state[message.chat.id].get('waiting_for_group'))
async def process_group_name(message):
    group_name = message.text.strip()
    if not validate_group_format(group_name):
        await bot.send_message(message.chat.id,
                               "Неверный формат группы. Пожалуйста, введите название группы корректно. (Например ИСПк-201-51-00) При вводе вашей группы, обязательно приписывайте нули.")
        return

    group_schedule = search_group(group_name)
    if group_schedule:
        response = f"Расписание для группы(-ы) '{group_name}':\n"
        for row in group_schedule:
            response += f"------------------------------------------------------------\n"
            response += f"📅 День и дата: {row[0]}\n"
            response += f"🕒 Время: {row[1]}\n"
            if row[2] != "!":
                response += f"📚 Дисциплина: {row[2]}\n"
            if row[3] != "." and row[3] != "!":
                response += f"🧪 Тип занятия: {row[3]}\n"
            if row[4] != "!":
                response += f"👨🏻‍💼 Преподаватель: {row[4]}\n"
            if row[5] != "!":
                response += f"🏛 Аудитория: {row[5]}\n"


        for i in range(0, len(response), 4096):
            await bot.send_message(message.chat.id, response[i:i + 4096])
    else:
        await bot.send_message(message.chat.id,
                               f"Расписание для группы(-ы) с названием, содержащим '{group_name}', не найдено.")

    del user_state[message.chat.id]



@bot.message_handler(func=lambda message: message.text == '⚙️Настройки', )
async def settings(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    changegr = telebot.types.KeyboardButton('👨🏻‍🎓Сменить группу')
    changentf = telebot.types.KeyboardButton('🔔Сменить уведомления')
    changeweek = telebot.types.KeyboardButton('↔️Сменить неделю на следующую')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(changegr, changentf)
    markup.add(changeweek, menu)
    await bot.send_message(message.chat.id, 'Здесь будут настройки', reply_markup=markup)
@bot.message_handler(func=lambda message: message.text == '🔔Сменить уведомления', )
async def notifications(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    onehour = telebot.types.KeyboardButton('Уведомлять за час до')
    oneday = telebot.types.KeyboardButton('Уведомлять за день до')
    hourday = telebot.types.KeyboardButton('Уведомлять за час и за день до')
    stopall = telebot.types.KeyboardButton('Отключить уведомления')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(onehour, oneday)
    markup.add(hourday,stopall)
    markup.add(menu)
    await bot.send_message(message.chat.id, '''Чтобы сменить уведомление нажмите на соответствующую кнопку.
Уведомления привязываются к первой паре каждого дня из вашего расписания.
Учтите это!''', reply_markup=markup)

def searchteacher(lastname):
    cur.execute("SELECT id_teacher FROM teachers WHERE full_name LIKE %s", (f"%{lastname}%",))
    teacher_id = cur.fetchone()
    if teacher_id:
        cur.execute("""
            SELECT
                groups.name_group,
                schedule.day_of_week_and_date,
                schedule.time_range,
                disciplines.name_discipline,
                schedule.lesson_type,
                audiences.room_number
            FROM
                schedule
                JOIN groups ON schedule.id_group = groups.id_group
                JOIN disciplines ON schedule.id_discipline = disciplines.id_discipline
                JOIN audiences ON schedule.id_audience = audiences.id_audience
            WHERE
                schedule.id_teacher = %s
        """, (teacher_id[0],))
        schedule_rows = cur.fetchall()
        return schedule_rows
    else:
        return None

@bot.message_handler(func=lambda message: message.text == '👨🏻‍💼Поиск преподавателя')
async def find_teacher(message):
    user_state[message.chat.id] = {'waiting_for_lastname': True}
    await bot.send_message(message.chat.id, "Введите фамилию преподавателя:")

@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id].get('waiting_for_lastname'))
async def process_teacher_name(message):
    teacher_lastname = message.text
    if teacher_lastname == "!":
        await bot.send_message(message.chat.id, "Расписание для данного преподавателя не найдено.")
        del user_state[message.chat.id]
        return

    teacher_lastname = message.text
    teacher_schedule = searchteacher(teacher_lastname)
    if teacher_schedule:
        response = f"Расписание преподавателя {teacher_lastname}:\n"
        for row in teacher_schedule:
            response += f"------------------------------------------------------------\n👫 {row[0]}\n"
            response += f"📅День и дата: {row[1]}\n"
            response += f"🕒Время: {row[2]}\n"
            response += f"📚Дисциплина: {row[3]}\n"
            if row[4] != ".":
                response += f"🧪Тип занятия: {row[4]}\n"
            response += f"🏛Аудитория: {row[5]}\n"
        await bot.send_message(message.chat.id, response)
    else:
        await bot.send_message(message.chat.id, "Расписание для данного преподавателя не найдено.")
    del user_state[message.chat.id]

@bot.message_handler(func=lambda message: message.text == '🆘Помощь')
async def help(message):
    await bot.send_message(message.chat.id,
                     f''' ❗ Справка для бота.
🤖Бот предоставляет услуги по уведомлению расписаний в беседах и личных сообщениях.
В разделе \"Расписание 📖\" можно найти кнопки, предоставляющие \"Ваше расписание\" и \"Общее расписание колледжа\".
\"Ваше расписание🗓\" является расписанием для вами выбранной группы.
Кнопка \"Преподаватель 👨🏻‍💼\" позволяет найти преподавателя в расписании по ФИО.
В разделе \"Настройки ⚙️\" присутствуют кнопки, изменяющие выбранную группу, изменяющие частоту уведомления, а также обновление🔄 недели общего расписания (по возможности).
Обновление недели может произойти только тогда, когда в бот была добавлена следующая неделя, а воскресенье еще не наступило.
В воскресенье неделя сменяется самостоятельно и для всех пользователей.
🎉 Удачи в обучении. Спасибо, что пользуйтесь нашим ботом!''')

@bot.message_handler(func=lambda message: True)
async def handle_messages(message):
    if message.text not in ['📖Расписание', '⚙️Настройки', '👨🏻‍💼Поиск преподавателя', '🆘Помощь', '🗓Моё расписание', '📚Расписание курса', '👨🏻‍🎓Сменить группу', '↔️Сменить неделю на следующую', 'Уведомлять за час до', 'Уведомлять за день до',  'Уведомлять за час и за день до', 'Отключить уведомления']:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        lessons0 = telebot.types.KeyboardButton('📖Расписание')
        settings0 = telebot.types.KeyboardButton('⚙️Настройки')
        findname0 = telebot.types.KeyboardButton('👨🏻‍💼Поиск преподавателя')
        help0 = telebot.types.KeyboardButton('🆘Помощь')
        markup.add(lessons0, settings0)
        markup.add(findname0, help0)
        await bot.send_message(message.chat.id, "Извините, не могу понять ваше сообщение. Выберите одну из опций ниже:", reply_markup=markup)


async def main():
    await bot.polling(none_stop=True)

if __name__ == "__main__":
    asyncio.run(main())