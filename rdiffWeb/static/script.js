$(document).ready(function() {
	
	
// Tooltip
$("[title]").tooltip({ position: "bottom center", relative:true});

// History error
$(".multiline-error").hide();
$(".history-error").click(function(){
	$(this).parent('tr').next().toggle();
});

// Overlay
$(".overlay-link[href]").each(function(){
	targetId = $(this).attr('href');
	$(this).attr('href','#');
	targetId = targetId.replace(/#/g,'');
	targetEle = document.getElementById(targetId);
	$(this).overlay({fixed:false,top:"center",left:"center",target:targetEle});
})

// Table sorting
$("table.sortable thead th.sortable").css('cursor', 'pointer');
$("table.sortable thead th.sortable").each(function(){
	
    // Get reference to this column
	var column = $(this);
	var columnIndex = column.index();
	var inverse = false;
	var table = column.parents("table");

	// Attach click event to column
	column.click(function(){
		
		// On click sort elements
	    table.find("tbody td").filter(function(){
	        
	        return $(this).index() === columnIndex;
	        
	    }).sortElements(function(a, b){
	        
	        var aData = $([a]).attr("data-value");
	        var bData = $([b]).attr("data-value");
	        if(aData == null || bData ==null){
	        	aData = $.text([a])
	        	bData = $.text([b])
	        } 
	        if(!isNaN(parseInt(aData)) && !isNaN(parseInt(bData))){
	        	aData = parseInt(aData)
	        	bData = parseInt(bData)
	        } else {
	        	aData = aData.toLowerCase()
	        	bData = bData.toLowerCase()
	        }
	        return aData > bData ? inverse ? -1 : 1 : inverse ? 1 : -1;
	        
	    }, function(){
	        
	        // parentNode is the element we want to move
	        return this.parentNode;
	        
	    });
	    
	    inverse = !inverse;
	    
	});
});

// Focus on username form field
$("#username").focus();

});



