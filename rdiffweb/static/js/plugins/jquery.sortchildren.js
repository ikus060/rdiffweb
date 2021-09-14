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

jQuery.fn.sortChildren = (function(){
    
    return function(comparator, transformer) {
        
        // Run the sort opperation
        //var start = window.performance.webkitNow();
        
        var children = this.children();
        	
    	// Create a buffered view on the node and it's transformed data
    	var Entry = function(node, value){
    		this.node = node;
    		this.value = value;
    	}
    	var transformedChildren = new Array(children.length);
    	for(var i = 0 ; i < children.length ; i++){
    		transformedChildren[i] = new Entry(children[i], transformer(children[i]));
    	}
    	TimSort.sort(transformedChildren, function(a,b){
    		// Handle undefined
    		if(a == undefined && b == undefined) return 0;
    		if(a == undefined) return 1;
    		if(b == undefined) return -1;
    		return comparator(a.value, b.value);
    	});
    	children.detach();
    	for(var i = 0 ; i < transformedChildren.length ; i++){
    	    this.append(transformedChildren[i].node);
    	}

        //var end = window.performance.webkitNow();
        //alert(end - start);
        
    };
    
})();