import asyncio
import logging
import psycopg2
import re
import telebot
from telebot.async_telebot import AsyncTeleBot
import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bot = AsyncTeleBot('6942842247:AAGliFh74a5cKTCeFQ3TY_1VxgaZpbAbrUs')

try:
    conn = psycopg2.connect(
        dbname="luk",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
except Exception as e:
    logger.exception("Ошибка при подключении к базе данных: %s", e)

user_state = {}

async def userregistration(message):
    try:
        markup = telebot.types.ReplyKeyboardRemove()
        await bot.send_message(message.chat.id, f"Приветствую! Я чат бот с расписанием! Введите свою группу:", reply_markup=markup)
        user_state[message.chat.id] = {'Ожидание_группы': True}
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id].get('Ожидание_уведомлений'))
async def notifications1(message):
    try:
        await bot.send_message(message.chat.id, "Пожалуйста введите и отправьте уведомления: за час, за день, за день и за час, без уведомлений")
        notif_text = message.text.strip().lower()
        if notif_text not in ['за день', 'за час', 'за день и за час', 'без уведомлений']:
            await bot.send_message(message.chat.id,
                                   "Неверный формат уведомлений. Пожалуйста, выберите один из предложенных вариантов.")
            return
        user_state[message.chat.id]['notif'] = notif_text
        user_id = message.from_user.id
        p_group = user_state[message.chat.id]['group']
        p_notif = user_state[message.chat.id]['notif']

        cur.execute("INSERT INTO people (id_p, unicours, notif) VALUES (%s, %s, %s)", (user_id, p_group, p_notif))
        conn.commit()
        user_state[message.chat.id]['Ожидание_уведомлений'] = False

        await bot.send_message(message.chat.id, "Ваши данные сохранены. Спасибо!")
        await mainmenu(message)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(commands=['start', 'menu'])
async def start(message) :
    try :
        user_id = message.from_user.id
        cur.execute("SELECT * FROM people WHERE id_p = %s", (user_id,))
        user_data = cur.fetchone()

        if user_data :
            await mainmenu(message)
        else :
            await userregistration(message)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: message.chat.id in user_state and user_state[message.chat.id].get('Ожидание_группы'))
async def firstgroup(message):
    try :
        group_name = message.text.strip()
        if not await validate_format(group_name) :
            await bot.send_message(message.chat.id,
                                   "Неверный формат группы. Пожалуйста, введите название группы корректно. (Например ИСПк-201-51-00). При вводе вашей группы, обязательно приписывайте нули.")
            return
        user_state[message.chat.id]['group'] = group_name
        user_state[message.chat.id]['Ожидание_группы'] = False
        user_state[message.chat.id]['Ожидание_уведомлений'] = True
        await bot.send_message(message.chat.id, "Отлично! Теперь введите время уведомления(за день, за час, за день и за час или без уведомлений).")
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def validate_format(group_name):
    pattern = r'^[А-ЯЁа-яё]{3,4}-[0-9]{3}-[0-9]{2}-[0-9]{2}$'
    return re.match(pattern, group_name) is not None

async def mainmenu(message):
    try :
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        lessons_button = telebot.types.KeyboardButton('📖Расписание')
        settings_button = telebot.types.KeyboardButton('⚙️Настройки')
        find_teacher_button = telebot.types.KeyboardButton('👨🏻‍💼Поиск преподавателя')
        help_button = telebot.types.KeyboardButton('🆘Помощь')
        markup.add(lessons_button, settings_button)
        markup.add(find_teacher_button, help_button)
        await bot.send_message(message.chat.id, f"Приветствую! Что тебя интересует?", reply_markup=markup)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: message.text.lower() == '🗓моё расписание')
