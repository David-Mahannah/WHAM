
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

/*
 * Call once per run. This will refresh and generate the entire graph.
 */
function loadData(nodes, edges) {
  
  // Add to network
  console.log(nodes)
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
      '0': {color: {background: '#f56a00', border: 'white'}},
      '1': {color: {background: '#255C99'}},
      '2': {color: {background: '#7FB285'}},
      '3': {color: {background: '#AF1B3F'}},
      '4': {color: {background: '#4D243D'}},
      '5': {color: {background: '#FCC521'}},
      '6': {color: {background: '#E2FFD6'}},
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

function addEdge() {

}
