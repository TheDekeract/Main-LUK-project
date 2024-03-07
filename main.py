import types
import telebot
from telebot.async_telebot import AsyncTeleBot

# Указываем токен вашего бота, который вы получили у BotFather Создаем экземпляр бота
bot = AsyncTeleBot('6942842247:AAGliFh74a5cKTCeFQ3TY_1VxgaZpbAbrUs')


# Обработчик команды /start
@bot.message_handler(commands=['start', 'menu'])
async def handle_start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lessons0 = telebot.types.KeyboardButton('📖Расписание')
    settings0 = telebot.types.KeyboardButton('⚙️Настройки')
    findname0 = telebot.types.KeyboardButton('👨🏻‍💼Поиск преподавателя')
    help0 = telebot.types.KeyboardButton('🆘Помощь')
    markup.add(lessons0, settings0)
    markup.add(findname0, help0)
    await bot.send_message(message.chat.id, "Приветствую, я чат бот с расписанием! Что тебя интересует?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '📖Расписание')
async def lessons(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mylessons = telebot.types.KeyboardButton('🗓Моё расписание')
    alllessons = telebot.types.KeyboardButton('📚Расписание курса')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(mylessons, alllessons)
    markup.add(menu)
    await bot.send_message(message.chat.id, 'Здесь будет расписание', reply_markup=markup)


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

@bot.message_handler(func=lambda message: message.text == '👨🏻‍💼Поиск преподавателя')
async def findname(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(menu)
    await bot.send_message(message.chat.id, 'Здесь будет поиск по именам')


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


# Запускаем бота
import asyncio
asyncio.run(bot.polling(none_stop=True))