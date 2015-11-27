$(function() {

// Send vars from menu to backend
var sendVarsToBackend = function(vars, datatype, url, callback){
	$.ajax({
	  type: 'POST',
	  dataType: datatype,
	  url: url,
	  //url: 'postmenu/',
	  data: {
	  	//msg: 'Hello my friend!',
	  	msg: vars,
	  },
	  success: function(data){
		callback(data);
	  	console.log('Successful response from backend!');
		console.log(data);
	  },
	  error: function(data){
	  	console.log('Error (ajax post): Unable to receive data from server.');
	  }
	}); // ajax post
}

var buildRecordsTable = function(json_objs, table_name){
	// Loop through all received documents
	$.each(json_objs.hits.hits, function(key, value){
		var hit = value;
		var tr = $('<tr>');	// Create a row

		// Loop through all elements of the _source dictionary
		for(var i in hit._source){
			var src_arr = hit._source
			tr.append('<td>'+src_arr[i]+'</td>');	// Create a cell and append it to the row created above
		}
		//$('#records_table:last').append(tr);	// Append the row to the table
		$(table_name).append(tr);	// Append the row to the table
	});
}

// Init menu, turn on menu node event listening
var initSelectableTree = function() {
  return $('#treeview-selectable').treeview({
  	color: "#428bca",
	data: menuItems,
    multiSelect: $('#chk-select-multi').is(':checked'),
    onNodeSelected: function(event, node) {
	  //sendVarsToBackend(node.text, 'postmenu/', function(){
	  //	console.log(node.text);
	  //});
	
	    // Log query
		function log_query(message){
			//$('<div>').text(message).appendTo('#selectable-output');
			//$('#selectable-output').scrollTop(0);
			var query_log = $('#selectable-output').text();
			query_log += message;
			$('#selectable-output').empty();
			$('#selectable-output').append(query_log);
		}

		// Autocomplete search field
		$('#input-field-search').autocomplete({
			source: function(request, response){
				sendVarsToBackend(request.term, 'json', 'livesearch/', response)
			},
			select: function(event, ui){
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

//// Select/unselect/toggle nodes. Test functionality.
//$('#input-select-node').on('keyup', function (e) {
//  selectableNodes = findSelectableNodes();
//  $('.select-node').prop('disabled', !(selectableNodes.length >= 1));
//});
//
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
$('#btn-clear-log-query-field.select-node').on('click', function (e) {
	$('#selectable-output').empty();
});

// AND - MUST
$('#btn-must.select-node').on('click', function (e) {
	//$('<div>').text(' AND ').appendTo('#selectable-output');
	var query_log = $('#selectable-output').text();
	query_log += ' MUST ';
	$('#selectable-output').empty();
	$('#selectable-output').append(query_log);
});

// OR - SHOULD
$('#btn-should.select-node').on('click', function (e) {
	var query_log = $('#selectable-output').text();
	query_log += ' SHOULD ';
	$('#selectable-output').empty();
	$('#selectable-output').append(query_log);
});

// NOT - MUST NOT
$('#btn-mustnot.select-node').on('click', function (e) {
	var query_log = $('#selectable-output').text();
	query_log += ' MUST_NOT ';
	$('#selectable-output').empty();
	$('#selectable-output').append(query_log);
});

// SEARCH button. Sends search query to server. 
$('#btn-search.select-node').on('click', function (e) {
	var search_query = $('#selectable-output').val();

	sendVarsToBackend(search_query, 'html', 'postmenu/', function(result){
		$('#output-free-search').html(result);
	});
});


// Press "Enter" key to search. Free search in Elasticsearch
$('#input-field-search').keypress(function (e) {
	if(e.which == 13){
		e.preventDefault();
		var search_query = $('#input-field-search').val();

		sendVarsToBackend(search_query, 'html', 'postmenu/', function(result){
	  		$('#output-free-search').html(result);
			console.log(result);
		});
	}
});

// Get first Elasticsearch records from server and display them on index.html
sendVarsToBackend('', 'json', 'search_all/', function(result){
	buildRecordsTable(result, '#records_table:last');
});

//// Old search bar
//// Press "Enter" key to search. Free search in Elasticsearch
//$('#input-free-search').keypress(function (e) {
//	if(e.which == 13){
//		e.preventDefault();
//		var search_query = $('#input-free-search').val();
//
//		sendVarsToBackend(search_query, 'html', 'postmenu/', function(result){
//	  		$('#output-free-search').html(result);
//			console.log(result);
//		});
//	}
//});

});
