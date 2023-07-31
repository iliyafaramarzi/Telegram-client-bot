from pyrogram import Client, filters, enums
import requests
import datetime
import time as tm #this is for some errors that time variable make you can delete 'as tm' section and see the error
import datetool 
from datetime import timedelta
import matplotlib.pyplot as plt
import os 
import json

app = Client('Self client bot')


def ktc(kelvin):
    return kelvin - 273.15

@app.on_message(filters.outgoing & filters.text)
async def message(_, message):
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
        response = requests.get('https://one-api.ir/sokhan/?token=YOUR_TOKEN')
        resp = json.loads(response.text)

        if resp['status'] == 200 and response.status_code == 200:
            await app.edit_message_text(chat_id, message_id, f"{resp['result']['author']}:\n{resp['result']['text']}")

        elif response.status_code != 200:
            await app.edit_message_text(chat_id, message_id, resp.status_code)
        
        elif resp['status'] != 200:
            await app.edit_message_text(chat_id, message_id, resp['status'])

    elif text == '!general-information':
        response = requests.get('https://one-api.ir/danestani/?token=YOUR_TOKEN')
        resp = json.loads(response.text)

        if resp['status'] == 200 and response.status_code == 200:
            await app.edit_message_text(chat_id, message_id, f"{resp['result']['Content']}")

        elif response.status_code != 200:
            await app.edit_message_text(chat_id, message_id, resp.status_code)
        
        elif resp['status'] != 200:
            await app.edit_message_text(chat_id, message_id, resp['status'])

    # elif listed_text[0] == '!last-news':
        # response = requests.get('https://one-api.ir/rss/?token=YOUR_TOKEN&action=tasnim')
        # resp = json.loads(response.text)

        # if resp['status'] == 200 and response.status_code == 200:
        #     print(resp)

        #     img_data = requests.get(resp['image']['url']).content
        #     with open('downloads/image_name.png', 'wb') as handler:
        #         handler.write(img_data)

        #     # 

        #     content = ''

        #     for i in range(3):
        #         content += f"\n\n **[{resp['item'][i]['title']}]({resp['item'][i]['link']})**\n{resp['item'][i]['description']}"


        #     await app.send_photo(chat_id, 'downloads/image_name.png', f"[{resp['title']}]({resp['link']}){content}", reply_to_message_id = message_id)

        # elif response.status_code != 200:
        #     await app.edit_message_text(chat_id, message_id, resp.status_code)
        
        # elif resp['status'] != 200:
        #     await app.edit_message_text(chat_id, message_id, resp['status'])

    
print('Bot is starting')
app.run()