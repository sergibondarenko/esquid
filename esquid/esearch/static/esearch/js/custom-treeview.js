$(function() {

$.getJSON("/static/esearch/json/test_menu.json", function(menu_data){
	console.log("Success: Menu json will be used.");
})
.done(function(menu_data){
	var initSelectableTree = function() {
	  return $('#treeview-selectable').treeview({
	  	color: "#428bca",
		data: JSON.stringify(menu_data),
	    multiSelect: $('#chk-select-multi').is(':checked'),
	    onNodeSelected: function(event, node) {
	      $('#selectable-output').prepend('<p>' + node.text + ' was selected</p>');
	
		  // Send calls from menu to backend
		  $.ajax({
			type: 'POST',
			url: 'postmenu/',
			data: {
				//msg: 'Hello my friend!',
				msg: node.text,
			},
			success: function(response){
				$('#selectable-output').html(response);
				console.log(response);
				//console.log('Success!');
			},
			error: function(response){
				$('#selectable-output').html('Error (ajax post): Unable to receive data from server.');
			}
		  }); // ajax post
	    },
	    onNodeUnselected: function (event, node) {
	      $('#selectable-output').prepend('<p>' + node.text + ' was unselected</p>');
	    }
	  });
	};
	initSelectableTree();

})
.fail(function(){
	console.log("Fail: Menu json was not used.");
})
.always(function(){
	console.log("Complete: Finished taking menu.");
});


//var $selectableTree = initSelectableTree();

//// Form functionality
//var findSelectableNodes = function() {
//  return $selectableTree.treeview('search', [ $('#input-select-node').val(), { ignoreCase: false, exactMatch: false } ]);
//};
//var selectableNodes = findSelectableNodes();
//
//$('#chk-select-multi:checkbox').on('change', function () {
//  console.log('multi-select change');
//  $selectableTree = initSelectableTree();
//  selectableNodes = findSelectableNodes();          
//});

//// Select/unselect/toggle nodes
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

});
