// rdiffWeb, A web interface to rdiff-backup repositories
// Copyright (C) 2012 rdiffWeb contributors
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
	fctsort = function(){
		
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
	    if(table.attr('id')!="" && column.attr('id')!="") {
	    	setPrefValue(table.attr('id') + '.sortingcolumn', column.attr('id'));
	    	setPrefValue(table.attr('id') + '.sortingdirection', inverse ? 'desc': 'asc');
	    }
	    
	};
	column.click(fctsort);
	
	// Check preference
	if(getPrefValue(table.attr('id') + '.sortingcolumn', '') == column.attr('id')) {
		var direction = getPrefValue(table.attr('id') + '.sortingdirection', 'asc');
		if(direction == 'asc'){
			inverse = true;
			fctsort();
		} else if (direction == 'desc') {
			inverse = false;
			fctsort();
		}
	}
	
});

// Focus on username form field
$("#username").focus();

});

/**
 * Save a preference data into the local storage if available.
 * 
 * @param {Object} key
 * 		the preference key
 * @param {Object} value
 * 		the preference value
 */
function setPrefValue(key, value) {
	if(typeof(localStorage)!=="undefined") {
		localStorage['pref.' + key] = value
	}
}

/**
 * Get the preference data from the local storage.
 * @param {Object} key
 * 		the preference key
 * @param {Object} defaultValue
 * 		the default value if the value is not available in the local storage
 */
function getPrefValue(key, defaultValue) {
	if(typeof(localStorage)!=="undefined") {
		if(typeof(localStorage['pref.' + key])==="string") {
			return localStorage['pref.' + key];
		}
	}
	return defaultValue;
}