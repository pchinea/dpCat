#encoding: utf-8

import string
import random
import unicodedata
import os
import threading
import subprocess
import shlex
import re
import json

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
        [ 'MELT_PATH' ,         which('melt') ], 
        [ 'FFMPEG_PATH',        which('ffmpeg') ],
        [ 'CRONTAB_PATH',       which('crontab') ],
        [ 'MEDIAINFO_PATH',     which('mediainfo') ],
        [ 'MAX_PREVIEW_WIDTH',  400 ],
        [ 'MAX_PREVIEW_HEIGHT', 300 ],
        [ 'VIDEO_LIBRARY_PATH', '/home/adminudv/videos/videoteca/' ],
        [ 'VIDEO_INPUT_PATH' ,  '/home/adminudv/videos/' ],
        [ 'PREVIEWS_PATH' ,     '/home/adminudv/videos/previews/' ],
        [ 'TOKEN_VALID_DAYS' ,  7 ],
        [ 'SITE_URL' ,          'http://127.0.0.1:8000' ],
        [ 'LOG_MAX_LINES',      1000 ],
        [ 'MAX_NUM_LOGFILES',   6 ],
    ]

    for op in defaults:
        config.get_option(op[0]) or config.set_option(op[0], op[1])

"""
Lista los plugins de publicación activos.
"""
def list_plugins():
    try:
        return json.loads(config.get_option('PUBLICATION_PLUGINS'))
    except TypeError:
        return list()

"""
Añade un nuevo plugin de publicación.
"""
def add_plugin(plugin_name):
    lst = list_plugins()
    lst.append(plugin_name)
    config.set_option('PUBLICATION_PLUGINS', json.dumps(lst))

"""
Elimina un plugin de publicación.
"""
def del_plugin(plugin_name):
    lst = list_plugins()
    try:
        lst.remove(plugin_name)
        config.set_option('PUBLICATION_PLUGINS', json.dumps(lst))
    except ValueError:
        pass

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

"""
Comprueba si la ruta dada corresponde a un fichero ejecutable
"""
def is_exec(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

"""
Trata de localizar la ruta del ejecutable dado en el PATH
"""
def which(fpath):
    command = "which %s" % fpath
    return subprocess.Popen(shlex.split(str(command)), stdout = subprocess.PIPE).communicate()[0].strip()

"""
Devuelve la versión del ffmpeg instalado.
"""
def ffmpeg_version():
    fpath = config.get_option('FFMPEG_PATH')
    if is_exec(fpath):
        command = "%s -version" % fpath
        data = subprocess.Popen(shlex.split(str(command)), stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()[0]
        return re.search('svn-(r[0-9]+)', data, re.I).group(1)
    
"""
Devuelve la versión del melt instalado.
"""
def melt_version():
    fpath = config.get_option('MELT_PATH')
    if is_exec(fpath):
        command = "%s -version" % fpath
        data = subprocess.Popen(shlex.split(str(command)), stderr = subprocess.PIPE).communicate()[1]
        return re.search('mlt melt ([\.0-9]+)', data, re.I).group(1)
    
"""
Devuelve la versión del mediainfo instalado.
"""
def mediainfo_version():
    fpath = config.get_option('MEDIAINFO_PATH')
    if is_exec(fpath):
        command = "%s --Version" % fpath
        data = subprocess.Popen(shlex.split(str(command)), stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()[0]
        return re.search('(v[0-9\.]+)$', data).group(1)

"""
Devuelve la información de uso del sistema de ficheros en el que se encuentra la ruta dada.
"""
def df(fpath):
    command = "df %s -Ph" % fpath
    data = subprocess.Popen(shlex.split(str(command)), stdout = subprocess.PIPE).communicate()[0].strip().splitlines()[1]
    return re.search('^.* +([0-9,]+[KMGTPEZY]?) +([0-9,]+[KMGTPEZY]?) +([0-9,]+[KMGTPEZY]?) +([0-9,]+%) +(/.*$)', data).group(1, 2, 3, 4, 5)

"""
Comprueba si el directorio dado existe y es accesible. Si no existe y puede, lo creará y devolverá verdadero.
"""
def check_dir(fpath):
    if os.path.isdir(fpath) and os.access(fpath, os.R_OK | os.W_OK | os.X_OK):
        return True
    if not os.path.exists(fpath):
        try:
            os.makedirs(fpath)
        except:
            return False
        return True
    else:
        return False

"""
Clase envoltorio que permite iterar sobre un fichero.
"""
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

"""
Devuelve a modo de flujo el contenido del fichero dado.
"""
def stream_file(filename):
    return FileIterWrapper(open(filename, "rb"))
