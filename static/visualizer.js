

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
  /*
  var vis_nodes = new vis.DataSet([
      { id: 1, label: "Node 1" },
      { id: 2, label: "Node 2" },
      { id: 3, label: "Node 3" },
      { id: 4, label: "Node 4" },
      { id: 5, label: "Node 5" },
    ]);
  */


  console.log(edges)
  // create an array with edges
  let vis_edges = new vis.DataSet(edges);
  /**
  var vis_edges = new vis.DataSet([
    { from: 1, to: 3 },
    { from: 1, to: 2 },
    { from: 2, to: 4 },
    { from: 2, to: 5 },
    { from: 3, to: 3 },
  ]);
  */

  // create a network
  var container = document.getElementById("show");
  var data = {
    nodes: vis_nodes,
    edges: vis_edges,
  };

  var options = {
    nodes: {
      shape: 'box',
      font: {
        size: 12,
      },
      shadow: {
        enabled: true
      }
    },
    edges: {
      font: {
        align: "top"
      },
      smooth: {
        type: "discrete"
      },
      arrows: {
        to: {enabled: true, scaleFactor: 1, type: "arrow"}
      }
    },
    layout: {
        improvedLayout: true,
    },
    physics: {
      // Even though it's disabled the options still apply to network.stabilize().
      enabled: false,
      solver: "repulsion",
      repulsion: {
        nodeDistance: 300 // Put more distance between the nodes.
      }
    },
  };

  var network = new vis.Network(container, data, options);
  network.stabilize();
}





function addEdge() {

}
