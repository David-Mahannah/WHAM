



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
