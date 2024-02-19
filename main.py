import telebot

# Указываем токен вашего бота, который вы получили у BotFather
TOKEN = '6903824564:AAHdkswkz44FizTwrcRcz1zKyt1W_VC5BL8'

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Приветствую")

# Запускаем бота
bot.polling()