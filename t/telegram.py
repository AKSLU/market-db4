import telebot
import psycopg2
from datetime import datetime, timedelta

TOKEN = " "
bot = telebot.TeleBot(TOKEN)

def check_subscription(tg_login):
    try:
        print(f" Проверка подписки для @{tg_login}")
        conn = psycopg2.connect(
            dbname="base",
            user="postgres",
            password="20062007",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT is_buy, expire_date FROM subscriptions
            WHERE tg_login = %s
        """, (tg_login,))
        result = cur.fetchone()

        if result:
            is_buy, expire_date = result
            if is_buy and expire_date and datetime.now() < expire_date:
                return True
        return False

    except Exception as e:
        print(f"Ошибка в check_subscription: {e}")
        return False

    finally:
        if 'conn' in locals():
            conn.close()

def activate_subscription(tg_login):
    try:
        print(f"Активация подписки для @{tg_login}")
        conn = psycopg2.connect(
            dbname="base",
            user="postgres",
            password="20062007",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        expire = datetime.now() + timedelta(days=5)

        cur.execute("SELECT * FROM subscriptions WHERE tg_login = %s", (tg_login,))
        if cur.fetchone():
            print(" Подписка уже есть, обновляем.")
            cur.execute("""
                UPDATE subscriptions
                SET is_buy = TRUE, buy_date = NOW(), expire_date = %s
                WHERE tg_login = %s
            """, (expire, tg_login))
        else:
            print(" Добавляем новую подписку.")
            cur.execute("""
                INSERT INTO subscriptions (tg_login, is_buy, buy_date, expire_date)
                VALUES (%s, TRUE, NOW(), %s)
            """, (tg_login, expire))

        conn.commit()

    except Exception as e:
        print(f"Ошибка в activate_subscription: {e}")

    finally:
        if 'conn' in locals():
            conn.close()

@bot.message_handler(commands=['start'])
def handle_start(message):
    username = message.from_user.username
    print(f"/start от: @{username}")
    
    if not username:
        bot.send_message(message.chat.id, "Установите username в Telegram.")
        return

    try:
        if check_subscription(username):
            bot.send_message(message.chat.id, "У вас активная подписка!")
        else:
            bot.send_message(message.chat.id, " Подписка не найдена. Напишите /buy чтобы купить.")

    except Exception as e:
        bot.send_message(message.chat.id, " Ошибка при проверке подписки.")
        print(f"Ошибка в /start: {e}")

@bot.message_handler(commands=['buy'])
def handle_buy(message):
    username = message.from_user.username
    print(f"/buy от: @{username}")

    if not username:
        bot.send_message(message.chat.id, "Установите username в Telegram.")
        return

    try:
        activate_subscription(username)
        bot.send_message(message.chat.id, " Подписка успешно активирована на 5 дней!")

    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при активации подписки.")
        print(f" Ошибка в /buy: {e}")


bot.polling()