async def findgroupschedule(message):
    try :
        user_id = message.from_user.id
        group_name = await getusergroup(user_id)
        if group_name :
            await sendgroupschedule(message.chat.id, group_name)
        else :
            await bot.send_message(message.chat.id, "Ваша группа не найдена. Пожалуйста, убедитесь в существовании вашей группы или обратитесь к администратору.")
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def getusergroup(user_id):
    try :
        cur.execute("SELECT unicours FROM people WHERE id_p = %s", (user_id,))
        group_name = cur.fetchone()
        return group_name[0] if group_name else None
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def searchgroupschedule(group_name):
    try :
        cur.execute("SELECT id_group FROM groups WHERE name_group LIKE %s", (f"%{group_name}%",))
        group_ids = cur.fetchall()
        if group_ids :
            schedule_rows = []
            for group_id in group_ids :
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
        else :
            return None
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def sendgroupschedule(chat_id, group_name):
    try :
        await bot.send_message(chat_id, "Ваша группа найдена. Пожалуйста ждите.")
        group_schedule = await searchgroupschedule(group_name)
        if group_schedule :
            response = f"Расписание для группы(-ы) '{group_name}':\n"
            for row in group_schedule :
                response += f"------------------------------------------------------------\n"
                response += f"📅 {row[0]}\n"
                response += f"🕒 {row[1]}\n"
                if row[2] != "!" :
                    response += f"📚 {row[2]}\n"
                if row[3] != "." and row[3] != "!" :
                    response += f"🧪 {row[3]}\n"
                if row[4] != "!" :
                    response += f"👨🏻‍💼 {row[4]}\n"
                if row[5] != "!" :
                    response += f"🏛 Аудитория: {row[5]}\n"

            for i in range(0, len(response), 4000) :
                await bot.send_message(chat_id, response[i :i + 4000])
        else :
            await bot.send_message(chat_id,
                                   f"Расписание для групп(-ы) с названием, содержащим '{group_name}', не найдено.")
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def send_notif_za_den(chat_id, group_name):
    await bot.send_message(chat_id, "Ваша группа найдена. Пожалуйста, подождите.")
    group_schedule = await searchgroupschedule(group_name)
    if group_schedule:
        current_time = datetime.datetime.now()
        if current_time.hour == 18 and current_time.minute == 1:
            current_day = current_time.weekday()
            if current_day == 5:
                next_day = 0
            else:
                next_day = (current_day + 1) % 7

            days_of_week = [
                "ПОНЕДЕЛЬНИК",
                "ВТОРНИК",
                "СРЕДА",
                "ЧЕТВЕРГ",
                "ПЯТНИЦА",
                "СУББОТА",
                "ВОСКРЕСЕНЬЕ"
            ]
            next_day_name = days_of_week[next_day]
            response = f"Расписание для группы(-ы) '{group_name}' на {next_day_name}:\n"
            for row in group_schedule:
                if next_day_name in row[0].upper():
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
            if next_day_name not in response:
                await bot.send_message(chat_id, f"В расписании для группы '{group_name}' нет занятий на {next_day_name}.")
            else:
                for i in range(0, len(response), 4000):
                    await bot.send_message(chat_id, response[i:i + 4000])
        else:
            pass
    else:
        await bot.send_message(chat_id, f"Расписание для групп(-ы) с названием, содержащим '{group_name}', не найдено.")

async def send_notif_za_chas(chat_id, group_name):
    try:
        await bot.send_message(chat_id, "Ваша группа найдена. Пожалуйста, подождите.")
        group_schedule = await searchgroupschedule(group_name)
        if not group_schedule:
            await bot.send_message(chat_id, f"Расписание для групп(-ы) с названием, содержащим '{group_name}', не найдено.")
            return
        current_time = datetime.datetime.now()
        days_of_week = [
            "ПОНЕДЕЛЬНИК",
            "ВТОРНИК",
            "СРЕДА",
            "ЧЕТВЕРГ",
            "ПЯТНИЦА",
            "СУББОТА",
            "ВОСКРЕСЕНЬЕ"
        ]
        found_classes = False
        current_day = current_time.weekday()
        next_day = (current_day) % 7
        current_day_name = days_of_week[next_day]
        for row in group_schedule:
            if current_day_name in row[0].upper():
                response = f"Расписание для группы(-ы) '{group_name}' на {current_day_name}:\n"
                response += f"------------------------------------------------------------\n"
                response += f"📅 {row[0]}\n"
                response += f"🕒 {row[1]}\n"
                response += f"📚 {row[2]}\n" if row[2] != "!" else ""
                response += f"🧪 {row[3]}\n" if row[3] != "." and row[3] != "!" else ""
                response += f"👨🏻‍💼 {row[4]}\n" if row[4] != "!" else ""
                response += f"🏛 Аудитория: {row[5]}\n" if row[5] != "!" else ""
                await bot.send_message(chat_id, response)
                found_classes = True
        if not found_classes:
            await bot.send_message(chat_id, f"В расписании для группы '{group_name}' нет занятий на {current_day_name}.")
        else:
            pass
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message : message.text == '⚙️Настройки', )
async def settings(message) :
    try :
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        changegr = telebot.types.KeyboardButton('👨🏻‍🎓Сменить группу')
        changentf = telebot.types.KeyboardButton('🔔Сменить уведомления')
        menu = telebot.types.KeyboardButton('/menu')
        markup.add(changegr, changentf)
        markup.add(menu)
        await bot.send_message(message.chat.id, 'Что именно вы хотите сменить?', reply_markup=markup)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: message.text == '👨🏻‍🎓Сменить группу')
