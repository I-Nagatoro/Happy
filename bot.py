import telebot
from telebot import types
import mysql.connector
from config import bot_token


host='localhost',
user='u2563829_root',
password='password123',
database='u2563829_bot_users'

TOKEN='7040842460:AAEVVtwpVDmuP8cXoMBI9-wcRPaXifJ4ag8'
bot = telebot.TeleBot(TOKEN)
bot_thread = None

chat_id = None

@bot.message_handler(commands=['start'])
def start(message):
    global chat_id
    chat_id=message.chat.id
    bot.send_message(message.chat.id, 'Кур-кур привет!')
    send_contact_request(message)

def send_contact_request(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(reg_button)
    nomer = bot.send_message(message.chat.id, 'Оставьте Ваш контактный номер для верификации.', reply_markup=keyboard)
    bot.register_next_step_handler(nomer, check_contact)

def check_contact(message):
    if message.content_type == 'contact':
        save(message)
    else:
        send_contact_request(message)

def save(message):
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    user_name = message.from_user.username
    if phone_number[0]=="+":
        phone_number[1:]
        print(phone_number)
    reg=check_phone_number(phone_number)
    connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
    if (connection.is_connected()) and (reg):
                cursor = connection.cursor()
                sql = "INSERT INTO users (id, name, phone_number) VALUES (%s, %s, %s)"
                values = (user_id, user_name, phone_number)
                cursor.execute(sql, values)
                connection.commit()
                cursor.close()
                connection.close()
                bot.send_message(message.chat.id, 'Спасибо. Данные обновлены.', reply_markup=types.ReplyKeyboardRemove())
    else:
                 bot.send_message(message.chat.id, 'Вы успешно авторизовались.')
        
    send_menu(message)    

def check_phone_number(phone_number):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='vertrigo',
            database='delivery'
        )
        cursor = connection.cursor()

        sql = "SELECT * FROM users WHERE phone_number = %s"
        cursor.execute(sql, (phone_number,))

        db_exists = bool(cursor.fetchone())
        cursor.close()
        connection.close()

        if db_exists:
            return True
        else:
            return False
    except mysql.connector.Error as error:
        bot.send_message('Ошибка при работе с базой данных: {}'.format(error))
    
def send_menu(message):
    markup = types.InlineKeyboardMarkup()
    web_info = types.WebAppInfo('https://happy-chicken.ru/menu')
    button1 = types.InlineKeyboardButton("Заказать", web_app=web_info)
    markup.add(button1)
    bot.send_message(message.chat.id, "Вот наше меню", reply_markup=markup)
    

bot.polling()