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

function hideTabByName(name) {
  var tab_idx = $('#tabs ul li').index($('#tabs ul a[href="#' + name + '"]').parent())
  $('#tabs').tabs("disable",tab_idx)
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
    editors[2] = card_type
    editors[3] = generic.text
    editors[4] = generic.date
    editors[5] = generic.date
    for(var i=6;i<15;i++) editors[i] = generic.text
    editors[15] = card_status
    editors[16] = generic.tariff    
    var cards = initTable('#cards','/card',$.extend( { editors: editors },arg_base))

    $('#cards_filter input').autocomplete({
      source: [  'разрешен','запрещен','администратор','кассир','пропуск' ],
      minLength: 0
    })

    return cards
  },

  tickets: function(arg_base,generic) {
    return initTable('#tickets', '/ticket', arg_base)
  },

  tariffs: function(arg_base,generic_editors) {
    var text = generic_editors.text
    var tariff_type = { type: 'select',
                        data: { '1':'Фиксированный', '2':'Переменный', '3' : 'Разовый', '4' : 'Новый тариф', '5':'Продоплаченный' }, 
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
    return initTable('#payment','/payment',arg_base)
  },

  terminals: function(arg_base,generic) {
    var editors = { 2: generic.text, 3: generic.text }
    return initTable('#terminals','/terminal',$.extend({editors: editors},arg_base,{ delete: 'replace' }))
  },

  users: function(arg_base,generic) {
    if(!arg_base.admin) {
      hideTabByName('tab-user')
      return;
    }

    var user_level = { type: 'select', data: { '1' : 'Пользователь', '2' : 'Администратор' } }
    var editors = { 2: generic.text, 3: generic.text, 4: user_level }
    return initTable('#users','/user',$.extend( { editors: editors },arg_base))
  },

  reports: function(arg_base,generic) {
    if(!arg_base.admin) hideTabByName('tab-reports')
  }
}

$(document).ready(function() {
  var admin = $('#userlevel').text() == 'Администратор'
  $('#userinfo').addClass({true: 'admin', false: 'user'}[admin])

  $('#tabs').tabs()

  //allows jEditable to submit select element when its value changes
  $('select').live('change', function() {
   $(this).parent().submit()
  })

  //allows jEditable to submit select element without confirm button, only using  <enter> key
  $('select').live('keydown', function (event) {
    if(event.keyCode == 13) $(this).parent().submit();
  })
  
  var arg_base = { 'admin'          : admin,
                   'jEditable'      : admin,
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
           users:    true,
           reports:  true
  },function(key,value) {
    if(value) tables[key] = init[key](arg_base,generic_editors)
  })

  /*setInterval(function() {
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
  },10000)*/

})