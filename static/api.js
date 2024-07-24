
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

document.addEventListener("click", async function(evnt){
  await sleep(500);
  updateApplicationState();
});

document.addEventListener("keyup", async function(evnt){
  await sleep(500);
  updateApplicationState();
});

function populateGroupColorTable(users) {
    document.getElementById('user_color_table').innerHTML = '';
    table = document.getElementById('user_color_table');
    new_row = table.insertRow(-1);

    new_row.insertCell(0).innerHTML = '<th>Color</th>'
    new_row.insertCell(1).innerHTML = '<th>Name</th>'


    if (users != undefined) {
    for (const [key, value] of Object.entries(users))
    {
      new_row = table.insertRow(-1);
      let cell1 = new_row.insertCell(0).innerHTML = '<input id="' + value + '" type=color value="'+ options.groups[value]['color']['background']+'" onchange=\'update_colors(this)\'></span>'
      let cell2 = new_row.insertCell(1).innerHTML = '<span class="user_group">'+key+'</span>'
    }
    }
}


/*
 * Called on window load. 
 * Will attempt to load any existing graph or settings data from a previouse
 * session.
 */
function init() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      let response_json = JSON.parse(this.responseText);
      document.getElementById('server_response').innerText = response_json['Message']; 

      if (response_json['Message'] != "Failed to load previous graph data.") {
        loadData(response_json['node_list'], response_json['edge_list'], response_json['groups'])
      }

      populateGroupColorTable(response_json["groups"])
    } else if (this.readyState == 4) {
      document.getElementById('server_response').innerText = 'Error ' + this.status;
    }
  }
  xhttp.open("get", "/api/graph", true);
  xhttp.send();


  loadApplicationState();

}



function gebid(id) {
  return document.getElementById(id);
}


function updateApplicationState() {
  auth_data = {}
  table = document.getElementById("auth_table");
  for (let i = 1; i < table.rows.length; i++) {
    let row = table.rows[i];
    let user = row.cells[0].getElementsByTagName('input')[0].value;
    if (user != '') {
      auth_data[user] = row.cells[1].getElementsByTagName('input')[0].value;
    }
  }
  
  var application_state = {
    "Target": {
      "Collapsed": !(gebid('Target_Details').open),
      "URL": {"Enabled": gebid('URL_Radio').checked, "value": gebid('URL').value},
      "Request": { "Enabled": gebid('Request_Radio').checked, "value": gebid('Request').value},
    },
    "User_Roles": {
      "Collapsed": !(gebid('User_Roles_Details').open),
      "Enabled": gebid('custom_user_roles_checkbox').checked,
      "Roles": auth_data
    },
    "Scope": {
      "Collapsed": !(gebid('Scope_Details').open),
      "Enabled":gebid('scope_toggle').checked,
      "Domain":gebid('Scope').value
    },
    "Proxy": {
      "Collapsed": !(gebid('Proxy_Details').open),
      "Enabled":gebid('ProxyCheckBox').checked,
      "Host":gebid('ProxyHost').value,
      "Port":gebid('ProxyPort').value,
      "Certificate":"NA"
    },
    "Behavior": {
      "Collapsed": !(gebid('Behavior_Details').open),
      "Delay": {
        "Enabled": gebid('DelayCheckBox').checked, 
        "MS": gebid('DelayMS').value
      },
      "Depth": gebid('Depth').value,
      "ThreadCount": gebid('ThreadCount').value
    },
    "Users": {
      "Collapsed": !(gebid('Users_Details').open)
    }
  }

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {

    }
  } 
  xhttp.open("post", "/api/state", true);
  xhttp.setRequestHeader("content-type", "application/json; charset=UTF-8");
  xhttp.send(JSON.stringify(application_state));
}

