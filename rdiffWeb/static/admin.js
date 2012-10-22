
function onEditUser(event)
{
   event = event || window.event;
   var elem = event.target || event.srcElement;
   
   /* jump to the next row */
   var clickRow = elem.parentNode.parentNode;
   var row = clickRow;
   do row = row.nextSibling;
   while (row && (!row.tagName || row.tagName !== "TR"));
   if (!row)
      return;

   if (row.className === "notEditingRow")
   {
      row.className = "editingRow"
      clickRow.className = "userEditingRow";
   }
   else
   {
      row.className = "notEditingRow";
      clickRow.className = "userNotEditingRow";
   }
}


addOnLoadEvent(function()
{
   var aLinks = document.getElementsByTagName("A");
   for (var i = 0; i < aLinks.length; i++)
   {
      if (aLinks[i].className === "editLink")
         aLinks[i].onclick = onEditUser;
   }
});