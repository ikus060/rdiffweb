var fg_curPopup;
var fg_curTimer;
function showPopup(div)
{
   if (fg_curPopup && fg_curPopup != div)
      hidePopup();
   else
      cancelHidePopup();
   fg_curPopup = div;
   fg_curPopup.style.display = 'block';
   fg_curPopup.onmouseover = cancelHidePopup;
   fg_curPopup.onmouseout = delayHidePopup;
   fg_curPopup.style.marginTop = "0px";

   // calculate the top relative to the body
   var top = 0;
   var curElem = fg_curPopup;
   while (curElem)
   {
      top += curElem.offsetTop || 0;
      curElem = curElem.offsetParent;
   }

   // how far does the flyout extend beyond the screen?
   // (the top of the flyout should not extend beyond the top of the screen)
   var offscreenDistanceBottom = (top + fg_curPopup.offsetHeight) - (document.body.scrollTop + document.body.clientHeight);
   offscreenDistanceBottom = Math.min(offscreenDistanceBottom, top - document.body.scrollTop);
   if (offscreenDistanceBottom > 0)
      fg_curPopup.style.marginTop = "-" + offscreenDistanceBottom + "px";
}

function hidePopup()
{
   if (fg_curPopup)
   {
      fg_curPopup.style.display = 'none';
      fg_curPopup = null;
      cancelHidePopup()
   }
}

function cancelHidePopup()
{
   if (fg_curTimer)
   {
      window.clearTimeout(fg_curTimer);
      fg_curTimer = null;
   }
}

function delayHidePopup()
{
   cancelHidePopup();
   fg_curTimer = window.setTimeout(hidePopup, 500);
}

function onTableMouseOver(event)
{
   event = event || window.event;
   var elem = event.target || event.srcElement;
   if (elem.className === "PopupLink")
   {
      /* jump to the next cell */
      var cell = elem.parentNode;
      do cell = cell.nextSibling;
      while (cell && (!cell.tagName || cell.tagName !== "TD"));
      if (!cell)
         return;

      /* find first DIV child */
      var div = cell.firstChild;
      while (div && (typeof div.tagName == "undefined" || div.tagName != "DIV"))
         div = div.nextSibling;

      if (div)
         showPopup(div);
   }
}

function onTableMouseOut(event)
{
   if (!fg_curPopup) return;

   event = event || window.event;
   var elem = event.target || event.srcElement;
   while (elem)
   {
      if (elem.className === "PopupLink")
         delayHidePopup();
      elem = elem.parentNode;
   }
}


addOnLoadEvent(function()
{
   var table = document.getElementById("PopupTable");
   if (table)
   {
      table.onmouseover = onTableMouseOver;
      table.onmouseout = onTableMouseOut;
   }
});
