$(function() {  // main() function, runs at start


// Send vars from menu to backend
var sendVarsToBackend = function(vars, datatype, url, callback){
	$.ajax({
	  type: 'POST',
	  dataType: datatype,
	  url: url,
	  data: {
	  	msg: vars,
	  },
	  success: function(data){
		callback(data);
	  	console.log('Successful response from backend!');
		//console.log(data);
	  },
	  error: function(data){
	  	console.log('Error (ajax post): Unable to receive data from server.');
	  }
	}); // ajax post
}


// Table builder
var buildRecordsTable = function(json_objs, table_name){

	// Find _source dictionary keys
	var hit = json_objs.hits.hits[0];
	var hr_num = Object.keys(hit._source).length; 
	var hr_arr = Object.keys(hit._source); 

	// Loop through _source keys array and append them to <th>
	var tr = $('<tr>');
	for(var i in hr_arr){
		tr.append('<th>' + hr_arr[i] + '</th>');
	}
	$(table_name).append(tr);

	// Loop through all received documents
	$.each(json_objs.hits.hits, function(key, value){
		hit = value;
		tr = $('<tr>');	// Create a row

		// Loop through all elements of the _source dictionary
		for(var i in hit._source){
			var src_arr = hit._source
			tr.append('<td>' + src_arr[i] + '</td>');	// Create a cell and append it to the row created above
		}
		$(table_name).append(tr);	// Append the row to the table
	});
}


// Headers table builder
var buildHeaderRecordsTable = function(json_objs, div_id, rec_header){
	// Loop through all received documents
	$.each(json_objs.hits.hits, function(key, value){
		hit = value;
		tr = $('<div>');	// Create a row

		// Loop through all elements of the _source dictionary
		for(var i in hit._source){
			var src_arr = hit._source
			if(i == rec_header)
				// Create a cell and append it to the row created above
				tr.append('<p><a href="#" id="record_header">' + src_arr[i] + '</a></p>');	
		}
		$(div_id).append(tr);	// Append the row to the table
	});
}


// Init menu, turn on menu node event listening
var initSelectableTree = function() {
  return $('#treeview-selectable').treeview({
  	color: "#428bca",
	data: menuItems,
    multiSelect: $('#chk-select-multi').is(':checked'),
    onNodeSelected: function(event, node) {
	
	    // Log query to textarea
		function log_query(message){
			var query_log = $('#selectable-output').val();
			query_log += message;
			$('#selectable-output').val('');
			$('#selectable-output').val(query_log);
		}

		// Autocomplete search field
		$('#input-field-search').autocomplete({
			source: function(request, response){
				sendVarsToBackend(node.parents + "." + node.text + "=" + request.term,
						'json', 'livesearch/', response)	// Search word in a specific field of a document in Elastic
			},
			select: function(event, ui){	// Add search query to textarea on select event
				log_query("(" + node.parents + "." + node.text + "=" + ui.item.label + ")");
			},
			delay: 1000,
			autoFocus: true,
			minLength: 1
		});

    },
    onNodeUnselected: function (event, node) {
      //$('#selectable-output').append('<p>' + node.text + ' was unselected</p>');
	  console.log(node.text);
    }
  });
};


// Build menu
var menuItems = {};
var buildMenu = function(){
	$.getJSON("/static/esearch/json/test_menu.json", function(menu_data){
		//console.log("Success: Menu json will be used.");
	})
	.done(function(menu_data){
		menuItems = JSON.stringify(menu_data);
		//console.log(menuItems);
		initSelectableTree()
	})
	.fail(function(){
		console.log("Fail: Menu json was not used.");
	})
	.always(function(){
		//console.log("Complete: Finished taking menu.");
	});
};
buildMenu();


var $selectableTree = initSelectableTree();

// Form functionality to search for nodes in menu
var findSelectableNodes = function() {
	return $selectableTree.treeview('search', [ $('#input-select-node').val(), { ignoreCase: false, exactMatch: false } ]);
};
var selectableNodes = findSelectableNodes();

// Multiselect functionality of menu
$('#chk-select-multi:checkbox').on('change', function () {
	console.log('multi-select change');
	$selectableTree = initSelectableTree();
	selectableNodes = findSelectableNodes();          
});

// Select/unselect/toggle nodes
$('#input-select-node').on('keyup', function (e) {
  selectableNodes = findSelectableNodes();
  $('.select-node').prop('disabled', !(selectableNodes.length >= 1));
});

//$('#btn-select-node.select-node').on('click', function (e) {
//  $selectableTree.treeview('selectNode', [ selectableNodes, { silent: $('#chk-select-silent').is(':checked') }]);
//});
//
//$('#btn-unselect-node.select-node').on('click', function (e) {
//  $selectableTree.treeview('unselectNode', [ selectableNodes, { silent: $('#chk-select-silent').is(':checked') }]);
//});
//
//$('#btn-toggle-selected.select-node').on('click', function (e) {
//  $selectableTree.treeview('toggleNodeSelected', [ selectableNodes, { silent: $('#chk-select-silent').is(':checked') }]);
//});

// Clear query field
$('#btn-clear-log-query-field.logic-btn').on('click', function (e) {
	$('#selectable-output').val('');
});


// AND - MUST
$('#btn-must.logic-btn').on('click', function (e) {
	var query_log = $('#selectable-output').val();
	query_log += ' MUST ';
	$('#selectable-output').val('');
	$('#selectable-output').val(query_log);
});


// OR - SHOULD
$('#btn-should.logic-btn').on('click', function (e) {
	var query_log = $('#selectable-output').val();
	query_log += ' SHOULD ';
	$('#selectable-output').val('');
	$('#selectable-output').val(query_log);
});


// NOT - MUST NOT
$('#btn-mustnot.logic-btn').on('click', function (e) {
	var query_log = $('#selectable-output').val();
	query_log += ' MUST_NOT ';
	$('#selectable-output').val('');
	$('#selectable-output').val(query_log);
});


// SEARCH button. Sends search query to server. 
$('#btn-search.logic-btn').on('click', function (e) {
	var search_query = $('#selectable-output').val();

	sendVarsToBackend(search_query, 'html', 'postmenu/', function(result){
		$('#output-free-search').html(result);
		console.log(result);
	});
});


// Press "Enter" key to search. Free search in Elasticsearch
$('#input-field-search').keypress(function (e) {
	if(e.which == 13){
		e.preventDefault();
		var search_query = $('#input-field-search').val();
		var free_search_check = $('#chk-select-freesearch').is(':checked');

		// Verify if Free Search is checked
		if(free_search_check){
			console.log(search_query);
			sendVarsToBackend(search_query, 'json', 'freesearch/', function(result){
				$('#records_table').empty();	// Empty table
				buildRecordsTable(result, '#records_table:last');
	  			//$('#output-free-search').html(result);
				console.log(result);
			});
		} else {
			var choice1 = 'Select a menu node to search it.';
		   	var choice2 = 'Or check "Free Search" to search in free mode.';	
			$('#output-free-search').html('<p>'+ choice1 +' '+ choice2 +'</p>');	
		}
	}
});


$('record_header').click(function(e){
	console.log('clicked');
});


//// Get first Elasticsearch records from server and display them on index.html
//sendVarsToBackend('', 'json', 'search_all/', function(result){
//	//$('#output-free-search').html(result);
//	buildRecordsTable(result, '#records_table:last');
//	//buildHeaderRecordsTable(result, '#output-free-search', 'text_entry');
//});


}); // End of main func
    
