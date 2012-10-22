window.ajax = window.ajax || {
   getUrl: function(url, onSuccess, onFailure)
   {
      this._doUrl(url, "GET", null, onSuccess, onFailure);
   },
   
   postUrl: function(url, postString, onSuccess, onFailure)
   {
      this._doUrl(url, "POST", postString, onSuccess, onFailure);
   },
   
   _doUrl: function(url, method, postString, onSuccess, onFailure)
   {   
      function _stateChange()
      {
         if (XHR.readyState == 4)
         {
            if (XHR.status == 200)  
               onSuccess(XHR.responseText);
            else
               onFailure();
         }
      }
      
      var XHR = this._getXHR();
      XHR.onreadystatechange = _stateChange;
      XHR.open(method, url, true);
      XHR.send(postString);
   },
   
   _getXHR: function()
   {
      if (window.XMLHttpRequest)
         return new XMLHttpRequest()
      try
      {
         return new ActiveXObject("Msxml2.XMLHTTP");
      }
      catch (e)
      {
         try
         {
            return new ActiveXObject("Microsoft.XMLHTTP");
         }
         catch (e)
         {
            return null;
         }
      }
   }
}