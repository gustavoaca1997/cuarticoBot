import sys
import os
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import pave_event_space, per_chat_id, create_open, include_callback_query_chat_id

from pprint import pprint

from Comprobante import Comprobante

# Lista de comprobantes sin registrar
comprobantes = []

# Diccionario de admins
admins = telepot.helper.SafeDict()

# Token para el cuartico
TOKEN_CUARTICO = os.environ.get('TOKEN_CUARTICO')

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
            comprobantes.append(Comprobante(msg))

            print('\n\nComprobante recibido:')
            pprint(msg)

            bot.sendMessage(chat_id, 'Comprobante recibido.')

        elif content_type in ['text'] and is_comprobantes(msg['text']):
            # si es administrador
            if username in admins:
                indice = 0
                for c in comprobantes:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Registrar', callback_data=indice)]
                        ])

                    bot.sendPhoto(chat_id, c.msg['photo'][0]['file_id'], reply_markup=keyboard, caption='Comprobante {}'.format(indice+1))

                    indice += 1

            else:
                bot.sendMessage(chat_id, 'Debes ser admin para usar este comando.')

        elif content_type in ['text'] and is_start(msg['text']):
            usuario_cuartico, token_cuartico = get_cuartico_data(msg['text'])

            # Si tiene permisos para ver los comprobantes
            if token_cuartico == TOKEN_CUARTICO:
                admins[username] = {
                    'deuda': 0,
                    'chat_id': chat_id,
                    'usuario_cuartico': usuario_cuartico
                }
                bot.sendMessage(chat_id, 'Administrador registrado.')

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        username = msg['from']['username']
        # si es administrador
        if username in admins:
            # Se borra comprobante
            del comprobantes[int(query_data)]
            print('\nRegistrado comprobante', query_data)

            print('\n\nCallback Query:')
            pprint(msg)

            bot.answerCallbackQuery(query_id, text='Registrado')
            bot.sendMessage(from_id, 'Comprobante {} registrado.'.format(int(query_data)+1))

        else:
            bot.sendMessage(from_id, 'Debes ser admin para usar este comando.')


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

    # /start o /start <usuario> <token>
    if not len(entrada.split(' ')) in [1, 3]:
        return False

    comando = entrada.split(' ')[0]
    if comando[1:] == 'start':
        return True

    return False

# Parser de los argumentos de /start
def get_cuartico_data(entrada):
    entrada_list = entrada.split(' ')
    assert(len(entrada_list) in [1, 3])

    # Si no se registró ningun admin
    if len(entrada_list) == 1:
        return None, None

    return entrada_list[1], entrada_list[2]

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