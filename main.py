import telebot
from telebot import types

# Указываем токен вашего бота, который вы получили у BotFather
TOKEN = '6524851966:AAH8Sv5CO16nLanHmMthGPOoTqmwpB5ecNU'

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    lessons0 = types.KeyboardButton('Расписание')
    settings0 = types.KeyboardButton('Настройки')
    findname0 = types.KeyboardButton('Поиск преподавателя')
    help0 = types.KeyboardButton('Помощь')
    markup.add(lessons0)
    markup.add(settings0)
    markup.add(findname0)
    markup.add(help0)
    bot.send_message(message.chat.id, "Приветствую", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Расписание')
def lessons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    mylessons = types.KeyboardButton('Моё расписание')
    alllessons = types.KeyboardButton('Расписание курса')
    menu = types.KeyboardButton('/menu')
    markup.add(mylessons)
    markup.add(alllessons)
    markup.add(menu)
    bot.send_message(message.chat.id, 'Здесь будет расписание', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Настройки', )
def settings(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    changegr = types.KeyboardButton('Сменить группу')
    changentf = types.KeyboardButton('Сменить уведомления')
    changeweek = types.KeyboardButton('Сменить неделю на следующую')
    menu = types.KeyboardButton('/menu')
    markup.add(changegr)
    markup.add(changentf)
    markup.add(changeweek)
    markup.add(menu)
    bot.send_message(message.chat.id, 'Здесь будут настройки', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Поиск преподавателя')
def findname(message):
    markup = types.ReplyKeyboardMarkup()
    menu = types.KeyboardButton('/menu')
    markup.add(menu)
    bot.send_message(message.chat.id, 'Здесь будет поиск по именам')


@bot.message_handler(func=lambda message: message.text == 'Помощь')
def help(message):
    bot.send_message(message.chat.id,
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
bot.polling(none_stop=True)