async def chnge_uni(message):
    try :
        await bot.send_message(message.chat.id,
                               'Чтобы сменить группу введите название группы корректно (например ИСПк-201-51-00). При вводе вашей группы, обязательно приписывайте нули.')
        user_state[message.chat.id] = {'Ожидание_группы1' : True}
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: True and user_state[message.chat.id].get('Ожидание_группы1'))
async def thewaiting(message):
    try :
        group_name = message.text.strip()
        pattern = r'^[А-ЯЁа-яё]{3,4}-[0-9]{3}-[0-9]{2}-[0-9]{2}$'
        if re.match(pattern, group_name) :
            await chnge_uni1(message, group_name)
            del user_state[message.chat.id]['Ожидание_группы1']
        else :
            await bot.send_message(message.chat.id,
                                   'Некорректный формат группы. Пожалуйста, введите группу в правильном формате.')
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def chnge_uni1(message, group_name):
    try :
        user_id = message.from_user.id
        p_group = group_name
        cur.execute("UPDATE people SET unicours = %s WHERE id_p = %s", (p_group, user_id))
        conn.commit()
        await bot.send_message(message.chat.id, "Отлично! Вы сменили свою группу.")
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: message.text == '🔔Сменить уведомления')
async def notifications(message):
    try :
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        onehour = telebot.types.KeyboardButton('Уведомлять за час до')
        oneday = telebot.types.KeyboardButton('Уведомлять за день до')
        hourday = telebot.types.KeyboardButton('Уведомлять за день и за час до')
        stopall = telebot.types.KeyboardButton('Отключить уведомления')
        menu = telebot.types.KeyboardButton('/menu')
        markup.add(onehour, oneday)
        markup.add(hourday, stopall)
        markup.add(menu)
        await bot.send_message(message.chat.id, '''Чтобы сменить уведомление нажмите на соответствующую кнопку. Уведомления привязываются к первой паре каждого дня из вашего расписания. Учтите это!''', reply_markup=markup)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message : message.text in ['Уведомлять за час до', 'Уведомлять за день до', 'Уведомлять за день и за час до', 'Отключить уведомления'])
async def handle_notifications(message) :
    try :
        notification_types = {
            'Уведомлять за час до' : 'за час',
            'Уведомлять за день до' : 'за день',
            'Уведомлять за день и за час до' : 'за день и за час',
            'Отключить уведомления' : 'без уведомлений'
        }
        notification_type = message.text
        notification_text = notification_types.get(notification_type)
        if notification_text is None :
            await bot.send_message(message.chat.id, "Неверный тип уведомления.")
            return

        user_state[message.chat.id] = {'notif' : notification_text}
        await update_notifindb(message)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def update_notifindb(message) :
    try :
        user_id = message.from_user.id
        p_notif = user_state[message.chat.id]['notif']
        cur.execute("UPDATE people SET notif = %s WHERE id_p = %s", (p_notif, user_id))
        conn.commit()
        await bot.send_message(message.chat.id, "Отлично! Вы сменили свои уведомления.")
    except Exception as e :
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: message.text == '📖Расписание')
async def lessons(message):
    try :
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        my_lessons = telebot.types.KeyboardButton('🗓Моё расписание')
        all_lessons = telebot.types.KeyboardButton('📚Расписание курса')
        back_to_menu = telebot.types.KeyboardButton('/menu')
        markup.add(my_lessons, all_lessons)
        markup.add(back_to_menu)
        await bot.send_message(message.chat.id, 'Выберите расписание', reply_markup=markup)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def searchteacher(lastname) :
    try :
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
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message : message.text == '👨🏻‍💼Поиск преподавателя')
async def find_teacher(message) :
    try :
        user_state[message.chat.id] = {'waiting_for_lastname' : True}
        await bot.send_message(message.chat.id, "Введите фамилию преподавателя:")
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(
    func=lambda message : message.chat.id in user_state and user_state[message.chat.id].get('waiting_for_lastname'))
async def teachername(message) :
    try :
        teacher_lastname = message.text
        if teacher_lastname == "!" :
            await bot.send_message(message.chat.id, "Расписание для данного преподавателя не найдено.")
            del user_state[message.chat.id]
            return
        teacher_lastname = message.text
        teacher_schedule = await  searchteacher(teacher_lastname)
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

            for i in range(0, len(response), 4000):
                await bot.send_message(message.chat.id, response[i :i + 4000])
        else :
            await bot.send_message(message.chat.id, "Расписание для данного преподавателя не найдено.")
            del user_state[message.chat.id]
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message : message.text == '🆘Помощь')
async def help(message) :
    await bot.send_message(message.chat.id,
                           f''' ❗ Справка для бота.
🤖Бот предоставляет услуги по уведомлению расписаний в личных сообщениях.
В разделе \"Расписание 📖\" можно найти кнопку, предоставляющую \"Ваше расписание\".
\"Ваше расписание🗓\" является расписанием для вами выбранной группы при начале работы с ботом.
Кнопка \"Преподаватель 👨🏻‍💼\" позволяет найти преподавателя в расписании по ФИО.
В разделе \"Настройки ⚙️\" присутствуют кнопки, изменяющие выбранную группу, изменяющие частоту уведомления.
В воскресенье неделя сменяется самостоятельно и для всех пользователей.
При возникновении внештатных ситуаций попробуйте сменить указанную вами группу.
🎉 Удачи в обучении. Спасибо, что пользуйтесь нашим ботом!''')

