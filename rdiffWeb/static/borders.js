
function addCornerElem(oParentElem, iNum)
{
   var oElem = document.createElement('b');
   oElem.className = 'xb' + iNum + (iNum > 1 ? " roundedBorderBackground" : "");
   oParentElem.appendChild(oElem);
}

function makeDivRounded(oDiv)
{
   var oDivParent = oDiv.parentNode;
   
   // Stick the container in where the div was, and yank
   // out the div temporarily (we'll reattach it later.)
   var oContainingTable = document.createElement('table');
   oContainingTable.className = 'roundedBorderContainer';
   oDivParent.insertBefore(oContainingTable, oDiv);
   oDiv.parentNode.removeChild(oDiv);
   
   var oTBody = document.createElement('tbody');
   var oTR = document.createElement('tr');
   var oTD = document.createElement('td');
   oContainingTable.appendChild(oTBody);
   oTBody.appendChild(oTR);
   oTR.appendChild(oTD);
   
   var oOuterBorder = document.createElement('div');
   oTD.appendChild(oOuterBorder)
   oOuterBorder.className = 'roundedBorderOuter';
   
   var oTop = document.createElement('b');
   oTop.className = 'xtop'
   oOuterBorder.appendChild(oTop);
   for (var i = 1; i < 5; i++)
      addCornerElem(oTop, i);
   var oInnerElem = document.createElement('div');
   oInnerElem.className = 'roundedBorderInner roundedBorderBackground';
   oOuterBorder.appendChild(oInnerElem);
   oInnerElem.appendChild(oDiv);
   
   var oBottom = document.createElement('b');
   oBottom.className = 'xbottom';
   oOuterBorder.appendChild(oBottom);
   for (var i = 4; i > 0; i--)
      addCornerElem(oBottom, i);
}

function roundDivBorders()
{
   var reBorderDivName = /roundedBorderContents/;
   var aDivs = document.getElementsByTagName('DIV');
   for (var i = aDivs.length-1; i >= 0; i--)
   {
      if (reBorderDivName.test(aDivs[i].className))
      {
         makeDivRounded(aDivs[i]);
      }
   }
}

addOnLoadEvent(function()
{
   roundDivBorders();
});
