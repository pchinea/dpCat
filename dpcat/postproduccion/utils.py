#encoding: utf-8

import string
import random
import unicodedata
import os
import threading

from configuracion import config

"""
Declara un cerrojo global para los bloqueos entre threads.
"""
lock = threading.Lock()

"""
Fija los valores de configuración por defecto
"""
def set_default_settings():
    defaults = [
        [ 'MAX_ENCODING_TASKS', 5 ],
        [ 'MELT_PATH' ,         '/usr/bin/melt' ], 
        [ 'FFMPEG_PATH',        '/usr/bin/ffmpeg' ],
        [ 'MAX_PREVIEW_WIDTH',  400 ],
        [ 'MAX_PREVIEW_HEIGHT', 300 ],
        [ 'VIDEO_LIBRARY_PATH', '/home/adminudv/videos/videoteca/' ],
        [ 'VIDEO_INPUT_PATH' ,  '/home/adminudv/videos/' ],
        [ 'PREVIEWS_PATH' ,     '/home/adminudv/videos/previews/' ],
        [ 'TOKEN_VALID_DAYS' ,  7 ],
        [ 'SITE_URL' ,          'http://127.0.0.1:8000' ],
        [ 'LOG_MAX_LINES',      1000 ],
    ]

    for op in defaults:
        config.get_option(op[0]) or config.set_option(op[0], op[1])

"""
Genera un token alfanumérico del tamaño dado
"""
def generate_token(length):
    return "".join([random.choice(string.letters + string.digits) for x in range(length)])

"""
Genera un nombre de fichero para un nuevo vídeo
"""
def generate_safe_filename(name, date, extension):
    day = date.strftime("%Y/%m/%d")
    safename = unicodedata.normalize('NFKD', name).encode('ascii','ignore').translate(None, string.punctuation).replace(' ', '_')
    return "%s_%s_%s%s" % (day, safename, generate_token(8), extension)

"""
Se asegura de que exista un directorio antes de crear un fichero en él.
"""
def ensure_dir(f):
    d = os.path.dirname(f)
    lock.acquire()
    if not os.path.exists(d):
        os.makedirs(d)
    lock.release()

"""
Borra el fichero dado y los directorios que lo contienen si están vacíos.
"""
def remove_file_path(f):
    if os.path.isfile(f):
        os.remove(f)
        try:
            os.removedirs(os.path.dirname(f))
        except OSError:
            pass

class FileIterWrapper(object):
    def __init__(self, flo, chunk_size = 1024**2):
        self.flo = flo
        self.chunk_size = chunk_size

    def next(self):
        data = self.flo.read(self.chunk_size)
        if data:
            return data
        else:
            raise StopIteration

    def __iter__(self):
        return self

def stream_file(filename):
    return FileIterWrapper(open(filename, "rb"))