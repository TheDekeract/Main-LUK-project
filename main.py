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


# @bot.message_handler(commands=['start', 'menu'])
# async def first_start(message):
#     username = message.from_user.first_name
#     user_state[message.chat.id] = {'Ожидание_группы': True, 'group': None, 'notif': None}
#     await bot.send_message(message.chat.id, f"Приветствую, {username}! Я чат бот с расписанием! Введите свою группу")

@bot.message_handler(
    func=lambda message: message.chat.id in user_state and user_state[message.chat.id].get('Ожидание_группы'))
async def firstgroup(message):
    group_name = message.text.strip()
    if not validate_group_format(group_name):
        await bot.send_message(message.chat.id,
                               "Неверный формат группы. Пожалуйста, введите название группы корректно. (Например ИСПк-201-51-00). При вводе вашей группы, обязательно приписывайте нули.")
        return
    user_state[message.chat.id]['group'] = group_name
    user_state[message.chat.id]['Ожидание_группы'] = False
    user_state[message.chat.id]['Ожидание_уведомлений'] = True
    await bot.send_message(message.chat.id, "Отлично! Теперь введите время уведомления.")
async def validate_group_format(group_name) :
    pattern = r'^[А-ЯЁа-яё]{3,4}\-[0-9]{3}\-[0-9]{2}\-[0-9]{2}$'  # Паттерн для проверки формата группы
    return re.match(pattern, group_name) is not None
@bot.message_handler(commands=['start', 'menu'])
async def handle_start(message) :
    user_id = message.from_user.id
    cur.execute("SELECT * FROM people WHERE id_p = %s", (user_id,))
    user_data = cur.fetchone()

    if user_data :
        await send_main_menu(message.chat.id)
    else :
        await new_user_registration(message.chat.id)


async def send_main_menu(chat_id) :
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lessons_button = telebot.types.KeyboardButton('📖 Расписание')
    settings_button = telebot.types.KeyboardButton('⚙️ Настройки')
    find_teacher_button = telebot.types.KeyboardButton('👨🏻‍💼 Поиск преподавателя')
    help_button = telebot.types.KeyboardButton('🆘 Помощь')
    markup.add(lessons_button, settings_button)
    markup.add(find_teacher_button, help_button)
    await bot.send_message(chat_id, f"Приветствую! Что тебя интересует?", reply_markup=markup)

async def new_user_registration(chat_id) :
    markup = telebot.types.ReplyKeyboardRemove()
    await bot.send_message(chat_id, f"Приветствую! Я чат бот с расписанием! Введите свою группу:",
                           reply_markup=markup)
    user_state[chat_id] = {'Ожидание_группы' : True}

@bot.message_handler(
    func=lambda message : message.chat.id in user_state and user_state[message.chat.id].get('Ожидание_уведомлений'))
async def notifications1(message) :
    notif_text = message.text.strip().lower()
    if notif_text not in ['за день', 'за час', 'за день и за час', 'без уведомлений'] :
        await bot.send_message(message.chat.id,
                               "Неверный формат уведомлений. Пожалуйста, выберите один из предложенных вариантов.")
        return
    user_state[message.chat.id]['notif'] = notif_text
    user_id = message.from_user.id
    p_group = user_state[message.chat.id]['group']
    p_notif = user_state[message.chat.id]['notif']
    cur.execute("INSERT INTO people (id_p, unicours, notif) VALUES (%s, %s, %s)", (user_id, p_group, p_notif))
    conn.commit()
    await bot.send_message(message.chat.id, "Ваши данные сохранены. Спасибо!")
    await send_main_menu(message.chat.id)









@bot.message_handler(func=lambda message: message.text == '🗓Моё расписание')
async def find_group_schedule(message):
    user_id = message.from_user.id
    group_name = await get_user_group(user_id)
    if group_name:
        await send_group_schedule(message.chat.id, group_name)
    else:
        await bot.send_message(message.chat.id, "Ваша группа не найдена. Пожалуйста, обратитесь к администратору.")

async def get_user_group(user_id):
    cur.execute("SELECT unicours FROM people WHERE id_p = %s", (user_id,))
    group_name = cur.fetchone()
    return group_name[0] if group_name else None

async def search_group_schedule(group_name):
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

async def send_group_schedule(chat_id, group_name):
    await bot.send_message(chat_id, "Ваша группа найдена. Пожалуйста ждите.")
    group_schedule = await search_group_schedule(group_name)
    if group_schedule:
        response = f"Расписание для группы(-ы) '{group_name}':\n"
        for row in group_schedule:
            response += f"------------------------------------------------------------\n"
            response += f"📅 {row[0]}\n"
            response += f"🕒 {row[1]}\n"
            if row[2] != "!":
                response += f"📚 {row[2]}\n"
            if row[3] != "." and row[3] != "!":
                response += f"🧪 {row[3]}\n"
            if row[4] != "!":
                response += f"👨🏻‍💼 {row[4]}\n"
            if row[5] != "!":
                response += f"🏛 Аудитория: {row[5]}\n"

        for i in range(0, len(response), 4000):
            await bot.send_message(chat_id, response[i:i + 4000])
    else:
        await bot.send_message(chat_id, f"Расписание для групп(-ы) с названием, содержащим '{group_name}', не найдено.")