function loadApplicationState() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      let response_json = JSON.parse(this.responseText);

      /* TODO Update DOM using the below items */

      // Target
      gebid('Target_Details').open = !(response_json['Target']['Collapsed']);
      gebid('URL_Radio').checked = response_json["Target"]["URL"]["Enabled"]
      gebid('URL').value = response_json["Target"]["URL"]["value"]
      gebid('Request_Radio').checked = response_json["Target"]["Request"]["Enabled"]
      gebid('Request').value = response_json["Target"]["Request"]["value"]

      // User Roles
      gebid('User_Roles_Details').open = !(response_json['User_Roles']['Collapsed']);
      gebid('custom_user_roles_checkbox').checked = response_json["User_Roles"]["Enabled"];
      let roles = response_json["User_Roles"]["Roles"];


      if (Object.keys(roles).length !== 0) {
        table = document.getElementById('auth_table');
        table.innerHTML = '<tbody><tr><th>User</th><th>Session Header</th></tr></tbody>';

        let first = true;
        for (let [key, value] of Object.entries(roles)) {
          if (key == 'default_header' && value == 'WHAM:WHAM')
          {
            key = '';
            value = '';
          }
          let new_row = table.insertRow(-1);
          let cell1 = new_row.insertCell(0).innerHTML = '<input type="text" class="role_input" value="'+key+'">'
          let cell2 = new_row.insertCell(1).innerHTML = '<input type="text" class="role_input" value="'+value+'">'
          if (!first) {
          let cell3 = new_row.insertCell(2).innerHTML = '<button class="delete_role_button" tabindex="-1" onclick="deleteme(this)">X</button>'
          }
          first = false;
        }
        custom_user_roles_toggle();
      }

      // Scope
      gebid('Scope_Details').open = !(response_json['Scope']['Collapsed']);
      gebid('scope_toggle').checked = response_json["Scope"]["Enabled"]
      gebid('Scope').value = response_json["Scope"]["Domain"]

      // Proxy
      gebid('Proxy_Details').open = !(response_json['Proxy']['Collapsed']);
      gebid('ProxyCheckBox').checked = response_json["Proxy"]["Enabled"]
      gebid('ProxyHost').value = response_json["Proxy"]["Host"]
      gebid('ProxyPort').value = response_json["Proxy"]["Port"]
      // response_json["Proxy"]["Certficate"]


      // Behavior
      gebid('Behavior_Details').open = !(response_json['Behavior']['Collapsed']);
      gebid('DelayCheckBox').checked = response_json["Behavior"]["Delay"]["Enabled"]
      gebid('DelayMS').value = response_json["Behavior"]["Delay"]["MS"]
      gebid('Depth').value = response_json["Behavior"]["Depth"]
      gebid('ThreadCount').value = response_json["Behavior"]["ThreadCount"]
     

      // Users
      gebid('Users_Details').open = !(response_json['Users']['Collapsed']);
      /*
      var application_state = {
        "Target": {
          "URL": {"Enabled": gebid('URL_Radio').checked, "value": gebid('URL').value},
          "Request": { "Enabled": gebid('Request_Radio'), "value": gebid('Request')},
        },
        "User_Roles": {
          "Roles": (gebid('custom_user_roles_checkbox').checked ? auth_data : {"default_header":"WHAM:WHAM"})
        },
        "Scope": {
          "Enabled":gebid('scope_toggle').checked,
          "Domain":gebid('Scope').value
        },
        "Proxy": {
          "Enabled":gebid('ProxyCheckBox').checked,
          "Host":gebid('ProxyHost').value,
          "Port":gebid('ProxyPort').value,
          "Certificate":"NA"
        },
        "Behavior": {
          "Delay": {
            "Enabled": gebid('DelayCheckBox').checked, 
            "MS": gebid('DelayMS').value
          },
          "Depth": gebid('Depth').value,
          "ThreadCount": gebid('ThreadCount').value
        }
      }
      */
    }
  }
  xhttp.open("get", "/api/state", true);
  xhttp.send(JSON.stringify());
}


function run() {
  updateApplicationState()

  document.getElementById("run_button").innerHTML='Running... <i class="fa fa-spinner fa-spin">';
  document.getElementById("run_button").disabled = true;
  document.getElementById("cancel_button").disabled = false;
  document.getElementById('user_color_table').innerHTML = '';

  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      let response_json = JSON.parse(this.responseText);
      document.getElementById('server_response').innerText = JSON.parse(this.responseText)['Message']; 
      loadData(response_json['node_list'], response_json['edge_list'], response_json['groups'])
      document.getElementById("run_button").innerHTML='Run';
      document.getElementById("run_button").disabled = false;
      document.getElementById("cancel_button").disabled = true;
      populateGroupColorTable(response_json["groups"])
    } else if (this.readyState == 4) {
      document.getElementById('server_response').innerText = 'Error ' + this.status;
      document.getElementById("run_button").innerHTML='Run';
      document.getElementById("run_button").disabled = false;
      document.getElementById("cancel_button").disabled = true;
    }
  };

  xhttp.open("post", "/api/run", true);
  xhttp.send();
}

function cancel() {
  document.getElementById("cancel_button").innerHTML='Cancelling... <i class="fa fa-spinner fa-spin">';
  document.getElementById("cancel_button").disabled = true
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.status == 200) {
      document.getElementById('graph_frame').contentWindow.location.reload();
      console.log("Cancel response received");
      document.getElementById("cancel_button").innerHTML='Cancel';
      document.getElementById("cancel_button").disabled = false
    } else if (this.readyState == 4) {
      document.getElementById("cancel_button").innerHTML='Cancel';
      document.getElementById("cancel_button").disabled = false;
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


function update_colors(element) 
{
  console.log("Updating group: " + element.id);
  options.groups[element.id] = {color: {background: element.value}}
  network.setOptions(options);
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
