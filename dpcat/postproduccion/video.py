#encoding: utf-8
from django.shortcuts import render_to_response
from postproduccion.encoder import get_file_info, encode_mixed_video, encode_preview, get_video_duration
from postproduccion.models import TecData, Previsualizacion
from configuracion import config
from postproduccion import utils

from xml.dom.minidom import parseString
import os
import tempfile
import shutil
import string


"""
Renderiza el fichero de configuración del MELT para la codificación de una píldora
"""
def get_fdv_template(v):
    data = dict()
    data['fondo'] = v.plantilla.fondo.path

    videos = list()
    duracion = list()
    for i in v.ficheroentrada_set.all():
        fe = dict()
        fe['fichero'] = i.fichero
        fe['geom'] = "%d,%d:%dx%d:%d" % (
            i.tipo.x,
            i.tipo.y,
            i.tipo.ancho,
            i.tipo.alto,
            i.tipo.mix
        )
        duracion.append(get_video_duration(i.fichero))
        
        videos.append(fe)
    data['videos'] = videos
    data['duracion'] = min(duracion) * 25

    return render_to_response('postproduccion/get_fdv_template.mlt', { 'data' : data })

"""
"""
def generate_tecdata(v):
    try:
        t = v.tecdata
    except TecData.DoesNotExist:
        t = TecData(video = v)
        t.save()

    [t.xml_data, t.txt_data] = get_file_info(v.fichero)
    t.duration = get_video_duration(v.fichero)
    t.save()

"""
"""
def get_tec_data(xmlstring):
    dom = parseString(xmlstring)
    unparse_width = dom.getElementsByTagName('Width')[0].firstChild.data
    unparse_height = dom.getElementsByTagName('Height')[0].firstChild.data
    unparse_ratio = dom.getElementsByTagName('Display_aspect_ratio')[0].firstChild.data

    width = int(str(unparse_width).translate(None, string.letters +  string.whitespace))
    height = int(str(unparse_height).translate(None, string.letters +  string.whitespace))

    if ':' in unparse_ratio:
        [rw, rh] = unparse_ratio.split(':')
        ratio = float(rw)  / float(rh)
    else:
        ratio = float(unparse_ratio)

    return [width, height, ratio]

"""
"""
def parse_mediainfo(mediadata):
    mediainfo = list()
    for section in mediadata.split('\n\n'):
        if len(section) > 1:
            lines = section.split('\n')
            titulo = lines[0]
            sect = { 'section' : lines[0], 'attr' : list() }
            for attr in lines[1:]:
                sect['attr'].append({ 'key' : attr[:33].strip(), 'value' : attr[34:].strip() })
            mediainfo.append(sect)
    return mediainfo


def calculate_preview_size(v):
    [width, height, ratio] = get_tec_data(v.tecdata.xml_data)
    max_width = float(config.get_option('MAX_PREVIEW_WIDTH'))
    max_height = float(config.get_option('MAX_PREVIEW_HEIGHT'))

    # Hace los pixels cuadrados
    if ratio > 0:
        width = height * ratio
    else:
        try:
            height = width / ratio
        except ZeroDivisionError:
            pass
    
    # Reduce el ancho
    if width > max_width:
        r = max_width / width
        width *= r
        height *= r

    # Reduce el alto
    if height > max_height:
        r = max_height / height
        width *= r
        height *= r

    # Hace el tamaño par (necesario para algunos codecs)
    width = int((width + 1) / 2) * 2
    height = int((height + 1) / 2) * 2

    return dict({'width' : width, 'height' : height, 'ratio' : ratio})

"""

"""
def create_pil(video, logfile, pid_notifier = None):
    # Actualiza el estado del vídeo
    video.set_status('PRV')

    # Guarda la plantilla en un fichero temporal
    (handler, path) = tempfile.mkstemp(suffix='.mlt')
    os.write(handler, get_fdv_template(video).content)
    os.close(handler)

    # Genera el nombre del fichero de salida
    video.fichero = os.path.join(config.get_option('VIDEO_LIBRARY_PATH'), utils.generate_safe_filename(video.titulo, video.informeproduccion.fecha_produccion.date(), ".mp4"))
    video.save()
    utils.ensure_dir(video.fichero)

    # Montaje y codificación de la píldora
    if encode_mixed_video(path, video.fichero, logfile, pid_notifier) != 0:
        video.set_status('DEF')
        os.unlink(path)
        try:
            os.unlink(video.fichero)
        except:
            pass
        return False

    # Obtiene la información técnica del vídeo generado.
    generate_tecdata(video)

    # Borra el fichero temporal
    os.unlink(path)

    # Actualiza el estado del vídeo
    if video.informeproduccion.aprobacion:
        video.set_status('COM')
    else:
        video.set_status('PTO')
    
    return True

def copy_video(video, logfile):
    # Actualiza el estado del vídeo
    video.set_status('PRV')

    # Obtiene los nombres de ficheros origen y destino
    src = video.ficheroentrada_set.all()[0].fichero
    dst = os.path.join(config.get_option('VIDEO_LIBRARY_PATH'), utils.generate_safe_filename(video.titulo, video.informeproduccion.fecha_produccion.date(), os.path.splitext(src)[1]))
    video.fichero = dst
    video.save()

    # Copia el fichero.
    utils.ensure_dir(video.fichero)
    try:
        shutil.copy(src, dst)
        os.write(logfile, '%s -> %s\n' % (src, dst))
    except IOError as error:
        os.write(logfile, error.__str__())
        video.set_status('DEF')
        return False

    # Obtiene la información técnica del vídeo copiado.
    generate_tecdata(video)

    # Actualiza el estado del vídeo
    if video.informeproduccion.aprobacion:
        video.set_status('COM')
    else:
        video.set_status('PTO')

    return True

def create_preview(video, logfile, pid_notifier = None):
    # Actualiza el estado del vídeo
    video.set_status('PRP')

    # Obtiene los nombres de ficheros origen y destino
    src = video.fichero
    dst = os.path.join(config.get_option('PREVIEWS_PATH'), utils.generate_safe_filename(video.titulo, video.informeproduccion.fecha_produccion.date(), ".flv"))

    # Crea el objecto previsualización
    pv = Previsualizacion(video = video, fichero = dst)
    pv.save()

    # Calcula las dimensiones de la previsualización.
    size = calculate_preview_size(video)

    # Codifica la previsualización.
    utils.ensure_dir(pv.fichero)
    if encode_preview(src, dst, size, logfile, pid_notifier) != 0:
        video.set_status('COM')
        try:
            os.unlink(dst)
        except:
            pass
        return False

    # Actualiza el estado del vídeo
    video.set_status('PTU')
    return True
