import telebot
import datetime
import json
import time
import datetime
from threading import Thread 

# Тут хранится переменная-константа с токеном бота, чтобы нормально выгружать на GitHUB
import const_var_token

# Название json файла
file_name = "main.json"

# Количество учеников
pupils_count = 18

bot = telebot.TeleBot(const_var_token.TOKEN, threaded=True)



########################### Асинхронный цикл #####################################
# По-хорошему, эту часть кода надо бы перенести наверх, но из-за особенностей Python,
# функции которые ниже, он не видит, поэтому данная часть кода снизу
def cycle():
    action = True

    with open(file_name, "r") as readed:
        main_js = json.load(readed)
    readed.close
            
    while True:
        n_time = datetime.datetime.now()
        num_of_day = n_time.isoweekday()

        if n_time.hour == 16 and action and (num_of_day != 6 and num_of_day != 7):
            # Перезаписывает комплекс на ""
            for index in range(0, len(main_js["names"])):
                main_js["names"][index]["choose"] = ""
            change_js(main_js)

            # Рассылает напоминание всем пользователям
            for user in main_js["names"]:
                if user["id"] != 0 and user["id"]:
                    try:
                        bot.send_message(user["id"], "Список очищен, измените статус питания")
                    except:
                        print(f"Заблокировал бота - {user['id']}")

            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close
            
            #bot.send_message(message.from_user.id, "Список очищен, напоминание разослано")
            action = False
        
        elif n_time.hour != 16:
            action = True

        time.sleep(30)
        

async_cycle = Thread(target=cycle)
async_cycle.start()
##################################################################################


########################### Дополнительные функции #####################################

# Функция, возвращающаяя индекс словаря в списке "names" в settings.json
def return_index(arr, element, find):
    index = 0
    arr = arr["names"]

    for b in arr:
        if b[element] == find:
            return index
        else:
            index += 1

    return None

# Функция, сохраняющаяя красивый {filename}.json
def change_js(main_js):
    char = ",\n\t\t"
    string = f'''
{{
    "names" : 
    [\n\t\t''' 
    for index in range(0, pupils_count):
        if index == pupils_count - 1:
            char = "\n\t"

        string += f'{{"name" : "{main_js["names"][index]["name"]}"{" " * (21 - len(main_js["names"][index]["name"]))}, \
"password": {main_js["names"][index]["password"]}, "id" : {main_js["names"][index]["id"]}{" " * (12 - len(str(main_js["names"][index]["id"])))}, \
"default_ch" : "{main_js["names"][index]["default_ch"]}"{" " * (6 - len(main_js["names"][index]["default_ch"]))}, \
"choose" : "{main_js["names"][index]["choose"]}"{" " * (6 - len(main_js["names"][index]["choose"]))}}}{char}'

    string += f'''],

    "command" : {main_js["command"]}
}}
'''

    # Записывает в {filename}.json
    with open(file_name, "w") as wr:
        wr.write(string)
        wr.close()


def _set_choose(main_js, id_index, var_type, var_value):
    main_js["names"][id_index][var_type] = var_value
    change_js(main_js)