@bot.message_handler(func=lambda message : message.text == '⚙️Настройки', )
async def settings(message) :
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    changegr = telebot.types.KeyboardButton('👨🏻‍🎓Сменить группу')
    changentf = telebot.types.KeyboardButton('🔔Сменить уведомления')
    changeweek = telebot.types.KeyboardButton('↔️Сменить неделю на следующую')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(changegr, changentf)
    markup.add(changeweek, menu)
    await bot.send_message(message.chat.id, 'Здесь будут настройки', reply_markup=markup)


@bot.message_handler(func=lambda message : message.text == '🔔Сменить уведомления', )
async def notifications(message) :
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    onehour = telebot.types.KeyboardButton('Уведомлять за час до')
    oneday = telebot.types.KeyboardButton('Уведомлять за день до')
    hourday = telebot.types.KeyboardButton('Уведомлять за час и за день до')
    stopall = telebot.types.KeyboardButton('Отключить уведомления')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(onehour, oneday)
    markup.add(hourday, stopall)
    markup.add(menu)
    await bot.send_message(message.chat.id, '''Чтобы сменить уведомление нажмите на соответствующую кнопку.
Уведомления привязываются к первой паре каждого дня из вашего расписания.
Учтите это!''', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '📖Расписание')
async def lessons(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mylessons = telebot.types.KeyboardButton('🗓Моё расписание')
    alllessons = telebot.types.KeyboardButton('📚Расписание курса')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(mylessons, alllessons)
    markup.add(menu)
    await bot.send_message(message.chat.id, 'Выберите расписание', reply_markup=markup)

def searchteacher(lastname) :
    cur.execute("SELECT id_teacher FROM teachers WHERE full_name LIKE %s", (f"%{lastname}%",))
    teacher_id = cur.fetchone()
    if teacher_id :
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
    else :
        return None


@bot.message_handler(func=lambda message : message.text == '👨🏻‍💼Поиск преподавателя')
async def find_teacher(message) :
    user_state[message.chat.id] = {'waiting_for_lastname' : True}
    await bot.send_message(message.chat.id, "Введите фамилию преподавателя:")


@bot.message_handler(
    func=lambda message : message.chat.id in user_state and user_state[message.chat.id].get('waiting_for_lastname'))
async def process_teacher_name(message) :
    teacher_lastname = message.text
    if teacher_lastname == "!" :
        await bot.send_message(message.chat.id, "Расписание для данного преподавателя не найдено.")
        del user_state[message.chat.id]
        return

    teacher_lastname = message.text
    teacher_schedule = searchteacher(teacher_lastname)
    if teacher_schedule :
        response = f"Расписание преподавателя {teacher_lastname}:\n"
        for row in teacher_schedule :
            response += f"------------------------------------------------------------\n👫 {row[0]}\n"
            response += f"📅 {row[1]}\n"
            response += f"🕒Время: {row[2]}\n"
            response += f"📚Дисциплина: {row[3]}\n"
            if row[4] != "." :
                response += f"🧪Тип занятия: {row[4]}\n"
            response += f"🏛Аудитория: {row[5]}\n"
        await bot.send_message(message.chat.id, response)
    else :
        await bot.send_message(message.chat.id, "Расписание для данного преподавателя не найдено.")
    del user_state[message.chat.id]


@bot.message_handler(func=lambda message : message.text == '🆘Помощь')
async def help(message) :
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


@bot.message_handler(func=lambda message : True)
async def handle_messages(message) :
    if message.text not in ['📖Расписание', '⚙️Настройки', '👨🏻‍💼Поиск преподавателя', '🆘Помощь', '🗓Моё расписание',
                            '📚Расписание курса', '👨🏻‍🎓Сменить группу', '↔️Сменить неделю на следующую',
                            'Уведомлять за час до', 'Уведомлять за день до', 'Уведомлять за час и за день до',
                            'Отключить уведомления'] :
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        lessons0 = telebot.types.KeyboardButton('📖Расписание')
        settings0 = telebot.types.KeyboardButton('⚙️Настройки')
        findname0 = telebot.types.KeyboardButton('👨🏻‍💼Поиск преподавателя')
        help0 = telebot.types.KeyboardButton('🆘Помощь')
        markup.add(lessons0, settings0)
        markup.add(findname0, help0)
        await bot.send_message(message.chat.id, "Извините, не могу понять ваше сообщение. Выберите одну из опций ниже:",
                               reply_markup=markup)


async def main() :
    await bot.polling(none_stop=True)


if __name__ == "__main__" :
    asyncio.run(main())