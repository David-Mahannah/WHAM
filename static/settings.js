



function radio_switch() {
  if (event.target && event.target.matches("input[type='radio']")) {
    if (event.target.id == "URL_Radio") {
      document.getElementById("URL").disabled = false;
      document.getElementById("Request").disabled = true;
    } else {
      document.getElementById("URL").disabled = true;
      document.getElementById("Request").disabled = false;
    }
    console.log(event.target.id);
  }
}

function proxy_toggle() {
  if (event.target && event.target.matches("input[type='checkbox']")) {
    if (event.target.checked) {
      document.getElementById("ProxyHost").disabled = false;
      document.getElementById("ProxyPort").disabled = false;
      document.getElementById("Cert").disabled = false;
    } else {
      document.getElementById("ProxyHost").disabled = true;
      document.getElementById("ProxyPort").disabled = true;
      document.getElementById("Cert").disabled = true;
    }
  }
}


function delay_toggle() {
  if (event.target && event.target.matches("input[type='checkbox']")) {
    if (event.target.checked) {
      document.getElementById("DelayMS").disabled = false;
    } else {
      document.getElementById("DelayMS").disabled = true;
    }
}
}


function custom_user_roles_toggle() {
  if (event.target && event.target.matches("input[type='checkbox']")) {
    if (event.target.checked) {
      let inputs = document.getElementsByClassName("role_input")
      for (let i = 0; i < inputs.length; i++)
      {
        inputs[i].disabled = false;
      }


      inputs = document.getElementsByClassName("delete_role_button")
      for (let i = 0; i < inputs.length; i++)
      {
        inputs[i].disabled = false;
      }
      document.getElementById("add_user_button").disabled = false;

    } else {
      let inputs = document.getElementsByClassName("role_input")
      for (let i = 0; i < inputs.length; i++)
      {
        inputs[i].disabled = true;
      }
      inputs = document.getElementsByClassName("delete_role_button")
      for (let i = 0; i < inputs.length; i++)
      {
        inputs[i].disabled = true;
      }
      document.getElementById("add_user_button").disabled = true;
    }
  }
}


function custom_scope_toggle() {
  if (event.target && event.target.matches("input[type='checkbox']")) {
    if (event.target.checked) {
      document.getElementById('Scope').disabled = false;
    } else {
      document.getElementById('Scope').disabled = true;
    }
  }
}