@bot.message_handler(func=lambda message: True)
async def handle_messages(message):
    try :
        if message.text not in ['📖Расписание', '⚙️Настройки', '👨🏻‍💼Поиск преподавателя', '🆘Помощь', '🗓Моё расписание',
                                '📚Расписание курса', '👨🏻‍🎓Сменить группу', '↔️Сменить неделю на следующую',
                                'Уведомлять за час до', 'Уведомлять за день до', 'Уведомлять за день и за час до',
                                'Отключить уведомления'] :
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            lessons0 = telebot.types.KeyboardButton('📖Расписание')
            settings0 = telebot.types.KeyboardButton('⚙️Настройки')
            findname0 = telebot.types.KeyboardButton('👨🏻‍💼Поиск преподавателя')
            help0 = telebot.types.KeyboardButton('🆘Помощь')
            markup.add(lessons0, settings0)
            markup.add(findname0, help0)
            await bot.send_message(message.chat.id,
                                   "Извините, не могу понять ваше сообщение. Выберите одну из опций ниже:",
                                   reply_markup=markup)
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

@bot.message_handler(func=lambda message: True)
async def findgroupnotif(message):
    cur.execute("SELECT id_p FROM people")
    user_id2 = cur.fetchone()
    group_name = await getusergroupnotif(user_id2)
    if group_name:
        await send_notif_za_den(message.chat.id, group_name)
    else:
        pass
    return user_id2[0] if user_id2 else None

async def getusergroupnotif(user_id2):
    cur.execute("SELECT unicours FROM people WHERE id_p = %s", (user_id2,))
    group_name = cur.fetchone()
    return group_name[0] if group_name else None

async def send_notif(interval_seconds):
        while True :
            cur.execute("SELECT id_p FROM people")
            user_id = cur.fetchone()
            cur.execute("SELECT notif FROM people WHERE id_p = %s", (user_id,))
            notifs = cur.fetchall()
            if not notifs == "за день" or not notifs == "за день и за час" :
                await asyncio.sleep(50)
            current_time = datetime.datetime.now()
            if current_time.hour == 18 and current_time.minute == 1 :
                cur.execute("SELECT id_p FROM people")
                user_ids = cur.fetchall()
                for user_id in user_ids :
                    group_name = await getusergroupnotif(user_id)
                    if group_name :
                        await send_notif_za_den(user_id[0], group_name)
            await asyncio.sleep(interval_seconds)


@bot.message_handler(func=lambda message: True)
async def find_group_notif2(message):
    try:
        cur.execute("SELECT id_p FROM people")
        user_id2 = cur.fetchone()
        group_name = await get_user_group_notif2(user_id2)
        if group_name:
            await send_notif_za_chas(message.chat.id, group_name)
        else:
            pass
        return user_id2[0] if user_id2 else None
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)

async def get_user_group_notif2(user_id2):
    try:
        cur.execute("SELECT unicours FROM people WHERE id_p = %s", (user_id2,))
        group_name = cur.fetchone()
        return group_name[0] if group_name else None
    except Exception as e:
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)



async def send_notif2(interval_seconds) :
    try :
            while True :
                cur.execute("SELECT id_p FROM people")
                user_id = cur.fetchone()
                cur.execute("SELECT notif FROM people WHERE id_p = %s", (user_id,))
                notifs = cur.fetchall()
                if not notifs == "за час" or not notifs == "за день и за час" :
                    await asyncio.sleep(50)
                current_time = datetime.datetime.now()
                if current_time.strftime("%H:%M") in ["7:20", "9:00", "10:45", "13:00", "14:45", "16:20", "17:55",
                                                      "12:20",
                                                      "13:55", "15:30"] :
                    cur.execute("SELECT id_p FROM people")
                    user_ids = cur.fetchall()
                    for user_id in user_ids :
                        group_name = await get_user_group_notif2(user_id)
                        if group_name :
                            await send_notif_za_chas(user_id[0], group_name)
                await asyncio.sleep(interval_seconds)
    except Exception as e :
        logger.exception("Произошла ошибка в обработчике уведомлений: %s", e)


async def main():
    try:
        interval_seconds = 50
        asyncio.ensure_future(send_notif(interval_seconds))
        asyncio.ensure_future(send_notif2(interval_seconds))
        await bot.polling(none_stop=True)
    except Exception as e:
        logger.exception("Произошла ошибка во время работы бота: %s", e)

if __name__ == "__main__":
    asyncio.run(main())