$.template( "costTemplate", '\
<tr style="background-color: ${color}">\
<td style="text-align: center">${hour}:00</td><td>${parseInt(hour)+1}:00</td>\
<td style="text-align: center"><input id="hour${hour}" size="12" type="text" value="${value}"></td></tr>' );

$.editable.addInputType( 'costpicker', {

    /* create input element */
    element: function( settings, original ) {
      var form = $( this ),
          input = $( '<input size="30" />' );
      input.attr( 'autocomplete','off' );
      form.append( input );
      return input;
    },
    
    /* show custom dialog to edit costs of each hour */
    plugin: function( settings, original ) {
      var form = this,
          input = form.find( "input" );

			//check, is user requires extended edit dialog, otherwise fallback to simple text edit
			if('isExtended' in settings) {
				if(!settings.isExtended(form.parent().parent())) return
			}

      // Don't cancel inline editing onblur when clicking inside dialog
			settings.onblur = 'nothing'

			var costs = input.val().split(' ')
			var hours = []
			for(var i = 0;i<24; i++) hours.push({color: i % 2 ? 'white' : '#E2E4FF',hour: i, value: i.toString() in costs ? costs[i] : 0})

			var table = $('<table cellpadding="0" style="margin: 5px;border-collapse: collapse">\
										 <tr style="border: 1px solid #D3D3D3;color: #555555;background-color: #E7E7E7">\
										 <th colspan="2">Тарифный интервал</th><th>Стоимость</th></tr></table>')
			$.tmpl( "costTemplate", hours ).appendTo(table)

      table.dialog({
				modal: true,
				width: 240,
        close: function() {
					original.reset(form)
				},
				buttons: {
					"Подтвердить": function() {
            var result = []
						//gather information from  all input element inside dialog in their respective order...
            table.find('input').each(function(idx,element) { result.push(element.value) })
            //... and merge them to our main input element
            input.val(result.join(' '))
            form.submit()
						$( this ).dialog( "close" )
					},
					"Отменить": function() {
						original.reset(form)
						$( this ).dialog( "close" )
					}
				}
      })
    }
} );
