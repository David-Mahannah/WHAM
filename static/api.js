


function run() {
  document.getElementById("run_button").innerHTML='Running... <i class="fa fa-spinner fa-spin">';
  document.getElementById("run_button").disabled = true;
  document.getElementById("cancel_button").disabled = false;
  document.getElementById('user_color_table').innerHTML = '';

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    console.log("response received");
    if (this.readyState == 4 && this.status == 200) {
      let response_json = JSON.parse(this.responseText);
      console.log("Success")
      //document.getElementById('graph_frame').contentWindow.location.reload();
      document.getElementById('server_response').innerText = JSON.parse(this.responseText)['Message']; 

      loadData(response_json['node_list'], response_json['edge_list'])

      //document.getElementById('graph_frame').contentWindow.location.reload();
      document.getElementById("run_button").innerHTML='Run';
      document.getElementById("run_button").disabled = false;
      document.getElementById("cancel_button").disabled = true;

      /*
      table = document.getElementById('user_color_table');
      new_row = table.insertRow(-1);
      new_row.insertCell(0).innerHTML = '<th>Color</th>'
      new_row.insertCell(1).innerHTML = '<th>Name</th>'
      let users = response_json["Users"];
      for (let i = 0; i < users.length; i++)
      {
        new_row = table.insertRow(-1);
        let cell1 = new_row.insertCell(0).innerHTML = '<input type=color value="'+ users[i][1]+'" onchange=\'update_colors()\'></span>'
        let cell2 = new_row.insertCell(1).innerHTML = '<span class="user_group">'+ users[i][0]+'</span>'
      }
      */
       //loadData(response_json['nodes'], response_json['edges'])


    } else if (this.readyState == 4) {
      console.log("Failure" + this.readyState)
      document.getElementById('server_response').innerText = 'Error ' + this.status;
      document.getElementById("run_button").innerHTML='Run';
      document.getElementById("run_button").disabled = false;
      document.getElementById("cancel_button").disabled = true;
    }
  };

  xhttp.open("post", "/api/run", true);
  xhttp.setRequestHeader("content-type", "application/json;charset=UTF-8");
  
  auth_data = {}
  table = document.getElementById("auth_table");
  for (let i = 1; i < table.rows.length; i++)
  {
    let row = table.rows[i];
    let user = row.cells[0].getElementsByTagName('input')[0].value;
    if (user != '')
    {
      auth_data[user] = row.cells[1].getElementsByTagName('input')[0].value;
    }
  }

  var formData = {"URL": ((document.getElementById('URL_Radio').checked) ? document.getElementById('URL').value : 'Disabled'),
                  "Request": ((document.getElementById('Request_Radio').checked) ? document.getElementById('Request').value : 'Disabled'),
                  "ProxyHost": ((document.getElementById('ProxyCheckBox').checked) ? document.getElementById('ProxyHost').value : "Disabled"),
                  "ProxyPort": ((document.getElementById('ProxyCheckBox').checked) ? document.getElementById('ProxyPort').value : "Disabled"),
                  "DelayMS": ((document.getElementById('DelayCheckBox').checked) ? document.getElementById('DelayMS').value : 'Disabled'),
                  "Depth": document.getElementById('Depth').value,
                  "Scope": ((document.getElementById('scope_toggle').checked) ? document.getElementById('Scope').value : "Disabled"),
                  "Cert": ((document.getElementById('ProxyCheckBox').checked) ? document.getElementById('Cert').value : 'Disabled'),
                  "ThreadCount": document.getElementById('ThreadCount').value,
                  "Auth": ((document.getElementById('custom_user_roles_checkbox').checked) ? auth_data : {"default_header":"WHAM:WHAM"})
  }
  xhttp.send(JSON.stringify(formData));
}

function cancel() {
  document.getElementById("cancel_button").innerHTML='Cancelling... <i class="fa fa-spinner fa-spin">';
  document.getElementById("cancel_button").disabled = true
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    console.log("Anything" + this.status);
    if (this.status == 200) {
      //document.getElementById().innertext = this.responsetext;
      document.getElementById('graph_frame').contentWindow.location.reload();
      console.log("Cancel response received");
      document.getElementById("cancel_button").innerHTML='Cancel';
      document.getElementById("cancel_button").disabled = false
    } else if (this.readyState == 4) {
      document.getElementById("cancel_button").innerHTML='Cancel';
      document.getElementById("cancel_button").disabled = false;
    } else {
      console.log('Ahhhh' + this.readyState + this.status);
    }
  };
  xhttp.open("post", "/api/cancel", true);
  xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded");
  xhttp.send();
}



function search() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    console.log("response received");
    if (this.readyState == 4 && this.status == 200) {
      console.log("Success")
      document.getElementById('graph_frame').contentWindow.location.reload();
      document.getElementById('server_response').innerText = JSON.parse(this.responseText)['Message']; 
    } else if (this.readyState == 4) {
      console.log("Failure" + this.readyState)
      document.getElementById('server_response').innerText = 'Error ' + this.status;
    }
  };

  xhttp.open("post", "/api/search", true);
  xhttp.setRequestHeader("content-type", "application/json;charset=UTF-8");
  var formData = {"Negative":document.getElementById("NegativeSearchCheckbox").checked,"Text":document.getElementById("SearchTextbox").value
  }
  xhttp.send(JSON.stringify(formData));
}


function update_colors() 
{
    color_data = {}
    table = document.getElementById("user_color_table");
    for (let i = 1; i < table.rows.length; i++)
    {
      let row = table.rows[i];
      let user = row.cells[1].innerText;
      if (user != '') {
        color_data[user] = row.cells[0].getElementsByTagName('input')[0].value;
      }
    }
    console.log(color_data)


    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      console.log("response received");
      if (this.readyState == 4 && this.status == 200) {
        console.log("Success")
        document.getElementById('graph_frame').contentWindow.location.reload();
        document.getElementById('server_response').innerText = JSON.parse(this.responseText)['Message']; 
      } else if (this.readyState == 4) {
        console.log("Failure" + this.readyState)
        document.getElementById('server_response').innerText = 'Error ' + this.status;
      }
    };

    xhttp.open("post", "/api/update_colors", true);
    xhttp.setRequestHeader("content-type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify(color_data));
}


function deleteme(element) {
  let row = element.parentNode.parentNode;
  row.parentNode.removeChild(row);
}

function addme() {
  table = document.getElementById('auth_table');
  new_row = table.insertRow(-1);
  let cell1 = new_row.insertCell(0).innerHTML = '<input type="text" class="role_input">'
  let cell2 = new_row.insertCell(1).innerHTML = '<input type="text" class="role_input">'
  let cell3 = new_row.insertCell(2).innerHTML = '<button class="delete_role_button" tabindex="-1" onclick="deleteme(this)">X</button>'
}
