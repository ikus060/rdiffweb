
function setText(parent, text)
{
   parent.innerHTML = "";
   parent.appendChild(document.createTextNode(text));
}

function getPassword()
{
   return document.getElementById("rootpassword").value;
}

function handleResponse(responseError, errorElem, nextStepElem)
{
   if (responseError)
      setText(errorElem, responseError);
   else
   {
      setText(errorElem, "");
      nextStepElem.style.display = 'block';
   }
}

function handleRequestButton(request, errorElem, nextStepElem)
{
   function onSuccess(str)
   {
      var response = eval("("+str+")");
      handleResponse(response.error, errorElem, nextStepElem);
   }
   function onFailure()
   {
      handleResponse("Unable to communicate with server.", errorElem, nextStepElem);
   }
   ajax.postUrl("/setup/ajax", JSON.stringify(request), onSuccess, onFailure);
}

function handleAdmin()
{
   var errorElem = document.getElementById("adminRootError");
   var nextStepElem = document.getElementById("adminRoot");
   
   var adminUsername = document.getElementById("adminUsername").value;
   var adminPassword = document.getElementById("adminPassword").value;
   var adminConfirmPassword = document.getElementById("adminConfirmPassword").value;
   
   var request = {
      "rootPassword": getPassword(),
      "adminUsername": adminUsername,
      "adminPassword": adminPassword,
      "adminConfirmPassword": adminConfirmPassword
   };
   handleRequestButton(request, errorElem, nextStepElem);
}

function handleAdminRoot()
{
   var errorElem = document.getElementById("adminError");
   var nextStepElem = document.getElementById("SetupCompleteDiv");
   
   var adminRoot = document.getElementById("adminRoot").value;
   
   var request = {
      "rootPassword": getPassword(),
      "adminRoot": adminRoot
   };
   handleRequestButton(request, errorElem, nextStepElem);
}

function handleRootPassword()
{
   var errorElem = document.getElementById("rootpassworderror");
   var nextStepElem = document.getElementById("adminSetup");
   var request = {"rootPassword": getPassword()};
   handleRequestButton(request, errorElem, nextStepElem);
}

function initEvents()
{
   document.getElementById("rootpasswordbtn").onclick = handleRootPassword;
   document.getElementById("adminbtn").onclick = handleAdmin;
   document.getElementById("adminRootBtn").onclick = handleAdminRoot;
}

addOnLoadEvent(initEvents)
