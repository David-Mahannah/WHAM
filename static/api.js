


function run() {
  document.getElementById("run_button").innerHTML='Running... <i class="fa fa-spinner fa-spin">';
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    console.log("response received");
    if (this.readyState == 4 && this.status == 200) {
      console.log("Success")
      document.getElementById('graph_frame').contentWindow.location.reload();
      document.getElementById('server_response').innerText = JSON.parse(this.responseText)['Message']; 
      document.getElementById('graph_frame').contentWindow.location.reload();
      document.getElementById("run_button").innerHTML='Run';
    } else if (this.readyState == 4) {
      console.log("Failure" + this.readyState)
      document.getElementById('server_response').innerText = 'Error ' + this.status;
      document.getElementById("run_button").innerHTML='Run';
    }
  };

  xhttp.open("post", "/api/run", true);
  xhttp.setRequestHeader("content-type", "application/json;charset=UTF-8");
  var formData = {"URL":document.getElementById('URL').value,
                  "Request": document.getElementById('Request').value,
                  "ProxyHost": ((document.getElementById('ProxyCheckBox').checked) ? document.getElementById('ProxyHost').value : "Disabled"),
                  "ProxyPort": ((document.getElementById('ProxyCheckBox').checked) ? document.getElementById('ProxyPort').value : "Disabled"),
                  "DelayMS": ((document.getElementById('DelayCheckBox').checked) ? document.getElementById('DelayMS').value : 'Disabled'),
                  "Depth": document.getElementById('Depth').value,
                  "Scope": document.getElementById('Scope').value,
                  "Cert": document.getElementById('Cert').value,
                  "ThreadCount": document.getElementById('ThreadCount').value
  }
  xhttp.send(JSON.stringify(formData));
}

function cancel() {
  var xhttp = new XMLHttpRequest();
  xhttp.onReadyStateChange = function() {
    if (this.readystate == 4 && this.status == 200) {
      //document.getElementById().innertext = this.responsetext;
      document.getElementById('graph_frame').contentwindow.location.reload();
      console.log("response received");
    }
  };
  xhttp.open("post", "/api/cancel", true);
  xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded");
  xhttp.send();
}


