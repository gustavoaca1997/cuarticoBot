import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from Comprobante import Comprobante

# Lista de comprobantes sin registrar
comprobantes = []

# Manejador de mensajes
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    # Si es un comprobante
    if content_type in ['photo']:
        comprobantes.append(Comprobante(msg))
        print(msg)

    elif content_type in ['text'] and is_comprobantes(msg['text']):
        for c in comprobantes:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Registrado', callback_data=comprobantes.index(c))]
                ])

            bot.sendPhoto(chat_id, c.msg['photo'][0]['file_id'], reply_markup=keyboard)

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    # Se borra comprobante
    del comprobantes[int(query_data)]
    print('Registrado comprobante', query_data)


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

    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {
            'chat': on_chat_message,
            'callback_query': on_callback_query
        }).run_as_thread()
    print('Listening...')

    #keep the program running
    while 1:
        time.sleep(10)