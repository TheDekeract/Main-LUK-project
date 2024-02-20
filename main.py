import telebot
from telebot import types

# Указываем токен вашего бота, который вы получили у BotFather
TOKEN = '6903824564:AAHdkswkz44FizTwrcRcz1zKyt1W_VC5BL8'

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Приветствую")
    markup = types.ReplyKeyboardMarkup()
    lessons = types.KeyboardButton('Расписание')
    settings = types.KeyboardButton('Настройки')
    findname = types.KeyboardButton('Поиск преподавателя')
    help = types.KeyboardButton('Помощь')
    markup.add(lessons)
    markup.add(settings)
    markup.add(findname)
    markup.add(help)
@bot.message_handler(commands=['lessons'])
def lessons(message):
    bot.send_message(message.chat.id, 'Здесь будет расписание')

@bot.message_handler(commands=['settings'])
def settings(message):
    bot.send_message(message.chat.id, 'Здесь будут настройки')

@bot.message_handler(commands=['findname'])
def findname(message):
    bot.send_message(message.chat.id, 'Здесь будет поиск по именам')
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                       '''  Справка для бота.
Бот предоставляет услуги по уведомлению расписаний в беседах и личных сообщениях.
В разделе \"Расписание\" можно найти кнопки, предоставляющие \"Ваше расписание\" и \"Общее расписание колледжа\".
\"Ваше расписание\" является расписанием для вами выбранной группы.
Кнопка \"Преподаватель\" позволяет найти преподавателя в расписании по ФИО.
В разделе \"Настройки\" присутствуют кнопки, изменяющие выбранную группу, изменяющие частоту уведомления, а также обновление недели общего расписания (по возможности).
Обновление недели может произойти только тогда, когда в бота были добавлена следущая неделя, а воскресенье еще не наступило.
В воскресенье неделя сменяется самостоятельно и для всех пользователей.
Удачи в обучении. Cпасибо что пользуйтесь нашим ботом!''')

# Запускаем бота
bot.polling(none_stop = True)

