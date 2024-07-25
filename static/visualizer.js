
var network;
var options;
/*

{
	"Message":"Mapping complete.",
	"node_list":["label":"/",
				 "host":"google.com",    # Data not explicitly used in Vis.JS can be stored in the node list.
				 "group": 1,			       # Group ID correlates with list index under "user_groupings"
				],                       # All nodes
	"edge_list":[],
	"user_groups":[
		"user1",                     # Nodes accessible to user 1
		"user2",
		"user3",
		"user1, user2",              # Nodes accessible to user 1 and user 2
		"user2, user3",
		"user1, user3",
		"user1, user2, user3"        # ...
	]
}

 */



function createHTMLTitle(item, groups) {
  var element = document.createElement("div");
  var table = document.createElement("table");

  new_row = table.insertRow();
  new_row.insertCell().appendChild(document.createTextNode('Host:'));
  new_row.insertCell().appendChild(document.createTextNode(item.host));


  new_row = table.insertRow();
  new_row.insertCell().appendChild(document.createTextNode('Path:'));
  new_row.insertCell().appendChild(document.createTextNode(item.path));


  new_row = table.insertRow();
  new_row.insertCell().appendChild(document.createTextNode('Users:'));
  new_row.insertCell().appendChild(document.createTextNode(groups[item['group']]));


  element.appendChild(table);
  return element;
}

/*
 * Call once per run. This will refresh and generate the entire graph.
 */
function loadData(nodes, edges, groups) {
  
  // Add to network
  console.log(nodes)
  for (item of nodes) {
    item.title = createHTMLTitle(item, Object.fromEntries(Object.entries(groups).map(([key, value]) => [value, key])));
  }
  let vis_nodes = new vis.DataSet(nodes);
  console.log(edges)
  // create an array with edges
  let vis_edges = new vis.DataSet(edges);

  // create a network
  var container = document.getElementById("show");
  var data = {
    nodes: vis_nodes,
    edges: vis_edges,
  };

  options = {
    groups: {
      '0': {color: {background: '#f56a00', border: '#71808D'}},
      '1': {color: {background: '#255C99', border: '#71808D'}},
      '2': {color: {background: '#7FB285', border: '#71808D'}},
      '3': {color: {background: '#AF1B3F', border: '#71808D'}},
      '4': {color: {background: '#4D243D', border: '#71808D'}},
      '5': {color: {background: '#FCC521', border: '#71808D'}},
      '6': {color: {background: '#E2FFD6', border: '#71808D'}},
    },
    nodes: {
      shape: 'box',
      font: { size: 12 },
      shadow: { enabled: true }
    },
    edges: {
      font: { align: "top" },
      smooth: { type: "discrete" },
      arrows: {
        to: {enabled: true, scaleFactor: 1, type: "arrow"}
      },
      color: {highlight: "white"}
    },
    layout: {
      hierarchical: {
        enabled:true,
      }
    },
    
    layout: { improvedLayout: true },
    
    physics: {
      // Even though it's disabled the options still apply to network.stabilize().
      enabled: false,
      solver: "repulsion",
      repulsion: {
        nodeDistance: 300 // Put more distance between the nodes.
      }
    },
  };

  network = new vis.Network(container, data, options);
  network.stabilize();
}



function default_graphView() {

  options['layout'] = { improvedLayout: true };
  network.setOptions(options);
  network.stabilize()
}

function hierarchicalView() {
  options['layout'] = {
      hierarchical: {
        enabled:true,
      }
    };
  network.setOptions(options);
}


function addEdge() {

}
// Function to toggle full screen
function toggleFullScreen() {
  var elem = document.getElementById("show");

  if (!document.fullscreenElement && !document.mozFullScreenElement &&
      !document.webkitFullscreenElement && !document.msFullscreenElement) {
    if (elem.requestFullscreen) {
      elem.requestFullscreen();
      elem.classList.add('fullscreen');
    } else if (elem.msRequestFullscreen) {
      elem.msRequestFullscreen();
    } else if (elem.mozRequestFullScreen) {
      elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) {
      elem.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
      elem.classList.remove('fullscreen');
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    }
  }
}
