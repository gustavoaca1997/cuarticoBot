import sys
import os
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import pave_event_space, per_chat_id, create_open, include_callback_query_chat_id
import requests

from pprint import pprint

from Comprobante import Comprobante

# Token para el cuartico
TOKEN_CUARTICO = os.environ.get('TOKEN_CUARTICO')
API = 'localhost:8000/'

class ChatSesion(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ChatSesion, self).__init__(*args, **kwargs)

    # Manejador de mensajes
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        username = msg['chat']['username']

        if chat_type != 'private':
            return

        # Si es un comprobante
        if content_type in ['photo']:
            api_endpoint = API + 'pagos/'
            data = {
                'chat_id': chat_id,
                'captura_comprobante': msg['photo'][0]['file_id']
            }
            response = requests.post(url=api_endpoint, data=data)
            bot.sendMessage(chat_id, 'Comprobante recibido.')

        elif content_type in ['text'] and is_comprobantes(msg['text']):
            # si es administrador
            if is_jd(username):
                api_endpoint = API + 'pagos/'
                r = requests.get(api_endpoint)
                pagos = r.json()
                for p in pagos:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Registrar', callback_data=p['id'])]
                        ])

                    bot.sendPhoto(chat_id, p['captura_comprobante'], reply_markup=keyboard, caption='Comprobante {}'.format(p['id']))

            else:
                bot.sendMessage(chat_id, 'Debes ser admin para usar este comando.')

        elif content_type in ['text'] and is_start(msg['text']):
            ci, usuario_cuartico, token_cuartico = get_cuartico_data(msg['text'])
            data = {}
            # Si tiene permisos para ver los comprobantes
            if token_cuartico == TOKEN_CUARTICO:
                data['usuario_cuartico'] = usuario_cuartico
                data['jd'] = True

            data['chat_id'] = chat_id
            data['ci'] = ci
            data['usuario_telegram'] = username

            api_endpoint = API + 'clientes/'
            r = requests.post(url = api_endpoint, data = data)
            bot.sendMessage(chat_id, 'Usuario registrado.')

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        username = msg['from']['username']
        # si es administrador
        if is_jd(username):
            # Se borra comprobante
            api_endpoint = API + 'pagos/'
            data = {
                'registrar': True,
                'pago_pk': query_data
            }
            r = requests.post(url=api_endpoint, data=data)
            data = r.json()

            if data['borrados']:
                bot.answerCallbackQuery(query_id, text='Registrado')
                bot.sendMessage(from_id, 'Comprobante {} registrado.'.format(int(query_data)+1))
            else:
                bot.answerCallbackQuery(query_id, text='Error registrando.')
                bot.sendMessage(from_id, 'Error registrando comprobante {}.'.format(int(query_data)+1))

        else:
            bot.sendMessage(from_id, 'Debes ser de la junta directiva para usar este comando.')

# Funcion que chequea si el usuario es JD
def is_jd(username):
    api_endpoint = API + 'clientes/'
    r = requests.get(url = api_endpoint, data={'usuario_telegram': username})
    data = r.json()
    return data['jd']

# Funcion que checkea si el texto es un comando
def is_command(text):
    text_list = text.split(' ')

    comando = text_list[0]  # unico token
    if comando[0] != '/':
        return False

    return True

# Funcion que chequea si el comando es /comprobantes
def is_comprobantes(comando):
    # si no es comando
    if not is_command(comando):
        return False

    # si tiene mas de un token el mensaje
    if len(comando.split(' ')) > 1:
        return False

    if comando[1:] == 'comprobantes':
        return True

    return False

# Funcion que checke si el comand es /start
def is_start(entrada):
    if not is_command(entrada):
        return False

    # /start <ci> o /start <ci> <usuario> <token>
    if not len(entrada.split(' ')) in [2, 4]:
        return False

    comando = entrada.split(' ')[0]
    if comando[1:] == 'start':
        return True

    return False

# Parser de los argumentos de /start
def get_cuartico_data(entrada):
    entrada_list = entrada.split(' ')
    if not (len(entrada_list) in [2, 4]):
        return False

    ret = []
    for e in entrada_list:
        ret.append(e)

    for i in range(len(e)-3):
        e.append(None)

    return ret

if __name__ == '__main__':
    TOKEN = os.environ.get('TOKEN')

    bot = telepot.DelegatorBot(TOKEN, [
        include_callback_query_chat_id(
            pave_event_space())(
                per_chat_id(), create_open, ChatSesion, timeout=3600),
    ])
    MessageLoop(bot).run_as_thread()
    print('Listening...')

    #keep the program running
    while 1:
        time.sleep(10)