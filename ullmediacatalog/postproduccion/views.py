# Create your views here.
# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse

from postproduccion.models import Video, Cola
from postproduccion.forms import VideoForm, FicheroEntradaForm
from postproduccion.queue import enqueue_copy, progress
from postproduccion import utils
from configuracion import config

import os
import urllib

"""
Muestra el formulario para insertar un nuevo proyecto de vídeo.
"""
def crear(request):
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            v = form.save()
            return HttpResponseRedirect(reverse('postproduccion.views.fichero_entrada', args=(v.id,)))
    else:
        form = VideoForm()
    return render_to_response("postproduccion/crear.html", { 'form' : form }, context_instance=RequestContext(request))


"""
Muestra el formulario para seleccionar el fichero de entrada.
"""
def _fichero_entrada_simple(request, v):
    if request.method == 'POST':
        form = FicheroEntradaForm(request.POST)
        if form.is_valid():
            fe = form.save(commit = False)
            fe.video = v
            fe.fichero = os.path.normpath(config.get_option('VIDEO_INPUT_PATH') + fe.fichero)
            fe.save()
            enqueue_copy(v)
            return HttpResponse("Video introducido y encolado")
    else:
        form = FicheroEntradaForm()
    return render_to_response("postproduccion/fichero_entrada.html", { 'form' : form }, context_instance=RequestContext(request))

"""
Muestra el formulario para seleccionar los ficheros de entrada.
"""
def _fichero_entrada_doble(request, v):
    return HttpResponse("Video plantilla")

"""
Llama al método privado adecuado para insertar los ficheros de entrada según
el tipo de vídeo.
"""
def fichero_entrada(request, video_id):
    v = get_object_or_404(Video, pk=video_id)
    if v.plantilla:
        return _fichero_entrada_doble(request, v)
    else:
        return _fichero_entrada_simple(request, v)

"""
Devuelve una lista (html) con el contenido de un directorio para usar con la
llamada AJAX del jqueryFileTree.
"""
def dirlist(request):
    r=['<ul class="jqueryFileTree" style="display: none;">']
    try:
        r=['<ul class="jqueryFileTree" style="display: none;">']
        basedir = urllib.unquote(config.get_option('VIDEO_INPUT_PATH'))
        reqdir = urllib.unquote(request.POST.get('dir'))
        fulldir = os.path.normpath(basedir + reqdir)
        for f in os.listdir(fulldir):
            ff = os.path.join(reqdir, f)
            if os.path.isdir(os.path.join(fulldir, f)):
                r.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff, f))
            else:
                e =os.path.splitext(f)[1][1:] # get .ext and remove dot
                r.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (e, ff, f))
        r.append('</ul>')
    except Exception,e:
        r.append('Could not load directory: %s' % str(e))
    r.append('</ul>')
    return HttpResponse(''.join(r))

def cola_base(request):
    return render_to_response("postproduccion/cola_base.html", context_instance=RequestContext(request))

def cola_listado(request):
    import json
    data = list()
    for task in Cola.objects.order_by('pk'):
        linea = dict()
        linea['video'] = task.video.titulo
        linea['tipo'] = dict(Cola.QUEUE_TYPE)[task.tipo]
        linea['comienzo'] = task.comienzo.__str__() if task.comienzo else ""
        linea['fin'] = task.fin.__str__() if task.fin else ""
        linea['logfile'] = task.logfile.name
        linea['id'] = task.pk
        linea['status'] = progress(task) if task.status == 'PRO' else dict(Cola.QUEUE_STATUS)[task.status]
        data.append(linea)
        pass
    return HttpResponse(json.dumps(data))
