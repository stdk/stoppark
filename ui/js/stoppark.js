var datatablesRuLang = {
    "sProcessing":   "Подождите...",
    "sLengthMenu":   "Показать _MENU_ записей",
    "sZeroRecords":  "Записи отсутствуют.",
    "sInfo":         "_START_ - _END_ : _TOTAL_ ",
    "sInfoEmpty":    "Нет данных",
    "sInfoFiltered": "(отфильтровано из _MAX_ записей)",
    "sInfoPostFix":  "",
    "sSearch":       "Поиск:",
    "sUrl":          "",
    "oPaginate": {
        "sFirst": "<<",
        "sPrevious": '<',
        "sNext": '>',
        "sLast": ">>"
    }
}

function jConfirm(args) {
 $( "#dialog-confirm-message" ).text(args['message'])
 $( "#dialog-confirm" ).dialog({
  resizable: false,
  height:140,
  modal: true,
  buttons: {
    "Подтвердить": function() {
      $( this ).dialog( "close" )
      args['ok']()      
    },
    "Отменить": function() {
      $( this ).dialog( "close" )
      args['cancel']()
    }
  }
 })
}

function sendCommand(path,args,success) {
  $.ajax({
        type: "POST",
        url: path,
        contentType: 'application/x-www-form-urlencoded',
        data: args,
        success: success,
        error : function() { alert(path + ":error"); }
  })
}


function initTable(selector,path,args) {

  var drawCallback = function() {}

  if('editors' in args) {
    var editors = args.editors
    var drawCallback = function() {
      var common_callback = function( value, settings ) {
        var aPos = table.fnGetPosition( this );
        table.fnUpdate( value, aPos[0], aPos[1] );
        $(this).css('font-weight','bold')
      }

      var submitdata = function ( value, settings ) {
        return {
          "row" : table.fnGetPosition( this )[0],
          "col" : table.fnGetPosition( this )[1]
        };
      }

      var editor_base = {
        callback: common_callback,
        submitdata: submitdata
      }

      for(var child in editors) {
        var editor = editors[child]
        var elements = $(selector + ' tbody td:nth-child(' + child +')')
        elements.editable(path + '/edit',$.extend(editor,editor_base))
        if('data' in editor) {
            elements.each(function(index,element) {
              var value = $(element).text()
              if(value in editor.data) {
                var aPos = table.fnGetPosition( element );
                table.fnUpdate( editor.data[value], aPos[0], aPos[1] , false);
              }
            })          
        }
      }
 
      if('delete' in args && args['delete']) {
        //⌫
        var button_template = '<input type="button" style="padding: 0px;width: 16px;height:16px" value="X" />&nbsp;'
        $(selector + ' tbody td:first-child').not(':has(input)').prepend(button_template)
                                             
        //$(selector + ' tbody td:first-child span.del').remove()
        //$(selector + ' tbody td:first-child').prepend('<span class="del">X&nbsp;</span>')
        //$(selector + ' tbody td:first-child span.del').click(function() {
        $(selector + ' tbody td:first-child input').button().click(function() {
          var element = this.parentNode
          jConfirm({
            message : 'Удалить ' + $(this.parentNode).text().substring(1) + '?',
            ok : function() {
              var row = table.fnGetPosition( element )[0]
              $.ajax({
                type: 'POST',
                url: path + '/delete',
                data: { row: row },
                success: function() {
                  table.fnReloadAjax()
                  /*$(element.parentNode).hide('highlight',{},1000,function() {
                    table.fnReloadAjax();
                  })*/                      
                },
                error : function(jqXHR, textStatus, errorThrown) { 
                  alert('Невозможно выполнить операцию: ' + errorThrown);
                }
              })//ajax
            }//ok function
          })//jConfirm call
        })//delete click
      }
    }
  }

  var table = $(selector).dataTable({
        oLanguage: datatablesRuLang,
        iDisplayLength: 15,
        bPaginate: true,
        bLengthChange: false,
        bFilter: 'filter' in args && args.filter,
        bSort: 'sort' in args && args.sort,
        bInfo: true,
        bAutoWidth: false,
        bProcessing: true,
        bJQueryUI: true,
        sAjaxSource: path + '/data',
        sPaginationType: 'full_numbers' ,
        aoColumnDefs: [],
        //sDom : 'fltrip',
        fnDrawCallback: drawCallback
  });

  if('add' in args && args.add) {
    $(selector+'-row-add').button().click(function() {
      $.ajax({
        type: "POST",
        url: path + "/add",
        contentType: 'application/x-www-form-urlencoded',
        data: {},
        success: function() { table.fnReloadAjax(); },
        error : function(jqXHR, textStatus, errorThrown) { 
          alert('Невозможно выполнить операцию: ' + errorThrown);
        }
      })
    })
  } else {
    $(selector+'-row-add').hide()
  }

  if('save-changes' in args && args['save-changes']) {
    $(selector + '-save-changes').button().click(function() {
      $.ajax({
        type: "POST",
        url: path + "/save",
        data: {},
        success: function() { table.fnReloadAjax(); },
        error : function(jqXHR, textStatus, errorThrown) { 
          alert('Невозможно выполнить операцию: ' + errorThrown);
        }
      })
    })
  } else {
    $(selector+'-save-changes').hide()
  }

  if('cancel-changes' in args && args['cancel-changes']) {
    $(selector + '-cancel-changes').button().click(function() {
      $.ajax({
        type: "POST",
        url: path + "/cancel",
        data: {},
        success: function() { table.fnReloadAjax(); },
        error : function(jqXHR, textStatus, errorThrown) { 
          alert('Невозможно выполнить операцию: ' + errorThrown);
        }
      })
    })
  } else {
    $(selector+'-cancel-changes').hide()
  }

  return table
}

