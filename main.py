from pyrogram import Client, filters, enums
import requests
import datetime
import time as tm #this is for some errors that time variable make you can delete 'as tm' section and see the error
import datetool 
from datetime import timedelta
import matplotlib.pyplot as plt
import os 
import json
import pandas as pd
import random
import csv

app = Client('Self client bot')


def ktc(kelvin):
    return kelvin - 273.15

def select_word(language : str):
    words = []
    with open(f'{language}-words.txt', encoding = 'utf8') as file:
        for word in file.readlines():
            words.append(word.strip())

    return random.choice(words)

def underline(word):
    word_list = list(word)
    for i in range(0 , (len(word) - len(word) // 3)):
        random_number = random.randrange(0 , len(word))
        word_list[random_number] = '-'

    return ' '.join(word_list)

used_words = []
Hangman_game = {}

names = pd.read_csv('persian-names.csv')

@app.on_message(filters.outgoing & filters.text)
async def message(_, message):
    global used_words, names
    start_time = tm.time()
    chat_id = message.chat.id
    message_id = message.id
    text = message.text
    try:
        listed_text = text.split(' ')
    except AttributeError: pass

    if text == '!info':
        chat = await app.get_chat(chat_id)

        if chat.type == enums.ChatType.PRIVATE:
            await app.edit_message_text(chat_id, message_id, f'نام کاربر: {chat.first_name}\nآیدی: {chat.username}\nآیدی عددی کاربر: {chat.id}')

        if chat.type == enums.ChatType.GROUP or chat.type == enums.ChatType.SUPERGROUP:
            await app.edit_message_text(chat_id, message_id, f'نام گروه: {chat.title}\nآیدی عددی گروه: {chat.id}\nتعداد اعضا: {chat.members_count}\nلینک گروه: {chat.invite_link if not chat.invite_link == None else "لینک دعوت وجود ندارد"}')

    elif listed_text[0] == '!weather':
        city = listed_text[1:]
        response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid=5d4124e4d62fdb365f2cd6b2fcf911c3')

        resp = response.json()

        for i in range(0, len(resp) + 1):
            if resp[0]['country'] == 'IR':
                lat = resp[0]['lat']
                lon = resp[0]['lon']
                break

        response = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=daily&appid=5d4124e4d62fdb365f2cd6b2fcf911c3')
        resp = response.json()

        sunrise = tm.strftime('%H:%M:%S', tm.gmtime(resp['current']['sunrise'])) + ' ☀️'
        sunset = tm.strftime('%H:%M:%S', tm.gmtime(resp['current']['sunset']))+ ' 🌖'
        tempeture = resp['current']['temp']
        tempeture = int(ktc(tempeture))
        cloud = str(resp['current']['clouds']) + '% ☁️'
        wind_speed = str(resp['current']['wind_speed']) + ' M/S'
        sky_status = resp['current']['weather'][0]['main']
        if sky_status == 'Clouds': sky_status = 'ابری⛅️'
        elif sky_status == 'Clear': sky_status = 'معمولی🌞'
        elif sky_status == 'Rain': sky_status = 'بارانی☔️'
        elif sky_status == 'Snow': sky_status = 'برفی❄️'
        data = f'موقعیت جغرافیایی: {lat}, {lon}🧭\nطلوع خورشید: {sunrise}\nغروب خوشید: {sunset}\nدما: {tempeture} C° 🌡  \nابر: {cloud}\nسرعت باد: {wind_speed}\nوضعیت هوا: {sky_status}'

        await app.edit_message_text(chat_id, message_id, data)

    elif text == '!time' or text == '!date':
        response = requests.get('https://api.keybit.ir/time/')

        resp = response.json()

        time = resp['time24']['full']['en']
        day = resp['date']['day']['name']
        month = resp['date']['month']['name']
        year = resp['date']['year']['number']['en']
        days_left = resp['date']['year']['left']['days']['en']
        year_animal = resp['date']['year']['animal']
        leapyear = resp['date']['year']['leapyear']

        data = f'ساعت: {time} ⏰\n{day} {month} {year} 📅\n امسال {leapyear} است.\n\nروز های باقیمانده تا پایان سال: {days_left} ⏲\nحیوان سال: {year_animal}'

        await app.edit_message_text(chat_id, message_id, data)

    elif listed_text[0] == '!calendar':
        if listed_text[1:] != []: format = int(listed_text[1])
        else: format = 1

        await app.edit_message_text(chat_id, message_id, f'<pre>{datetool.calendar(format)}</pre language="python">', parse_mode=enums.ParseMode.HTML)

    elif listed_text[0] == '!price':
        if listed_text[1] == 'اتریوم':
            response = requests.get('https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=30&interval=daily')

            resp = response.json()

            days = []
            today = datetime.datetime.today()
            for i in range(0, 31):
                a = today - timedelta(days=i)
                a = a.strftime('%m/%d')
                days.append(a)

            days.reverse()

            prices = [price for price in resp['prices']]

            price_fin = []
            for i in prices:
                price_fin.append(i[1])

            plt.figure(facecolor='#151825', edgecolor = '#000000')
            ax = plt.axes()
            ax.set_facecolor("#151825")
            plt.ylabel('USD')
            plt.xlabel('Day')

            response = requests.get('https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=1&interval=daily')

            resp = response.json()
            data = 'price: $%.3f \nmarket cap: $%i \ntotal volume: $%i' % (resp['prices'][1][1], resp['market_caps'][1][1], resp['total_volumes'][1][1])


            plt.plot(days, price_fin, color = '#2962FF')
            plt.grid(color = '#212530')
            plt.tick_params(axis='x', which='major', labelsize=6)
            plt.xticks(rotation=45)
            plt.savefig('%s.png' % chat_id, dpi=300)
            await app.send_photo(chat_id, '%s.png' % chat_id, data, reply_to_message_id=message_id)
            os.remove('%s.png' % chat_id)
        
        elif listed_text[1] == 'بیت' and listed_text[2] == 'کوین':
            response = requests.get('https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30&interval=daily')

            resp = response.json()

            days = []
            today = datetime.datetime.today()
            for i in range(0, 31):
                a = today - timedelta(days=i)
                a = a.strftime('%m/%d')
                days.append(a)

            days.reverse()

            prices = [price for price in resp['prices']]

            price_fin = []
            for i in prices:
                price_fin.append(i[1])

            plt.figure(facecolor='#151825', edgecolor = '#000000')
            ax = plt.axes()
            ax.set_facecolor("#151825")
            plt.ylabel('USD')
            plt.xlabel('Day')

            response = requests.get('https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1&interval=daily')

            resp = response.json()
            data = 'price: $%.3f \nmarket cap: $%i \ntotal volume: $%i' % (resp['prices'][1][1], resp['market_caps'][1][1], resp['total_volumes'][1][1])


            plt.plot(days, price_fin, color = '#2962FF')
            plt.grid(color = '#212530')
            plt.tick_params(axis='x', which='major', labelsize=6)
            plt.xticks(rotation=45)
            plt.savefig('%s.png' % chat_id, dpi=300)
            await app.send_photo(chat_id, '%s.png' % chat_id, data, reply_to_message_id=message_id)
            os.remove('%s.png' % chat_id)

        elif listed_text[1] == 'دوج' and listed_text[2] == 'کوین':
            response = requests.get('https://api.coingecko.com/api/v3/coins/dogecoin/market_chart?vs_currency=usd&days=30&interval=daily')

            resp = response.json()

            days = []
            today = datetime.datetime.today()
            for i in range(0, 31):
                a = today - timedelta(days=i)
                a = a.strftime('%m/%d')
                days.append(a)

            days.reverse()

            prices = [price for price in resp['prices']]

            price_fin = []
            for i in prices:
                price_fin.append(i[1])

            plt.figure(facecolor='#151825', edgecolor = '#000000')
            ax = plt.axes()
            ax.set_facecolor("#151825")
            plt.ylabel('USD')
            plt.xlabel('Day')

            response = requests.get('https://api.coingecko.com/api/v3/coins/dogecoin/market_chart?vs_currency=usd&days=1&interval=daily')

            resp = response.json()
            data = 'price: $%.3f \nmarket cap: $%i \ntotal volume: $%i' % (resp['prices'][1][1], resp['market_caps'][1][1], resp['total_volumes'][1][1])


            plt.plot(days, price_fin, color = '#2962FF')
            plt.grid(color = '#212530')
            plt.tick_params(axis='x', which='major', labelsize=6)
            plt.xticks(rotation=45)
            plt.savefig('%s.png' % chat_id, dpi=300)
            await app.send_photo(chat_id, '%s.png' % chat_id, data, reply_to_message_id=message_id)
            os.remove('%s.png' % chat_id)

        elif listed_text[1] == 'سولانا':
            response = requests.get('https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=30&interval=daily')

            resp = response.json()

            days = []
            today = datetime.datetime.today()
            for i in range(0, 31):
                a = today - timedelta(days=i)
                a = a.strftime('%m/%d')
                days.append(a)

            days.reverse()

            prices = [price for price in resp['prices']]

            price_fin = []
            for i in prices:
                price_fin.append(i[1])

            plt.figure(facecolor='#151825', edgecolor = '#000000')
            ax = plt.axes()
            ax.set_facecolor("#151825")
            plt.ylabel('USD')
            plt.xlabel('Day')

            response = requests.get('https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=1&interval=daily')

            resp = response.json()
            data = 'price: $%.3f \nmarket cap: $%i \ntotal volume: $%i' % (resp['prices'][1][1], resp['market_caps'][1][1], resp['total_volumes'][1][1])


            plt.plot(days, price_fin, color = '#2962FF')
            plt.grid(color = '#212530')
            plt.tick_params(axis='x', which='major', labelsize=6)
            plt.xticks(rotation=45)
            plt.savefig('%s.png' % chat_id, dpi=300)
            await app.send_photo(chat_id, '%s.png' % chat_id, data, reply_to_message_id=message_id)
            os.remove('%s.png' % chat_id)

    elif text == '!joke':
        joke = requests.get("https://api.codebazan.ir/jok/")

        await app.edit_message_text(chat_id, message_id, joke.text)

    elif text == '!fal':
        all = requests.get("https://one-api.ir/hafez/?token=471350:61c3153c30ea59.05127527")

        all = json.loads(all.text)

        await app.edit_message_text(chat_id, message_id,"%s \n\nمعنی:\n%s" % (all['result']['RHYME'], all['result']['MEANING']))

    elif text == '!test':
        await app.edit_message_text(chat_id, message_id,  "I'm here")

    elif text == '!ping':
        await app.edit_message_text(chat_id, message_id, '%.14f' % float((tm.time() - start_time)))
    
    elif listed_text[0] == '!spam':
        await app.delete_messages(chat_id, message_id)

        for counter, i in enumerate(range(int(listed_text[1]))):
            await app.send_message(chat_id, f'{" ".join(listed_text[2:])}')
            if counter % 10 == 0:
                tm.sleep(1)

    elif text == '!download-profiles':
        counter = 0
        async for photo in app.get_chat_photos(chat_id):
            await app.download_media(photo.file_id, f'downloads/{counter}.jpg')
            await app.send_photo(chat_id, f'downloads/{counter}.jpg')
            os.remove(f'downloads/{counter}.jpg')
            counter += 1

    elif listed_text[0] == '!heart-wave':
        hearts = ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎']
        if len(listed_text) == 2: repeats = int(listed_text[1])
        else: repeats = 10
        for counter, i in enumerate(range(repeats)):
            await app.edit_message_text(chat_id, message_id, ''.join(hearts))
            heart = hearts[0]
            hearts.pop(0)
            hearts.append(heart)
            tm.sleep(0.3)
            if counter % 15 == 0: tm.sleep(1.5)
        
        await app.edit_message_text(chat_id, message_id, '🫀')

    elif text == '!dialogue':
        response = requests.get('https://one-api.ir/sokhan/?token=371624:64c69cdb1bc05&action=random')
        resp = json.loads(response.text)

        if resp['status'] == 200 and response.status_code == 200:
            await app.edit_message_text(chat_id, message_id, f"{resp['result']['author']}:\n{resp['result']['text']}")

        elif response.status_code != 200:
            await app.edit_message_text(chat_id, message_id, resp.status_code)
        
        elif resp['status'] != 200:
            await app.edit_message_text(chat_id, message_id, resp['status'])

    elif text == '!general-information':
        response = requests.get('https://one-api.ir/danestani/?token=371624:64c69cdb1bc05')
        resp = json.loads(response.text)

        if resp['status'] == 200 and response.status_code == 200:
            await app.edit_message_text(chat_id, message_id, f"{resp['result']['Content']}")

        elif response.status_code != 200:
            await app.edit_message_text(chat_id, message_id, resp.status_code)
        
        elif resp['status'] != 200:
            await app.edit_message_text(chat_id, message_id, resp['status'])

    elif listed_text[0] == '!last-news':
        #available news agencies: irinn, tasnim, mehr, irna, mizan, varzesh3(if you want to change the news agency you have to change all codes bcs the json of the requests are different)
        response = requests.get(f'https://one-api.ir/rss/?token=371624:64c69cdb1bc05&action=tasnim')
        resp = json.loads(response.text)

        page = 0

        if len(listed_text) == 2:
            if int(listed_text[1]) <= 9:
                page = int(listed_text[1])

                if resp['status'] == 200 and response.status_code == 200:
                    resp = resp['result']

                    content = ''

                    for i in range(page, page + 3):
                        content += f"\n\n **[{resp['item'][i]['title']}]({resp['item'][i]['link']})**\n{resp['item'][i]['description']}"

                    await app.send_message(chat_id, f"[{resp['title']}]({resp['link']}){content}", reply_to_message_id = message_id, disable_web_page_preview = True)

                elif response.status_code != 200:
                    await app.edit_message_text(chat_id, message_id, resp.status_code)
                
                elif resp['status'] != 200:
                    await app.edit_message_text(chat_id, message_id, resp['status'])


            else:
                await app.send_message(chat_id, 'بیشتر از 9 نمیتوانید وارد کنید.')

    elif text == '!start-names-game':
        if used_words == []:
            await app.send_message(chat_id, 'بازی در پیوی شما شروع شد. برای اتمام بازی از دستور !stop-names-game استفاده کنید.', reply_to_message_id = message_id)
            
            used_words.append(message.from_user.id)
            used_words.append(names['name'][random.randrange(len(names))])
            await app.send_message(message.from_user.id, used_words[-1])

        else:
            await app.send_message(chat_id, 'شخص دیگری در حال بازی کردن است لطفا منتظر بمانید', reply_to_message_id = message_id)

    elif listed_text[0] == '!start-hangman-game':
        if chat_id in Hangman_game.keys():
            await app.send_message(chat_id, 'در این گروه در حال حاضر یک بازی در حال اجرا است.', reply_to_message_id = message_id)

        else:
            if listed_text[1] == 'english':
                guess_word = select_word('english')
                final_word = underline(guess_word)
                await app.send_message(chat_id, final_word, reply_to_message_id = message_id)
                Hangman_game[chat_id] = guess_word


            elif listed_text[1] == 'persian':
                guess_word = select_word('persian')
                final_word = underline(guess_word)
                await app.send_message(chat_id, final_word, reply_to_message_id = message_id)
                Hangman_game[chat_id] = guess_word

    elif chat_id in Hangman_game.keys():
        if text == Hangman_game[chat_id]:
            await app.send_message(chat_id, f'آفرین درست بود.\n کلمه درست {Hangman_game[chat_id]}')
            del Hangman_game[chat_id]

        if text == '!regenerate':
            final_word = underline(Hangman_game[chat_id])
            await app.send_message(chat_id, final_word, reply_to_message_id = message_id)


@app.on_message(filters.private & filters.text)
async def private_messages(_, message):
    global used_words
    chat_id = message.chat.id
    message_id = message.id
    text = message.text

    if used_words != []:
        if chat_id == used_words[0]:
            if any(names['name'] == text) and not text in used_words and text[0] == used_words[-1][-1]:

                used_words.append(text)
                word = text

                while word in used_words:
                    word = names['name'][random.randrange(len(names))]
                    if word[0] == text[-1]:
                        used_words.append(word)
                        break
                    else: word = text

                await app.send_message(chat_id, word, reply_to_message_id = message_id)
            
            else: 
                await app.send_message(chat_id, 'شما باختیددددد', reply_to_message_id = message_id)
                used_words = []

@app.on_message(filters.group & filters.text)
async def group(_, message):
    global used_words, names, Hangman_game
    start_time = tm.time()
    chat_id = message.chat.id
    message_id = message.id
    text = message.text
    try:
        listed_text = text.split(' ')
    except AttributeError: pass

    if text == '!start-names-game':
        if used_words == []:
            await app.send_message(chat_id, 'بازی در پیوی شما شروع شد. برای اتمام بازی از دستور !stop-names-game استفاده کنید.', reply_to_message_id = message_id)
            
            used_words.append(message.from_user.id)
            used_words.append(names['name'][random.randrange(len(names))])
            await app.send_message(message.from_user.id, used_words[-1])

        else:
            await app.send_message(chat_id, 'شخص دیگری در حال بازی کردن است لطفا منتظر بمانید', reply_to_message_id = message_id)
 
    elif listed_text[0] == '!add_new_name':
        with open('persian-names.csv', 'a', encoding = 'utf8') as file:
            if not any(names['name'] == ''.join(listed_text[1:])):
                file.write(f"{len(names)},{''.join(listed_text[1:])}\n")
                file.close()   
                await app.send_message(chat_id, 'اسم مورد نظر با موفقیت به دیتابیس اضافه شد.', reply_to_message_id = message_id)
            
            else:
                await app.send_message(chat_id, 'اسم مورد نظر قبلا در دیتابیس وجود داشت.', reply_to_message_id = message_id)

        names = pd.read_csv('persian-names.csv')

    elif listed_text[0] == '!start-hangman-game':
        if chat_id in Hangman_game.keys():
            await app.send_message(chat_id, 'در این گروه در حال حاضر یک بازی در حال اجرا است.', reply_to_message_id = message_id)

        else:
            if listed_text[1] == 'english':
                guess_word = select_word('english')
                final_word = underline(guess_word)
                await app.send_message(chat_id, final_word, reply_to_message_id = message_id)
                Hangman_game[chat_id] = guess_word


            elif listed_text[1] == 'persian':
                guess_word = select_word('persian')
                final_word = underline(guess_word)
                await app.send_message(chat_id, final_word, reply_to_message_id = message_id)
                Hangman_game[chat_id] = guess_word

    elif chat_id in Hangman_game.keys():
        if text == Hangman_game[chat_id]:
            await app.send_message(chat_id, f'آفرین درست بود.\n کلمه درست {Hangman_game[chat_id]}')
            del Hangman_game[chat_id]

print('Bot is starting')
app.run()