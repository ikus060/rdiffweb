// rdiffweb, A web interface to rdiff-backup repositories
// Copyright (C) 2012-2021 rdiffweb contributors
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
		localStorage['pref.' + key] = value;
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

/**
 * Convert a value to a date.
 */
var DATE_PATTERN = /^(\d\d\d\d)(\-)?(\d\d)(\-)?(\d\d)$/i;
function toDate(n) {
    var matches, year, month, day;
    if (typeof n === "number") {
        n = new Date(n * 1000); // epoch
    } else if ((matches = n.match(DATE_PATTERN))) {
        year = parseInt(matches[1], 10);
        month = parseInt(matches[3], 10) - 1;
        day = parseInt(matches[5], 10);
        return new Date(year, month, day);
    } else { // str
        n = isNaN(n) ? new Date(n) : new Date(parseInt(n) * 1000 );
    }
    return n;
  }

/**
 * Add form validation where applicable.
 */
jQuery.validator.addMethod("equalValue", function(value, element, parameters) {
    return value == parameters;
}, "Enter the same value.");

$(document).ready(function() {

// Table sorting
$("table.sortable thead th.sortable").each(function(){
	
    // Get reference to this column
	var column = $(this);
	var columnIndex = column.index();
	var direction = 'asc';
	var table = column.parents("table");

	// Create sorting function
	fctsort = function() {
		var	comparator = Comparators.naturalComparator;
		if(column.attr("data-type")=="int"){
			comparator = Comparators.naturalIntComparator;
		} else if(column.attr("data-type")=="str"){
			comparator = Comparators.naturalStrComparator;
		} else if(column.attr("data-type")=="dir"){
			comparator = function(a, b){
				a = String(a); b = String(b);
				aIsDir = a.indexOf("dir-");
				bIsDir = b.indexOf("dir-");
				if(aIsDir<bIsDir) return 1;
				if(aIsDir>bIsDir) return -1;
				if(a > b) return 1;
			    if(a < b) return -1;
			    return 0;
			};
		}
		table.find("tbody").sortChildren(function(a, b) {
		    return direction=='asc' ? comparator(a,b) : -comparator(a,b);
        }, function(child){
			var node = $(child.children[columnIndex]);
			var data = node.attr("data-value");
			if(data === null){
				data = $.text([node]);
			}
			if(!isNaN(parseInt(data))){
				return parseInt(data);
			}
			return data.toLowerCase();
	    });
	    
	    // Remove desc and asc from all columns
	    table.find("thead th.sortable").removeClass('desc asc');
	    column.addClass(direction);
	    if(table.attr('id')!=="" && column.attr('id')!=="") {
	    	setPrefValue(table.attr('id') + '.sortingcolumn', column.attr('id'));
	    	setPrefValue(table.attr('id') + '.sortingdirection', direction);
	    }
	    
	    // Inverse direction for next execution
	    direction = direction=='asc' ? 'desc' : 'asc';
	    
	};
	
	// Create link
	column.wrapInner('<a href="#"/>');
	
	// Add click event
	column.children('a').click(fctsort);
	
	// Apply user preference
	if(getPrefValue(table.attr('id') + '.sortingcolumn', '') == column.attr('id')) {
		direction = getPrefValue(table.attr('id') + '.sortingdirection', direction);
		if(direction == 'asc'){
			fctsort();
		} else {
			direction = 'desc';
			fctsort();
		}
	}
});

/**
 * Handle flexible Ajax form submit.
 */
$('form[data-async]').on('submit', function(event) {
    var $form = $(this);
    var $target = $($form.attr('data-target'));
    $.ajax({
    	headers: { 
            Accept: "text/plain; charset=utf-8",
        },
        type: $form.attr('method'),
        url: $form.attr('action'),
        data: $form.serialize(),
        success: function(data, status) {
            $target.html('<i class="icon-ok text-success"></i> ' + data);
        },
        error: function(data, status, e) {
        	$target.html('<i class="icon-attention text-danger"></i> ' + data.responseText);
        },
    });
    event.preventDefault();
})

/**
 * Handle local datetime using <time datetime="value"></time>. 
 * Uses the value of `datetime` to converted it into local timezone. 
 * Class `js-date` could be used to only display the date portion. e.g.: 2021-05-28
 * Class `js-datetime` could be used to display the date and time portion e.g.: 2021-05-28 1:04pm
 * Class `js-time` could be used to display the time portion. e.g.: 1:04 pm
 */
$('time[datetime]').each(function(){
  var t = $(this);
  var d = toDate(t.attr('datetime'));
  if(t.hasClass("js-date")) {
    t.attr('title', d.toLocaleDateString());
    t.text(d.toLocaleDateString());
  } else if($(this).hasClass("js-datetime")) {
    t.attr('title', d.toLocaleString());
    t.text(d.toLocaleString());
  } else if($(this).hasClass("js-time")) {
    t.attr('title', d.toLocaleString());
    t.text(d.toLocaleTimeString());
  } else {
    t.attr('title', d.toLocaleString());
  }
})

});
