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
 });
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
        $(selector + ' tbody td:first-child div.del').remove()
        $(selector + ' tbody td:first-child').prepend('<span class="del">⌫</span>&nbsp;')
        $(selector + ' tbody td:first-child span.del').click(function() {
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
  }

  return table
}

$(document).ready(function() {
  $('#tabs').tabs()

  $('select').live('change', function() {
   $(this).parent().submit()
  })

  $('select').live('keydown', function (event) {
    if(event.keyCode == 13) $(this).parent().submit();
  })

  var gstatus = initTable('#status','/gstatus',{})
  var lstatus = initTable('#boards','/lstatus',{})  
  $('#status_wrapper .fg-toolbar').hide()
//  $('#status_wrapper tr:first-child th:first-child').hide()

  arg_base = { 'add'            : true,
               'save-changes'   : true,
               'cancel-changes' : true,
               'delete'         : true,
               'filter'         : true,
               'sort'           : true }

  var text = { height: "10px", width: "90px" }
  var color = { height: "10px", data: " {'Черный':'Черный','Белый':'Белый','Желтый':'Желтый', 'selected':'Черный'}", type: 'select' }
  var date = { type: 'datepicker' }
  var time = { type: 'timepicker' } 

  var card_type = { data : {'0':'служебный','1':'разовый','2':'клиент','3':'кассир','4':'админ'}, type : 'select' }
  var card_status = { data : {'1':'разрешен','2':'утерян','3':'просрочен','4':'запрещен'}, type : 'select' }

  var cardEditors = {}
  for(var i=2;i<17;i++) cardEditors[i] = text
  cardEditors[2] = card_type
  cardEditors[4] = date
  cardEditors[5] = date
  cardEditors[13] = card_status
  var cards = initTable('#cards','/card',$.extend( { editors: cardEditors },arg_base))

  $('#cards_filter input').autocomplete({
   source: [  'разрешен','запрещен','администратор','кассир','пропуск' ],
   minLength: 0
  }) 

  var ticketEditors = {}
  for(var i = 2;i<12;i++) ticketEditors[i] = text
  var tickets = initTable('#tickets','/ticket',{'sort' : true,'filter':true })

  var tariff_type = { type: 'select', data: { '1':'Фиксированный', '2':'Переменный', '3' : 'Разовый' }, width: "40px" }
  var tariff_interval = { type: 'select', data: { '1':'час', '2':'сутки', '3':'месяц' }, width: "20px" }
  var tariff_cost = { type: 'costpicker', isExtended: function(row) {
    var result = false
    row.find('td:nth-child(3)').each(function(idx,cell) { if( $(cell).text() == 'Переменный' ) result = true; })    
    return result
  } }
  var tariffEditors = { 2: text, 3: tariff_type, 4: tariff_interval, 5: tariff_cost, 6: time, 7: text, 8: text }
  var tariff = initTable('#tariffs','/tariff',$.extend( { editors: tariffEditors },arg_base))
  
  var configEditors = { 1: text, 2: text}
  var config = initTable('#config','/config',{ editors: configEditors, 'save-changes' : true, 'cancel-changes' : true })


  var events = initTable('#events','/events',{})
  var payment = initTable('#payment','/payment',{})

  setInterval(function() {
    if( $('#userlevel').text() == 'Пользователь' ) { 
      gstatus.fnReloadAjax()
      lstatus.fnReloadAjax()
      tickets.fnReloadAjax()
      cards.fnReloadAjax()
      tariff.fnReloadAjax()
      config.fnReloadAjax()
      payment.fnReloadAjax()
      events.fnReloadAjax()
    } else {
      sendCommand('/gstatus/update',{},function() {
        gstatus.fnReloadAjax()
      }) 

      sendCommand('/lstatus/update',{},function() {
        lstatus.fnReloadAjax()
      })
   
      sendCommand('/ticket/update',{},function() {
        tickets.fnReloadAjax()
      })

      sendCommand('/events/update',{},function() {
        events.fnReloadAjax()
      })
      sendCommand('/payment/update',{},function() {
        payment.fnReloadAjax()
      })
    }
  },5000)

})
