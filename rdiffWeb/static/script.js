// menubar
$(document).ready(function() {
	var closing = undefined;
	var closingInterval = undefined;
	function doClose()
	{
	    $(closing).children("ul").stop(true, true).slideUp(10);
	    closing = undefined;
	    closingInterval = undefined;
	}
	
	$(".revision").children("ul").hide();
	$(".revision").hover(function() {
	    if (closing)
	    {
	        clearTimeout(closingInterval);
	        if (closing != this)
	        {
	            doClose();
	        }
	        else
	        {
	            closing = undefined;
	            closingInterval = undefined;
	        }
	    }
	    $(this).children("ul").stop(true, true).slideDown(10);
	}, function() {
	    closing = this;
	    closingInterval = setTimeout(doClose, 100); 
	});
});

// Tooltip
$(document).ready(function() {
	$("[title]").tooltip({ position: "bottom center", relative:true});
});

// History error
$(document).ready(function() {
	$(".multiline-error").hide();
	$(".history-error").click(function(){
		$(this).parent('tr').next().toggle();
	});
});

// Overlay
$(document).ready(function() {
	$(".overlay-link[rel]").overlay({fixed:false,top:"center",left:"center"});
});