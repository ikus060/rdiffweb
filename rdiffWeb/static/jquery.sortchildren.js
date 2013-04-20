/**
 * jQuery.fn.sortElements
 * --------------
 * @author James Padolsey (http://james.padolsey.com)
 * @version 0.11
 * @updated 18-MAR-2010
 * --------------
 * @param Function comparator:
 *   Exactly the same behaviour as [1,2,3].sort(comparator)
 *   
 * @param Function getSortable
 *   A function that should return the element that is
 *   to be sorted. The comparator will run on the
 *   current collection, but you may want the actual
 *   resulting sort to occur on a parent or another
 *   associated element.
 *   
 *   E.g. $('td').sortElements(comparator, function(){
 *      return this.parentNode; 
 *   })
 *   
 *   The <td>'s parent (<tr>) will be sorted instead
 *   of the <td> itself.
 */
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