function addOnLoadEvent(func)
{
   var oldOnload = window.onload;
   if (typeof(window.onload) !== 'function')
      window.onload = func;
   else
   {
      window.onload = function()
      {
         if (oldOnload)
            oldOnload();
         func();
      }
   }
}