


function run() {
  var xhttp = new xmlhttprequest();
  xhttp.onreadystatechange = function() {
    if (this.readystate == 4 && this.status == 200) {
      //document.getelementbyid().innertext = this.responsetext;
      document.getelementbyid('graph_frame').contentwindow.location.reload();
      console.log("response received");
    }
  };
  xhttp.open("post", "/api/run", true);
  xhttp.setrequestheader("content-type", "application/x-www-form-urlencoded");

  xhttp.send(`url=${document.getelementbyid('url').value}&request=${document.getelementbyid('request').value}&proxyhost=${document.getelementbyid('proxyhost').value}&proxyport=${document.getelementbyid('proxyport').value}&delayms=${document.getelementbyid('delayms').value}&depth=${document.getelementbyid('depth').value}&scope=${document.getelementbyid('scope').value}`
            );
}

function cancel() {
  var xhttp = new xmlhttprequest();
  xhttp.onreadystatechange = function() {
    if (this.readystate == 4 && this.status == 200) {
      //document.getelementbyid().innertext = this.responsetext;
      document.getelementbyid('graph_frame').contentwindow.location.reload();
      console.log("response received");
    }
  };
  xhttp.open("post", "/api/cancel", true);
  xhttp.setrequestheader("content-type", "application/x-www-form-urlencoded");
  xhttp.send();
}
