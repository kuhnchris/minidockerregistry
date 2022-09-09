nunjucks.configure('static/views', { autoescape: true });
setInterval(loadEntries, 5000);
// get the content of url and pass that content to specified function
function getContent( url, callBackFunction ){
    // attempt to create the XMLHttpRequest and make the request
    try {
        var asyncRequest; // variable to hold XMLHttpRequest object
        asyncRequest = new XMLHttpRequest(); // create request object

        // register event handler
        asyncRequest.onreadystatechange = function(){
            stateChange(asyncRequest, callBackFunction);
        }
        asyncRequest.open( 'GET', url, true ); // prepare the request
        asyncRequest.send( null ); // send the request
    } // end try
    catch ( exception ) {
       alert( 'Request failed.' );
    } // end catch
} // end function getContent

// call function with content when ready
function stateChange(asyncRequest, callBackFunction)
{
     if ( asyncRequest.readyState == 4 && asyncRequest.status == 200 )
     {
           callBackFunction(asyncRequest.responseText);
     } // end if
} // end function stateChange

function loadEntries() {
    getContent("/api/getEntries",processEntries)
}
function processEntries(response){
    nunjucks.render('item.j2', { entries: JSON.parse(response)}, (err, res) => {
        var contentDiv = document.getElementById("content");
        if (err !== null)
            contentDiv.innerHTML = err + "<BR>" + res;
        else
            contentDiv.innerHTML = res;
    });

}

