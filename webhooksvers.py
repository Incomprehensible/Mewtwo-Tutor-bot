# -*- coding: UTF-8 -*-
#!/usr/bin/python3

import telebot
import json
import cherrypy

import config
from data_base import modules, file

WEBHOOK_HOST = '192.168..'
WEBHOOK_PORT = 443  # 443, 80, 88 или 8443
WEBHOOK_LISTEN = '192.168..'  # На некоторых серверах указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (config.token)

bot = telebot.TeleBot(config.token)

class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            # Эта функция обеспечивает проверку входящего сообщения
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

def dict_to_json(my_dict):
    into_json = json.dumps(my_dict)
    return into_json

def json_to_file(my_dict, filename):
    with open(filename, 'w') as my_json:
        json.dump(my_dict, my_json)

def load_json(file):
    with open(file, 'r') as my_json:
        loaded = json.load(my_json)
    return loaded

def access_json_module():
    global file
    data_base = load_json(file)
    module = list(data_base.keys())[0]
    minm = data_base[module]['Priority']
    for key in data_base:
        if data_base[key]['Priority'] < minm:
            minm = data_base[key]['Priority']
            module = key
    data_base[module]['Priority'] += 1
    json_to_file(data_base, file)
    return module

def access_json_data(module, key):
    global file
    data_base = load_json(file)
    data_block = data_base[module][key]
    choice = list(data_block.keys())[0]
    minm = data_block[choice]['priority']
    for book in data_block:
        if data_block[book]['priority'] < minm:
            minm = data_block[book]['priority']
            choice = book
    data_block[choice]['priority'] += 1
    json_to_file(data_base, file)
    return choice, data_block[choice]['link']


class Day:
    module = 'Fuck'
    book = ['fuck', 'fuck']
    course = ['fuck', 'fuck']
    video = ['fuck', 'fuck']

    def __init__(self):
        self.module = access_json_module()

    def fill_form(self):
        self.book = access_json_data(self.module, 'Books')
        self.course = access_json_data(self.module, 'Courses')
        self.video = access_json_data(self.module, 'Videos')

    def display_form(self, list):
        list.append("Today module: " + self.module + "\n")
        list.append("Book: " + self.book[0] + " -> link: " + self.book[1] + "\n")
        list.append("Course: " + self.course[0] + " -> link: " + self.course[1] + "\n")
        list.append("Video: " + self.video[0] + " -> link: " + self.video[1] + "\n")
        print("Uchis' blyat!!!\n\n")

def make_timetbl():
    block1 = Day()
    block2 = Day()
    block1.fill_form()
    block2.fill_form()
    list = []
    block1.display_form(list)
    list.append("\n\n")
    block2.display_form(list)
    s = ' '
    return s.join(list)

@bot.message_handler(content_types=['text'])
def tutor_awaken(message):
    global file
    if message.text == "Change json file":
        bot.send_message(message.chat.id, "Type name for the file: ")
        file = input("Type name for the file: ")
    elif message.text == "Kek":
        result = make_timetbl()
        bot.send_message(message.from_user.id, result)
    elif message.text == "Update base":
        try:
            json_to_file(modules, file)
        except FILEFAULT:
            bot.send_message(message.from_user.id, "Fault: file not found")
    else:
        bot.send_message(message.from_user.id, "See ya studying hard")


cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))
    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
