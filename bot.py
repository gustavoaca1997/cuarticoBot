import sys
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

class ChatSesion(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(ChatSesion, self).__init__(*args, **kwargs)

    # Manejador de mensajes
    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        # Si es un comprobante
        if content_type in ['photo']:
            comprobantes.append(Comprobante(msg))

            print('\n\nComprobante recibido:')
            pprint(msg)

        elif content_type in ['text'] and is_comprobantes(msg['text']):
            indice = 0
            for c in comprobantes:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Registrado', callback_data=indice)]
                    ])

                bot.sendPhoto(chat_id, c.msg['photo'][0]['file_id'], reply_markup=keyboard, caption='Comprobante {}'.format(indice))

                indice += 1

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        # Se borra comprobante
        del comprobantes[int(query_data)]
        print('\nRegistrado comprobante', query_data)

        print('\n\nCallback Query:')
        pprint(msg)
        
        bot.sendMessage(from_id, 'Comprobante {} registrado.'.format(query_data))


# Funcion que checkea si el texto es un comando
def is_command(text):
    text_list = text.split(' ')

    # Si hay mas de un token o ninguno,
    # no es un comando
    if len(text_list) != 1:
        return False

    comando = text_list[0]  # unico token
    if comando[0] != '/':
        return False

    return True

# Funcion que chequea si el comando es /comprobantes
def is_comprobantes(comando):
    # si no es comando
    if not is_command(comando):
        return False

    if comando[1:] == 'comprobantes':
        return True

if __name__ == '__main__':
    TOKEN = sys.argv[1] #get token from cli

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