var init = {
  gstatus: function(arg_base,generic_editors) {
    var gstatus = initTable('#status','/gstatus',{})
    $('#status_wrapper .fg-toolbar').hide()
    return gstatus
  },

  lstatus: function(arg_base,generic_editors) {
    return initTable('#boards','/lstatus',{})
  },

  cards: function(arg_base,generic_editors) {
    var card_type = { data: {'0':'служебный','1':'разовый','2':'клиент','3':'кассир','4':'админ'}, type : 'select' }
    var card_status = { data: {'1':'разрешен','2':'утерян','3':'просрочен','4':'запрещен'}, type : 'select' }
    var tariffs = { data: {}, type: 'select' }

    $.ajax({
        async: false,
        type: "GET",
        url: '/tariff/data',
        success: function(data,textStatus,jqXHR) {
          var aaData = $.parseJSON(data).aaData
          $.each(aaData,function(index,value) {
            tariffs.data[value[0]] = value[1]
          })
        }        
    })   

    var cardEditors = {}
    for(var i=2;i<17;i++) cardEditors[i] = generic_editors.text
    cardEditors[2] = card_type
    cardEditors[4] = generic_editors.date
    cardEditors[5] = generic_editors.date
    cardEditors[13] = card_status
    cardEditors[14] = tariffs
    var cards = initTable('#cards','/card',$.extend( { editors: cardEditors },arg_base))

    $('#cards_filter input').autocomplete({
      source: [  'разрешен','запрещен','администратор','кассир','пропуск' ],
      minLength: 0
    })

    return cards
  },

  tickets: function(arg_base,generic_editors) {
    var ticketEditors = {}
    for(var i = 2;i<12;i++) ticketEditors[i] = generic_editors.text
    return initTable('#tickets','/ticket',$.extend({},arg_base))
  },

  tariffs: function(arg_base,generic_editors) {
    var text = generic_editors.text
    var tariff_type = { type: 'select', data: { '1':'Фиксированный', '2':'Переменный', '3' : 'Разовый' }, width: "40px" }
    var tariff_interval = { type: 'select', data: { '1':'час', '2':'сутки', '3':'месяц' }, width: "20px" }
    var tariff_cost = { type: 'costpicker', isExtended: function(row) {
      var result = false
      row.find('td:nth-child(3)').each(function(idx,cell) {
        if( $(cell).text() == 'Переменный' ) result = true;
      })    
      return result
    } }
    var tariffEditors = { 2: text, 3: tariff_type, 4: tariff_interval, 5: tariff_cost, 6: generic_editors.time, 7: text, 8: text }
    return initTable('#tariffs','/tariff',$.extend( { editors: tariffEditors },arg_base))    
  },

  config: function(arg_base,generic_editors) {
    var configEditors = { 1: generic_editors.text, 2: generic_editors.text}
    var args = $.extend({ editors: configEditors }, arg_base)
    $.extend(args,{ add:    false,
                    delete: false,
                    filter: false,
                    sort:   false })
    return initTable('#config','/config',args)
  },

  events: function(arg_base,generic_editors) {
    return initTable('#events','/events',$.extend({},arg_base))
  },

  payments: function(arg_base,generic_editors) {
    return initTable('#payment','/payment',$.extend({},arg_base))
  }
}

$(document).ready(function() {
  var admin = $('#userlevel').text() == 'Администратор'
  $('#userinfo').addClass({true: 'admin', false: 'user'}[admin])

  $('#tabs').tabs()

  $('select').live('change', function() {
   $(this).parent().submit()
  })

  $('select').live('keydown', function (event) {
    if(event.keyCode == 13) $(this).parent().submit();
  })
  
  var arg_base = { 'add'            : admin,
                   'save-changes'   : admin,
                   'cancel-changes' : admin,
                   'delete'         : admin,
                   'filter'         : true,
                   'sort'           : true }

  var generic_editors = {
    text:  { height: "10px", width: "90px" },
    date:  { type: 'datepicker' },
    time:  { type: 'timepicker' },
    color: { height: "10px", data: " {'Черный':'Черный','Белый':'Белый','Желтый':'Желтый', 'selected':'Черный'}", type: 'select' } 
  }

  var table_config = { gstatus:  true,
                       lstatus:  true,
                       tickets:  true,
                       cards:    true,
                       tariffs:  true,                                              
                       config:   true,
                       payments: true,
                       events:   true
  }

  var tables = {}
  for(var key in table_config) {
    console.log(key)
    tables[key] = init[key](arg_base,generic_editors)
  }

  setInterval(function() {
    if( !admin ) { 
      for(var key in tables) {
        tables[key].fnReloadAjax()
      }
    } else {
      sendCommand('/gstatus/update',{},function() {
        tables.gstatus.fnReloadAjax()
      }) 

      sendCommand('/lstatus/update',{},function() {
        tables.lstatus.fnReloadAjax()
      })
   
      sendCommand('/ticket/update',{},function() {
        tables.tickets.fnReloadAjax()
      })

      sendCommand('/events/update',{},function() {
        tables.events.fnReloadAjax()
      })

      sendCommand('/payment/update',{},function() {
        tables.payments.fnReloadAjax()
      })
    }
  },8000)

})