@bot.message_handler(content_types=['text', 'document', "photo"])
def get_text_messages(message):
    
    ########################### Основные функции #####################################


    # Одна из функций авторизации, она просто принимает имя и обращается к другой функции
    def get_user_name(message):
        global u_name
        u_name = message.text
        bot.send_message(message.from_user.id, "Введите ваш пароль")
        bot.register_next_step_handler(message, get_user_pwd)
    
    # Основная функция авторизации, принимает пароль и имя и сравнивает их со списком пользователей
    def get_user_pwd(message):
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close

            # Находит индекс пользователя по введённому им имени в {filename}.json
            name_index = return_index(main_js, "name", u_name)

            # Проверяет, был ли этот пользователь уже авторизован
            if return_index(main_js, "id", message.from_user.id) == None:             
                
                if message.text == str(main_js["names"][name_index]["password"]) and main_js["names"][name_index]["id"] == 0:
                    main_js["names"][name_index]["id"] = message.from_user.id
                    change_js(main_js)
                    bot.send_message(message.from_user.id, "Вы успешно авторизованы")
                
                else:
                    bot.send_message(message.from_user.id, "Неверный пароль или этот пользователь уже авторизован")
            else:
                bot.send_message(message.from_user.id, "Вы уже авторизованы")
        except:
            bot.send_message(message.from_user.id, "Такого пользователя не существует")

    # Выход из аккаунта
    def logout(message):
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close
            
            # Находит индекс пользователя по его id в {filename}.json
            id_index = return_index(main_js, "id", message.from_user.id)

            if id_index == None:
                bot.send_message(message.from_user.id, "Вы не авторизованы")           
            else:
                main_js["names"][id_index]["id"] = 0
                change_js(main_js)
                bot.send_message(message.from_user.id, "Вы вышли")
        except:
            bot.send_message(message.from_user.id, "Ошибка")
    
    
    # Функция выбора комплекса
    def choose(message):
        try:
            # Читает {filename}.json
            with open(file_name, 'r') as readed:
                main_js = json.load(readed)
            readed.close()

            # Находит индекс пользователя по его id в {filename}.json
            id_index = return_index(main_js, "id", message.from_user.id)

            # Изменяет выбранный комплекс в {filename}.json
            if id_index != None:

                if (main_js["names"][id_index]["choose"] != "" and (
                   (message.text == "1" or message.text.lower() == "Ест") or message.text == "0")):
                    
                    bot.send_message(message.from_user.id, "Выбор обновлён")

                if message.text == "1" or message.text.lower() == "ест":
                    _set_choose(main_js, id_index, "choose", "Ест")
                    bot.send_message(message.from_user.id, "Вы выбрали 1-ый комплекс")              
                
                elif message.text == "0":
                    _set_choose(main_js, id_index, "choose", "Не ест")
                    bot.send_message(message.from_user.id, "Сегодня вы не едите")

                else:
                    bot.send_message(message.from_user.id, "Такого комплекса нет")

            # Если не нашло id в {filename}.json
            elif id_index == None:
                bot.send_message(message.from_user.id, "Вы не авторизованы")
        except:
            bot.send_message(message.from_user.id, "Ошибка")

    
    # Функция установки комплекса по умолчнию
    def set_default_choose(message):
        try:
            # Читает {filename}.json
            with open(file_name, 'r') as readed:
                main_js = json.load(readed)
            readed.close()

            # Находит индекс пользователя по его id в {filename}.json
            id_index = return_index(main_js, "id", message.from_user.id)

            # Изменяет комплекс по умолчанию в {filename}.json
            if id_index != None:
                
                if message.text == "1" or message.text.lower() == "ем":
                    _set_choose(main_js, id_index, "default_ch", "Ест")                 
                    bot.send_message(message.from_user.id, "Значение по умолчанию установлено")

                
                elif message.text == "0":
                    _set_choose(main_js, id_index, "default_ch", "Не ест")                    
                    bot.send_message(message.from_user.id, "Значение по умолчанию установлено")

                else:
                    bot.send_message(message.from_user.id, "Такого комплекса нет")

            # Если не нашло id в {filename}.json
            elif id_index == None:
                bot.send_message(message.from_user.id, "Вы не авторизованы")
        except:
            bot.send_message(message.from_user.id, "Ошибка")


    # Функция установки комплекса по умолчнию админом, 1-ая часть
    def admin_set_choose_part_one(message):
        global u_name_adm
        u_name_adm = message.text

        # Читает {filename}.json
        with open(file_name, 'r') as readed:
            main_js = json.load(readed)
        readed.close()

        if return_index(main_js, "name", u_name_adm):
            bot.send_message(message.from_user.id, "Введите номер комплекса")
            bot.register_next_step_handler(message, admin_set_choose_part_two)
        else:
            bot.send_message(message.from_user.id, "Такого пользователя не существует")
    
    
    # Функция установки комплекса по умолчнию админом, 2-ая часть
    def admin_set_choose_part_two(message):
        try:
            # Читает {filename}.json
            with open(file_name, 'r') as readed:
                main_js = json.load(readed)
            readed.close()

            # Находит индекс пользователя по его id в {filename}.json
            id_index = return_index(main_js, "name", u_name_adm)

            # Изменяет комплекс по умолчанию в {filename}.json
            if id_index != None:
                
                if message.text == "1" or message.text.lower() == "ем":
                    main_js["names"][id_index]["default_ch"] = "Ест"
                    change_js(main_js)
                    
                    bot.send_message(main_js["names"][id_index]["id"], "Ваш комплекс по умолчанию был изменён администратором, теперь он 1-ый")
                    bot.send_message(message.from_user.id, "Значение по умолчанию установлено")
                    
                elif message.text == "0":
                    main_js["names"][id_index]["default_ch"] = "Не ест"
                    change_js(main_js)
                    
                    bot.send_message(main_js["names"][id_index]["id"], "Ваш комплекс по умолчанию был изменён администратором, теперь вы не едите")
                    bot.send_message(message.from_user.id, "Значение по умолчанию установлено")

                else:
                    bot.send_message(message.from_user.id, "Такого комплекса нет")

            # Если не нашло id в {filename}.json
            elif id_index == None:
                bot.send_message(message.from_user.id, "Вы не авторизованы")
        except:
            bot.send_message(message.from_user.id, "Ошибка")
 


