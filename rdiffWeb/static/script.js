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
	$(".overlay-link[rel]").each(function(){
		targetId = $(this).attr('rel');
		$(this).removeAttr('rel');
		targetId = targetId.replace(/#/g,'');
		targetEle = document.getElementById(targetId);
		$(this).overlay({fixed:false,top:"center",left:"center",target:targetEle});
	}) 
});