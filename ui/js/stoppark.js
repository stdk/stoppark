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

  var draw_callback = function() {}

  if('editors' in args) {
    var editors = args.editors
    var jEditable = 'jEditable' in args ? args.jEditable : true

    var callback = function( value, settings ) {
      if('transform' in settings) {
        value = settings.transform(value)
        $(this).data('value',value)
      }

      if('data' in settings && value in settings.data) {
        value = settings.data[value]
      }

      var aPos = table.fnGetPosition( this )
      table.fnUpdate( value, aPos[0], aPos[1], false )
      $(this).css('font-weight','bold')
    }

    var submitdata = function ( value, settings ) {
      var result = {
        "row" : table.fnGetPosition( this )[0],
        "col" : table.fnGetPosition( this )[1]
      }

      if('reverse_transform' in settings) {
        result[settings.name] = settings.reverse_transform(value)
      }

      return result
    }

    var editor_base = {
      callback: callback,
      submitdata: submitdata,
    }

    var draw_callback = function() {
      for(var child in editors) {
        var editor = editors[child]
        var elements = $(selector + ' tbody td:nth-child(' + child +')')        

        //jEditable attribute in editor prevails over global jEditor parameter
        if( ('jEditable' in editor && editor.jEditable) || ( !('jEditable' in editor) && jEditable) ) {
          elements.editable(path + '/edit',$.extend(editor,editor_base))
        }

        //data options allow us to replace value in cell with another value using predefined dictionary
        if('data' in editor) {
          elements.each(function(index,element) {
            var value = $(element).text()
            if(value in editor.data) {
              var aPos = table.fnGetPosition( element )
              table.fnUpdate( editor.data[value], aPos[0], aPos[1] , false)
            }
          })          
        }

        //transform option allows us to change value in cell using predefined function
        if('transform' in editor) {
          elements.each(function(index,element) {
            var e = $(element)
            var value = e.text()
            if(e.data('value') != value) {
              var transformed_value = editor.transform(value)
              var aPos = table.fnGetPosition( element )
              table.fnUpdate(transformed_value, aPos[0], aPos[1] , false)
              e.data('value',transformed_value)
            }
          })
        }
      }
 
      if('delete' in args && args.delete) {
        var action = {true: 'prepend', prepend: 'prepend', replace: 'html'}[args.delete]
        var button_template = '<input type="button" style="padding: 0px;width: 16px;height:16px" value="X" />&nbsp;'
        var button_elements = $(selector + ' tbody td:first-child').not(':has(input)')[action](button_template).find('input')
        button_elements.button().click(function() {        
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
                  table.fnReloadAjax(null,null,true)
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
        iDisplayLength: 20,
        bPaginate: true,
        bLengthChange: false,
        bFilter: 'filter' in args && args.filter,
        bSort: 'sort' in args && args.sort,
        bInfo: true,
        bAutoWidth: false,
        bProcessing: true,
        bJQueryUI: true,
        sAjaxSource: path + '/data',
        sPaginationType: 'full_numbers',
        aaSorting: [],
        bDeferRender: true,
        fnDrawCallback: draw_callback
  });

  if('add' in args && args.add) {
    $(selector+'-row-add').button().click(function() {
      $.ajax({
        type: "POST",
        url: path + "/add",
        contentType: 'application/x-www-form-urlencoded',
        data: {},
        success: function() { table.fnReloadAjax(null,null,true); },
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
        success: function() { table.fnReloadAjax(null,null,true); },
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
        success: function() { table.fnReloadAjax(null,null,true); },
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

function getForeignKeyData(path,args)
{
  var result = {}

  if(!args) args = {}

  var i = 'i' in args ? args.i : 0
  var j = 'j' in args ? args.j : 1

  $.ajax({
      async: 'async' in args ? args.async : false,
      type: "GET",
      url: path,
      success: function(data,textStatus,jqXHR) {
        var aaData = $.parseJSON(data).aaData
        $.each(aaData,function(index,value) {
          result[value[i]] = value[j]
        })
      }        
  }) 

  return result
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

  cards: function(arg_base,generic) {
    var card_type = { data: {'0':'служебный','1':'разовый','2':'клиент','3':'кассир','4':'админ'}, type : 'select' }
    var card_status = { data: {'1':'разрешен','2':'утерян','3':'просрочен','4':'запрещен'}, type : 'select' }

    var editors = {}
    for(var i=2;i<17;i++) editors[i] = generic.text
    editors[2] = card_type
    editors[4] = generic.date
    editors[5] = generic.date
    editors[13] = card_status
    editors[14] = generic.tariff
    var cards = initTable('#cards','/card',$.extend( { editors: editors },arg_base))

    $('#cards_filter input').autocomplete({
      source: [  'разрешен','запрещен','администратор','кассир','пропуск' ],
      minLength: 0
    })

    return cards
  },

  tickets: function(arg_base,generic) {
    var editors = { 3: generic.tariff, 4: generic.price, 5: generic.price, 11: generic.status }
    return initTable('#tickets', '/ticket', $.extend({editors: editors},arg_base,{delete: false, jEditable: false}))
  },

  tariffs: function(arg_base,generic_editors) {
    var text = generic_editors.text
    var tariff_type = { type: 'select',
                        data: { '1':'Фиксированный', '2':'Переменный', '3' : 'Разовый', '4' : 'Новый тариф' }, 
                        width: "40px" }
    var tariff_interval = { type: 'select', data: { '1':'час', '2':'сутки', '3':'месяц' }, width: "20px" }
    var tariff_cost = { type: 'costpicker', jEditable: true, isExtended: function(row) {
      var result = false
      row.find('td:nth-child(3)').each(function(idx,cell) {
        var t = $(cell).text()
        if( t == tariff_type.data['2'] || t == tariff_type.data['4'] ) result = true;
      })    
      return result
    } }
    var tariffEditors = { 2: text, 3: tariff_type, 4: tariff_interval, 5: tariff_cost, 6: generic_editors.time, 7: text, 8: text }
    return initTable('#tariffs','/tariff',$.extend( { editors: tariffEditors },arg_base))    
  },

  config: function(arg_base,generic_editors) {
    var configEditors = { 1: generic_editors.text, 2: generic_editors.text}
    var args = $.extend({ editors: configEditors }, arg_base, 
      { add:    false,
        delete: false,
        filter: false,
        sort:   false  } )
    return initTable('#config','/config',args)
  },

  events: function(arg_base,generic) {
    var events = { type: 'select', data: { 'moving' :'Проезд','opening':'Открытие', 'unknown':'Неизвестно' } }
    var direction = { type: 'select', data: { 'into'   :'Въезд', 'outfrom':'Выезд' } }
    var reason = { type: 'select', data: { 'auto'   :'Автоматический', 'manual' :'Ручной' } }
    var editors = { 1: events, 3: generic.terminal, 4: direction, 5: reason }
    return initTable('#events','/events',$.extend({editors: editors},arg_base,{delete: false, jEditable: false}))
  },

  payments: function(arg_base,generic) {
    var payments = { type: 'select',
      data: {
        'Card payment'  : 'Абонемент',
        'Single payment': 'Разовый',
        'Talon payment' : 'Талон'
      }
    }

    var editors = { 1: payments, 3: generic.tariff, 7: generic.status, 8: generic.price, 12: generic.price }
    return initTable('#payment','/payment',$.extend({editors: editors},arg_base,{delete: false, jEditable: false}))
  },

  terminals: function(arg_base,generic) {
    var editors = { 2: generic.text, 3: generic.text }
    return initTable('#terminals','/terminal',$.extend({editors: editors},arg_base,{ delete: 'replace' }))
  },

  users: function(arg_base,generic) {
    var user_level = { type: 'select', data: { '1' : 'Пользователь', '2' : 'Администратор' } }
    var password = $.extend({ transform: function(value) { return '***********' } }, generic.text)
    var editors = { 2: generic.text, 3: password, 4: user_level }
    return initTable('#users','/user',$.extend( { editors: editors },arg_base))
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
  
  var arg_base = { 'jEditable'      : admin,
                   'add'            : admin,
                   'save-changes'   : admin,
                   'cancel-changes' : admin,
                   'delete'         : admin,
                   'filter'         : true,
                   'sort'           : true }

  var generic_editors = {
    text  : { height: "9px", width: "70px" },
    date  : { type: 'datepicker' },
    time  : { type: 'timepicker' },
    color : { height: "10px", data: " {'Черный':'Черный','Белый':'Белый','Желтый':'Желтый', 'selected':'Черный'}", type: 'select' },
    status: { type: 'select', data: { '1' : 'Въехал', '5' : 'Оплачен', '13': 'Выехал' } },
    tariff: { type: 'select', data: {} },
    price : { height:"9px",
             transform: function(value) { return (parseFloat('0'+value)/100).toString() },
             reverse_transform: function(value) { return (parseFloat('0'+value)*100).toString() }
    },

    terminal: {type: 'select', data: {} },

    doUpdate: function(async) {
      this.tariff.data = getForeignKeyData('/tariff/data',{ i: 0, j: 1, async: async })
      this.terminal.data = getForeignKeyData('/terminal/data',{i: 1, j: 2, async: async})
    }
  }

  generic_editors.doUpdate(false)  

  var tables = {}
  $.each({ gstatus:  true,
           lstatus:  true,
           tickets:  true,
           cards:    true,
           tariffs:  true,                                              
           config:   true,
           payments: true,
           events:   true,
           terminals:true,
           users:    true
  },function(key,value) {
    if(value) tables[key] = init[key](arg_base,generic_editors)
  })

  setInterval(function() {
    generic_editors.doUpdate(true)

    if( !admin ) { 
      for(var key in tables) {
        tables[key].fnReloadAjax(null,null,true)
      }
    } else { //update only tables that we cannot edit in admin interface, i.e. readonly tables 
      tables.gstatus.fnReloadAjax()
      tables.lstatus.fnReloadAjax()
      tables.tickets.fnReloadAjax(null,null,true)
      tables.events.fnReloadAjax(null,null,true)
      tables.payments.fnReloadAjax(null,null,true)
    }
  },10000)

})