########################### Основные команды #####################################
    

    # Команда приветствия
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Этот бот спрашивает номер комплекса в столовой. Для авторизации введите /login.")
        bot.send_message(message.from_user.id, "Чтобы узнать меню на сегодня выберете или напишите /menu.")
        bot.send_message(message.from_user.id, "Для выбора комплекса напишите /choose")
    
    # Команда авторизации, ссылается к функцияс выше
    elif message.text == '/login':
        try:
            bot.send_message(message.from_user.id, "Введите ваше имя")
            bot.register_next_step_handler(message, get_user_name)
        except:
            bot.send_message(message.from_user.id, "Ошибка")
    
    # Команда выхода из учётной записи, ссылается к функцияс выше
    elif message.text == "/logout":
        try:
            logout(message)
        except:
            bot.send_message(message.from_user.id, "Ошибка")
    
    # Команда просмотра меню
    elif message.text == "/menu":
        try:
            try:
                img = open(f"photos/{datetime.date.today()}.png", 'rb')
                bot.send_photo(message.from_user.id, img)
                img.close()
            
            # Отправляет деда с дулями 
            except:
                img = open(f"photos/default.jpg", 'rb')
                bot.send_photo(message.from_user.id, img)
                img.close()

                bot.send_message(message.from_user.id, "Меню ещё нет")
        except:
            bot.send_message(message.from_user.id, "Ошибка")

    # Команда выбора комплекса, ссылается на функции выше
    elif message.text == "/choose":
        try:
            bot.send_message(message.from_user.id, "Введите номер комплекса, если вы не хотите сегодня есть, то напишите 0")
            bot.register_next_step_handler(message, choose)
        except:
            bot.send_message(message.from_user.id, "Ошибка")

    # Установка комплекса по умолчанию
    elif message.text == "/default_choose":
        try:
            bot.send_message(message.from_user.id, "Введите номер комплекса по умолчанию")
            bot.register_next_step_handler(message, set_default_choose)
        except:
            bot.send_message(message.from_user.id, "Ошибка")
    

