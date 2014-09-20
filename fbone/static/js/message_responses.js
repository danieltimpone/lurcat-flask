function processMessages(msgs){
	messages={}
	messages['positive-messages']=[]
	messages['negative-messages'] = []
	messages['yescount'] = 0
	messages['nocount'] = 0

	msgs.forEach(function(message){
		if(message.response === true){
			messages['yescount']++;
			if(message.text != ''){
				messages['positive-messages'].push(message);
			}
		}
		else if(message.response === false){
			messages['nocount']++;
			if(message.text != ''){

				messages['negative-messages'].push(message);
			}
		}
		else{
			if(message.text != ''){
				messages['positive-messages'].push(message);
			}
		}

	})
	return messages;

}


function showResponses(id){
	
	$.getJSON('/message/responses/'+id, {
       }, function(messages) {
       	messages = processMessages(messages);
       	var container = $('#message-responses');
       	container.html('');
       	var div = $("<div class='container response-stats'></div>");
       	div.html("<div class='span2 offset1'><i class='icon-thumbs-up'></i>"+messages['yescount']+"</div><div class='span2'><i class='icon-thumbs-down'></i>"+messages['nocount']+"</div>");
       	container.append(div);
       	var table =$('<table class="table table-condensed"></table>');
       	messages['positive-messages'].forEach(function(message){
   		       	var tr = $("<tr class='success'></tr>");
   		       	var td = $("<td></td>")
   		       	td.html(message.text);
   		       	tr.append(td);
   		       	table.append(tr)
       	})

       	messages['negative-messages'].forEach(function(message){
   		       	var tr = $("<tr class='error'>");
  		       	var td = $("<td></td>")
   		       	td.html(message.text);
   		       	tr.append(td);
   		       	table.append(tr)
       	})
       	container.append(table);


       });
	$('#myModal').modal()



}
