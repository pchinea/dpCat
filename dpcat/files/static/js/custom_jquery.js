

// Hacer desaparecer los mensajes tipo.

$(document).ready(function() {
    $(".cerrar").click(function () {
        $(this.parentNode).animate({ opacity: 0, height: 0 }, "slow").hide("slow");
    });

    $(".alerta-header").click(function () {
        $(this).find(".icon").toggleClass("minus").toggleClass("plus");
        $(this).parents(".alerta:first").find(".alerta-content").toggle();
    });

    $(".rechazar").click(function () {
        $(this.parentNode.parentNode).find(".form-validacion-opciones").toggle();
        $(this.parentNode.parentNode).find(".form-validacion-rechaza").toggle();
    });

    $(function() {
        var dates = $( "#from, #to" ).datepicker({
            maxDate: "+0d",
            changeMonth: true,
            changeYear: true,
            numberOfMonths: 3,
            onSelect: function( selectedDate ) {
                var option = this.id == "from" ? "minDate" : "maxDate",
                    instance = $( this ).data( "datepicker" ),
                    date = $.datepicker.parseDate(
                        instance.settings.dateFormat ||
                        $.datepicker._defaults.dateFormat,
                        selectedDate, instance.settings );
                dates.not( this ).datepicker( "option", option, date );
           }
        });
    });

// Dialog eliminar producción
    $( "#dialog-eliminar" ).dialog({
        autoOpen: false,
        modal: true
    });

    $(".eliminar").click(function (e) {
        e.preventDefault();
        var urlEliminar = $(this).attr("href");
        $( "#dialog-eliminar" ).dialog({
            autoOpen: false,
            resizable: false,
            height:160,
            modal: true,
            buttons: {
                "Eliminar": function() {
                   window.location.href = urlEliminar;
                },
                "Cancelar": function() {
                    $( this ).dialog( "close" );
                }
            }
        });
        $( "#dialog-eliminar" ).dialog("open");
    });

// Dialog validación de producción
    $( "#dialog-validar" ).dialog({
        autoOpen: false,
        modal: true
    });

    $(".validar").click(function (e) {
        e.preventDefault();
        var urlValidar = $(this).attr("href");
        $( "#dialog-validar" ).dialog({
            autoOpen: false,
            resizable: false,
            height:160,
            modal: true,
            buttons: {
                "Validar": function() {
                   window.location.href = urlValidar;
                },
                "Cancelar": function() {
                    $( this ).dialog( "close" );
                }
            }
        });
        $( "#dialog-validar" ).dialog("open");
    });

// Dialog publicación de producción
    $( "#dialog-publicar" ).dialog({
        autoOpen: false,
        modal: true
    });

    $(".publicar").click(function (e) {
        e.preventDefault();
        var urlPublicar = $(this).attr("href");
        $( "#dialog-publicar" ).dialog({
            autoOpen: false,
            resizable: false,
            height:160,
            modal: true,
            buttons: {
                "Publicar": function() {
                   window.location.href = urlPublicar;
                },
                "Cancelar": function() {
                    $( this ).dialog( "close" );
                }
            }
        });
        $( "#dialog-publicar" ).dialog("open");
    });

// Dialog generación de ticket
    $('#dialog-generarticket').dialog({
        autoOpen: false,
        height: 160,
        modal: true,
        resizable: false,
        buttons: {
            "Generar ticket": function() {
                document.formgenerarticket.submit();
            },
            "Cancelar": function() {
                $(this).dialog("close");
            }
        }
    });

    $("input.generarticket").click(function(e) {
        e.preventDefault();
        $("#dialog-generarticket").dialog("open");
    });

});


// Arrastra y ordena

$(function() {
    $( ".column" ).sortable({
        connectWith: ".column"
    });

    $( ".portlet" ).addClass( "ui-widget ui-widget-content ui-helper-clearfix ui-corner-all" )
        .find( ".portlet-header" )
            .addClass( "ui-widget-header ui-corner-all" )
            .prepend( "<span class='ui-icon ui-icon-minusthick'></span>")
            .end()
        .find( ".portlet-content" );

    $( ".portlet-header .ui-icon" ).click(function() {
        $( this ).toggleClass( "ui-icon-minusthick" ).toggleClass( "ui-icon-plusthick" );
        $( this ).parents( ".portlet:first" ).find( ".portlet-content" ).toggle();
    });

    $( ".portlet-header" ).disableSelection();
});