########################### Админские команды #####################################


    # Команда получения доступа к отправке меню, удалению списка, просмотру списка
    elif message.text == "/add_to_comm":
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close

            if message.from_user.id in main_js["command"]:
                bot.send_message(message.from_user.id, "Вы уже авторизованы")
            
            else:
                main_js["command"].append(message.from_user.id)
                change_js(main_js)
                bot.send_message(message.from_user.id, "Вы успешно авторизованы")
        except:
            bot.send_message(message.from_user.id, "Ошибка")

    # Команда загрузки фото от людей с нужным уровнем доступа
    elif message.photo:
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close
            
            # Скачивает и рассылает фотографию с меню 
            if message.from_user.id in main_js["command"]:
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src = f"photos/{datetime.date.today()}.png"
                
                # Сохраняет фотографию с меню
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                new_file.close()

                # Очищает список и сохраняет
                for index in range(0, len(main_js["names"])):
                    main_js["names"][index]["choose"] = ""                
                change_js(main_js)

                # Рассылает фотографию всем пользователям
                for user in main_js["names"]:
                    if user["id"] != 0 and user["id"] != message.from_user.id:
                        try:
                            bot.send_photo(user["id"], downloaded_file)
                        except:
                            print(user["id"])
                
                bot.send_message(message.from_user.id, f"Меню на {datetime.date.today()} добавлено")

            else:
                bot.send_message(message.from_user.id, "У вас недостаточно прав")
        except Exception as e:
            print(e)
            bot.send_message(message.from_user.id, "Ошибка")

    #elif message.text == "/"

    # Команда вывода списка
    elif message.text == "/readchoose":
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close
            
            # Считет количество комплексов и выводит в виде таблицы
            if message.from_user.id in main_js["command"]:
                bad_names = "Никита, Илья, Фома, Савва, Лука, Кузьма, Фока, Зосима, Добрыня, Вавила, Вакула, Даниила, Гавриила, Данила, Гаврила"
                list_of_menu = "```\n"
                temp_ch = ""
                one = 0

                for index in range(0, len(main_js["names"])):          

                    if main_js["names"][index]["choose"] == "":
                        if main_js["names"][index]["default_ch"] == "Не ест":
                            temp_ch = f'''{main_js["names"][index]["default_ch"]} (A)'''
                        else:                   
                            temp_ch = f'''{main_js["names"][index]["default_ch"]}    (A)'''                       
                    else:
                        temp_ch = main_js["names"][index]["choose"]
                 
                    if main_js["names"][index]["id"] == 0:
                        # Проверяет мужское ли имя (примерно)                     
                        if (main_js["names"][index]["name"])[-1] in "бвгджзйклмнпрстфхцчшщ" or (main_js["names"][index]["name"].split(" "))[1] in bad_names.split(", "):
                            temp_ch = "Не вошёл"
                        else:
                            temp_ch = "Не вошла"

                    if temp_ch == "Ест" or temp_ch == "Ест    (A)":
                        one += 1
                
                    list_of_menu += f'''{main_js["names"][index]["name"]}{" " * (21 - len(main_js["names"][index]["name"]))}: {temp_ch}\n'''

                list_of_menu += f"\nЕст - {one} шт```"
                    
                try:
                    bot.send_message(message.from_user.id, list_of_menu, parse_mode="Markdown")
                except:
                    bot.send_message(message.from_user.id, "Пока пусто")
            
            else:
                bot.send_message(message.from_user.id, "У вас недостаточно прав")
        except:
            bot.send_message(message.from_user.id, "Ошибка")

    # Команда установки комплекса по умолчанию для других участников
    elif message.text == "/set":
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close
            
            # Перезаписывает комплекс на ""
            if message.from_user.id in main_js["command"]:
                bot.send_message(message.from_user.id, "Введите имя пользователя")
                bot.register_next_step_handler(message, admin_set_choose_part_one)
            else:
                bot.send_message(message.from_user.id, "У вас недостаточно прав")
        except:
            bot.send_message(message.from_user.id, "Ошибка")

    elif message.text == "/notification":
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close
            
            if message.from_user.id in main_js["command"]:
                # Перезаписывает комплекс на ""
                for index in range(0, len(main_js["names"])):
                    main_js["names"][index]["choose"] = ""
                change_js(main_js)

                # Рассылает напоминание всем пользователям
                for user in main_js["names"]:
                    if user["id"] != 0 and user["id"] != message.from_user.id:
                        try:
                            bot.send_message(user["id"], "Список очищен, измените статус питания")
                        except:
                            print(f"Заблокировал бота - {user['id']}")
                
                bot.send_message(message.from_user.id, "Список очищен, напоминание разослано")
            else:
                bot.send_message(message.from_user.id, "У вас недостаточно прав")
        except:
            bot.send_message(message.from_user.id, "Ошибка")


    # Команда очистки комплекса
    elif message.text == "/remove":
        try:
            # Читает {filename}.json
            with open(file_name, "r") as readed:
                main_js = json.load(readed)
            readed.close
            
            # Перезаписывает комплекс на ""
            if message.from_user.id in main_js["command"]:
                for index in range(0, len(main_js["names"])):
                    main_js["names"][index]["choose"] = ""
                
                change_js(main_js)
                bot.send_message(message.from_user.id, "Список очищен")
            
            else:
                bot.send_message(message.from_user.id, "У вас недостаточно прав")
        except:
            bot.send_message(message.from_user.id, "Ошибка")



########################### Прочие команды #####################################

    elif message.text == "/code":
        bot.send_message(message.from_user.id, "Исходники - https://github.com/Apsapeh/Food_Bot")

    # Помощь по командам
    elif message.text == "/help":
        msg = '''Все команды:\n
    /login - Авторизоваться
    /logout - Выйти
    /menu - Посмотреть меню
    /choose - Выбрать комплекс
    /default_choose - установить комплекс по умолчанию
    /code - Ссылка на исходники\n

Комманды для тех, у кого есть нужные права доступа:\n
    /readchoose - Прочитать список
    /remove - Очистить список
    /set - Поменять комплекс по умолчанию\n'''

        bot.send_message(message.from_user.id, msg)

    # Если пользователь не ввёл команду
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю, напиши /help или посмотри команды в меню")



# Запуск цикла бота
while True:
    try:
        bot.infinity_polling(0)
    except Exception as e:
        pass
