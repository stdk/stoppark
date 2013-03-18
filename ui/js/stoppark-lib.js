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
      var position = table.fnGetPosition(this)
      var result = {
        row: position[0],
        col: position[1],
        id: table.fnGetData(position[0],0)
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

    function update() {
      if(args.serverSide) {
       table.fnDraw(false)
      } else {
       table.fnReloadAjax(null,null,true)
      }
    }

    var draw_callback = function() {
      console.log(selector)
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
            var e = $(element)
            var value = e.text()
            if(value in editor.data) {
              //e.text(editor.data[value])
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
                data: { 
                  row: row,
                  id: table.fnGetData(row,0)
                },
                success: function() {
                  // instead of table redraw we can just locally delete this row
                  // in response to successful delete from server
                  table.fnDeleteRow(row)
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
        iDisplayLength: 25,
        bPaginate: true,
        bLengthChange: false,
        bFilter: 'filter' in args && args.filter,
        bSort: 'sort' in args && args.sort,
        bInfo: true,
        bAutoWidth: false,
        bProcessing: true,
        bServerSide: args.serverSide,
        bJQueryUI: true,
        sAjaxSource: path + '/data',
        sPaginationType: 'full_numbers',
        aaSorting: [],
        bDeferRender: true,
        fnDrawCallback: draw_callback,
        //sDom: 'R<"H"lfr>t<"F"ip>',
        "fnServerData": function ( sSource, aoData, fnCallback ) {
          $.getJSON( sSource, aoData, function (json) {
            fnCallback(json);
          }).error(function(jqXHR, statusText, errorThrown) {
            //when data request failed with to 403 Forbidden status
            //we should try to authenticate user once more
            if(jqXHR.status == 403) {
              window.location += 'auth'
            }            
          });
        }
  });

  if('add' in args && args.add) {
    $(selector+'-row-add').button().click(function() {
      $.ajax({
        type: "POST",
        url: path + "/add",
        contentType: 'application/x-www-form-urlencoded',
        data: {},
        success: update,
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
        success: update,
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
        success: update,
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