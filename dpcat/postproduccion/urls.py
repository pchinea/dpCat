from django.conf.urls.defaults import *


urlpatterns = patterns('postproduccion.views',
    url(r'^$', 'index', name ="index"),
    url(r'^crear/$', 'crear', name = "crear"),
    url(r'^crear/(?P<video_id>\d+)/$', 'crear', name = "crear"),
    (r'^fichero_entrada/(?P<video_id>\d+)/$', 'fichero_entrada'),
    (r'^resumen_video/(?P<video_id>\d+)/$', 'resumen_video'),
    (r'^dirlist/$', 'dirlist'),
    url(r'^cola/$', 'cola_base', name = "cola"),
    (r'^cola_listado/$', 'cola_listado'),
    url(r'^mostrar_log/(?P<task_id>\d+)/$', 'mostrar_log', name = "mostrar_log"),
    url(r'^definir_metadatos/(?P<tk_str>\w{25})/$', 'definir_metadatos_user', name = "definir_metadatos_user"),
    url(r'^definir_metadatos/(?P<video_id>\d+)/$', 'definir_metadatos_oper', name = "definir_metadatos_oper"),
    url(r'^estado_video/(?P<video_id>\d+)/$', 'estado_video', name = "estado_video"),
    url(r'^validar_produccion/(?P<video_id>\d+)/$', 'validar_produccion', name = "validar_produccion"),
    url(r'^media_info/(?P<video_id>\d+)/$', 'media_info', name = "media_info"),
    url(r'^download_media_info/(?P<video_id>\d+)/$', 'download_media_info', name = "download_media_info"),
    url(r'^gestion_tickets/(?P<video_id>\d+)/$', 'gestion_tickets', name = "gestion_tickets"),
    url(r'^borrar/(?P<video_id>\d+)/$', 'borrar_produccion', name = "borrar"),
    url(r'^aprobacion_video/(?P<tk_str>\w{25})/$', 'aprobacion_video', name = "aprobacion_video"),
    url(r'^rechazar_video/(?P<tk_str>\w{25})/$', 'rechazar_video', name = "rechazar_video"),
    url(r'^stream/(?P<video_id>\d+).mp4$', 'stream_video', name = "stream_video"),
    url(r'^stream/(?P<tk_str>\w{25}).flv$', 'stream_preview', name = "stream_preview"),
    url(r'^enproceso/$', 'listar_en_proceso', name = "enproceso"),
    url(r'^pendientes/$', 'listar_pendientes', name = "pendientes"),
    url(r'^log/$', 'showlog', name = 'log'),
    url(r'^oldlog/$', 'showlog', { 'old' : True }, name = "oldlog"),
    url(r'^alertas/$', 'alerts', name = "alertas"),
    url(r'^config/$', 'config_settings', name = "config"),
    url(r'^status/$', 'status', name = "status"),
    url(r'^config_plugin/$', 'config_plugin', name = "config_plugin"),
    url(r'^publicar/(?P<video_id>\d+)/$', 'publicar', name = "publicar"),
    url(r'^videoteca/$', 'videoteca', name = "videoteca"),
    url(r'^ultimas/$', 'ultimas_producciones', name = "ultimas"),
)
