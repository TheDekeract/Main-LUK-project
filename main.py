import types
import telebot
from telebot.async_telebot import AsyncTeleBot

# Указываем токен вашего бота, который вы получили у BotFather Создаем экземпляр бота
bot = AsyncTeleBot('6524851966:AAH8Sv5CO16nLanHmMthGPOoTqmwpB5ecNU')


# Обработчик команды /start
@bot.message_handler(commands=['start', 'menu'])
async def handle_start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lessons0 = telebot.types.KeyboardButton('Расписание')
    settings0 = telebot.types.KeyboardButton('Настройки')
    findname0 = telebot.types.KeyboardButton('Поиск преподавателя')
    help0 = telebot.types.KeyboardButton('Помощь')
    markup.add(lessons0)
    markup.add(settings0)
    markup.add(findname0)
    markup.add(help0)
    await bot.send_message(message.chat.id, "Приветствую", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Расписание')
async def lessons(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mylessons = telebot.types.KeyboardButton('Моё расписание')
    alllessons = telebot.types.KeyboardButton('Расписание курса')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(mylessons)
    markup.add(alllessons)
    markup.add(menu)
    await bot.send_message(message.chat.id, 'Здесь будет расписание', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Настройки', )
async def settings(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    changegr = telebot.types.KeyboardButton('Сменить группу')
    changentf = telebot.types.KeyboardButton('Сменить уведомления')
    changeweek = telebot.types.KeyboardButton('Сменить неделю на следующую')
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(changegr)
    markup.add(changentf)
    markup.add(changeweek)
    markup.add(menu)
    await bot.send_message(message.chat.id, 'Здесь будут настройки', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Поиск преподавателя')
async def findname(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    menu = telebot.types.KeyboardButton('/menu')
    markup.add(menu)
    await bot.send_message(message.chat.id, 'Здесь будет поиск по именам')


@bot.message_handler(func=lambda message: message.text == 'Помощь')
async def help(message):
    await bot.send_message(message.chat.id,
                     '''  Справка для бота.
Бот предоставляет услуги по уведомлению расписаний в беседах и личных сообщениях.
В разделе \"Расписание\" можно найти кнопки, предоставляющие \"Ваше расписание\" и \"Общее расписание колледжа\".
\"Ваше расписание\" является расписанием для вами выбранной группы.
Кнопка \"Преподаватель\" позволяет найти преподавателя в расписании по ФИО.
В разделе \"Настройки\" присутствуют кнопки, изменяющие выбранную группу, изменяющие частоту уведомления, а также обновление недели общего расписания (по возможности).
Обновление недели может произойти только тогда, когда в бот была добавлена следующая неделя, а воскресенье еще не наступило.
В воскресенье неделя сменяется самостоятельно и для всех пользователей.
Удачи в обучении. Спасибо, что пользуйтесь нашим ботом!''')


# Запускаем бота
import asyncio
asyncio.run(bot.polling(none_stop=True))