

function GraphFactory($http,AppSettings,$q,$log) {


    var self = this;
    var debug = false;
    var force; // forces
    this.vis = null; // svg canvas
    var nodes;
    var links;
    /*
     holds a hash map: {node:  [relatedNode, relatedNode,... ] }

     */
    var graphStructureCache = {};
    var h = 100;
    var w = 100;
    var tooltip;
    var popover = jQuery('#graphPopover');
    var d3;

    var defaultUrl = AppSettings.apiUrl + 'search_entity?entityName=';
    var additionalNodesUrlCluster = AppSettings.apiUrl + "retrieve_documents";
    var additionalNodesUrlDocument = AppSettings.apiUrl + "search_similar";

    // use local files instead of server
    if (AppSettings.mockhttp){
        defaultUrl = '/holist/web/demo.json?entityName=';
        additionalNodesUrlCluster = '/holist/web/demo.json?retrieve_documents';
        additionalNodesUrlDocument = '/holist/web/demo.json?retrieve_documents';
    }

    // init
    self.initGraph = function(_d3, el) {
        d3 = _d3;
        plugins();

        // get window dimensions
        fullScreenGraph();
        force = d3.layout.force()
            .gravity(.05)
            .distance(170)
            .charge(-5020)
            .size([w, h]);
        //    .tick(self.tick);

        this.clearNodes();

        // draw svg
        self.vis = d3.select(el).append("svg:svg");
        //resize
        fullScreenGraph();
        jQuery(window).resize(fullScreenGraph);


        // addons


        // Make it all go
        self.update();
        return self;

    }



    // =====================================
    // Add and remove Data interface
    // =====================================

    // clears all nodes
    this.clearNodes = function() {

        nodes = force.nodes();
        links = force.links();


    }
    // Add and remove elements on the graph object
    this.addNode = function(node) {
        for (var i = nodes.length - 1; i >= 0; i--) {
            if(nodes[i].id == node.id){
                return;
            }
        };
        console.log('[graph] adding node', node);
        nodes.push(node);
    }

    // find node by id
    var findNode = function(id) {
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === id)
                return nodes[i]
        };
    }

    // find index of node by id
    var findNodeIndex = function(id) {
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === id)
                return i
        };
    }

    /**
     * pass the node and remove its links
     * to other nodes.
     * @param id
     */
    this.removeLinksOfNode = function(node) {

        var i = 0;
        while (i < links.length) {
            if ((links[i]['source'].id == node.id) || (links[i]['target'].id == node.id)) {
                links.splice(i, 1);
            } else {
                i++;
            }
        }
    }
    /***
     * pass node or nodeid to remove the node;
     * @param id
     */
    this.removeNode = function(id) {

        var i = 0;
        var n = (typeof(id) == 'object' ? id : findNode(id) );

        self.removeLinksOfNode(n);
        var index = findNodeIndex(n.id);
        if (index !== undefined) {
            nodes.splice(index, 1);
            self.update();
        }else {
            console.log('[graph] error: remove node, not found!',id);
        }
    }

    // add connection between 2nodes (by id)
    this.addLink = function(sourceId, targetId) {
        var sourceNode = findNode(sourceId);
        var targetNode = findNode(targetId);
        if ((sourceNode !== undefined) && (targetNode !== undefined)) {
            links.push({
                "source": sourceNode,
                "target": targetNode
            });
            //self.update();
        }
    }
    /**
     *
     */
    var buildLinkStructure = function() {
        graphStructureCache = {};

        var addLink = function(node,targetNode) {

            if (!graphStructureCache[node.id])
                graphStructureCache[node.id] = [];
            graphStructureCache[node.id].push(targetNode);

        }
        console.log(links);
        for (var i in links) {
            //console.log(links[i]['target'].id + '<====>' + links[i]['source'].id);
            addLink(links[i]['target'], links[i]['source']);
            addLink(links[i]['source'], links[i]['target']);
        }

        console.log('final graph structure: ',graphStructureCache );
    }
    /**
     * find all related links
     * @param skipNode
     * @param node
     * @returns {*}
     */
    this.findLinkedNodes = function(node) {
        if (node == null) return [];
        return graphStructureCache[node.id];

    }

    //
    // reduces Opacity of all nodes, except the "skip" one
    // skip is a node id
    //
    this.reduceNodes = function(currentNode){
        buildLinkStructure();
        var reduceNodesRecursive = function(parentNode, node, level) {
            var nodes = self.findLinkedNodes(node);
            for (var i in nodes) {
                if (parentNode && parentNode.id == nodes[i].id) continue;
                reduceNodesRecursive(node, nodes[i], level + 1 );
            }
            console.log(node.id + ' = ' + level);
            if (level > 2) {
                return self.removeNode(node);
            }
            if (level > 1) {
                var opacity = 1 - (0.25 * level);

            }


        }
        reduceNodesRecursive(null, currentNode, 0);

    };
    this.reduceAllNodes = function(skip) {


        return;
        for (var i in nodes) {

            console.log('new opacity',i, nodes[i].opacity);
            // skip single node, e.g. parent
            if (skip && skip === nodes[i].id) {
                continue;
            }
            nodes[i].opacity = (nodes[i].opacity ? nodes[i].opacity - 0.3: 0.8);

            if (nodes[i].opacity < 0.1) {
                this.removeNode(nodes[i].id);
                return;
            }
            if (!nodes[i].jqCircle) nodes[i].jqCircle = $(nodes[i].circle);

            nodes[i].jqCircle.fadeTo(500, nodes[i].opacity);

        }
        // console.log(nodes);
    }
    this.reduceNodeOpacity = function(node) {
        if (!node.opacity) {
            node.opacity = 0.5;
        }



    }
    // update method; updates the graph
    self.update = function() {

        var link = self.vis.selectAll("line.link")
            .data(links, function(d) {
                return d.source.id + "-" + d.target.id;
            });

        link.enter().insert("line")
            .attr("class", "link");

        link.exit().remove();

        var node = self.vis.selectAll("g.node")
            .data(nodes, function(d) {
                return d.id;
            });

        var nodeEnter = node.enter()
            .append("g")
            .attr("class", "node")
            .attr("id", function(d) {
                return d.id
            })
            .call(force.drag);

        nodeEnter.append("circle")
            .attr("r", function(d) {
                if (d.id == 'center') return 30;

                return 30 * Math.random() + 3; // @todo: change to d.weight if it has sensible values
            })
            .attr("id", function(d) {
                d.circle = this;
                return "circle_"+d.id
            })
            .style('cursor', 'pointer')
            .on("mouseover", mouseover)
            .on("mouseout", mouseout)
            .on("click", expand);


        /*nodeEnter.attr("cx", function(d) {
            return 10;
        });*/

        /*nodeEnter.append("image")
            .attr("class", "circle")
            .attr("x", "-8px")
            .attr("y", "-8px")
            .attr("width", "16px")
            .attr("height", "16px")*/



        nodeEnter.append("text")
            .attr("class", "nodetext")
            .attr("dx", 30)
            .attr("dy", ".35em")
            .text(function(d) {
                return (debug? d.id : d.title)
            });

        nodeEnter.append("id").attr("id", function(d) {
            return "id"+d.id;
        });

        node.exit().remove();

        force.on("tick", function() {
            link.attr("x1", function(d) {
                return d.source.x;
            })
                .attr("y1", function(d) {
                    return d.source.y;
                })
                .attr("x2", function(d) {
                    return d.target.x;
                })
                .attr("y2", function(d) {
                    return d.target.y;
                });

            node.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
        });

        // Restart the force layout.
        force.start();
    }



    // =====================================
    // User interaction
    // =====================================
    // getNodeByEvent(d3.select(this))
    // deprecated see next method
    var getNodeIdByEvent = function(target) {
        var targetId = target[0][0].getAttribute('id');
        if (!targetId)
            return console.log('could not find id of targe object', target);
        //
        // a little sloppy
        // gets event ID from circle instead of the node(?)
        // this.id should contain the id, but it does not.
        //


        return (targetId);
    }
    // gets id from (this) (event sender) and removes the prefix
    var getNodeIdFromEventObject = function(obj) {

        var targetId = obj.id;
        return targetId.replace(/circle_/,'').replace(/node_/,'');

    }

    var expand = function() {
        var targetId = getNodeIdFromEventObject(this);
        var targetNode =  findNode(targetId);
        if (!targetNode) {
            return;
        }



        if(!targetNode.documents){
            var argstring = "?id=" + targetId;
            self.fetchAdditionalNodes(additionalNodesUrlDocument + argstring, targetId);
        } else{
                var argstring = "?";
                targetNode.documents.forEach(function(doc) {
                    argstring = argstring + "document=" + doc.id + "&"
                });
                self.fetchAdditionalNodes(additionalNodesUrlCluster + argstring, targetId);
        }



    }
    var mouseout = function() {

        popover.css("visibility", "hidden");

        d3.select(this).select("circle").transition()
            .duration(750)
            .attr("r", 15);
    }
    var mouseover = function() {
        var targetId = getNodeIdFromEventObject(this);
        var targetNode =  findNode(targetId);
        popover
            .css('visibility', "visible")
            .css('left', d3.event.pageX + 10 + "px")
            .css('top', d3.event.pageY - 10 + "px");


        var subdocs = (targetNode.documents?targetNode.documents.length:0);
        var info = targetNode.title;
        if (subdocs > 0) {
            info += ' <br/><i>related documents: '  + subdocs + '</i>';
        }
        popover.find('p').html( info);


        return;
    }



    // =====================================
    // fetchData
    // =====================================
    // fetches enite new keyword
    this.fetchData = function(keyword) {

        console.log('[graph] fetching keyword', keyword);
        httpGet(defaultUrl + keyword)
            .then(function(graphObj, status) {
                var vlinks = graphObj.links;
                var vnodes = graphObj.nodes;

                self.clearNodes();

                for (var i = vnodes.length - 1; i >= 0; i--) {
                    self.addNode(vnodes[i]);

                }
                for (var i = vlinks.length - 1; i >= 0; i--) {
                    self.addLink(vlinks[i].source.id, vlinks[i].target.id);
                }
                self.update();
                //debug
                self.reduceAllNodes('center');

            });


    }
    this.fetchAdditionalNodes = function(url, parentNodeId) {
        var parentNode = findNode(parentNodeId);

        httpGet(url).then(function(results,status){
            if (!results.documents){
                $log.warn('additional nodes does not have documents',results);
            }
            var newNodes = results.documents;
            for (i in newNodes){
                self.addNode(newNodes[i]);
                self.addLink(newNodes[i].id,parentNodeId)
            }
            self.update();
            self.reduceNodes(parentNode);
            if (self.onElementsRender){
                self.onElementsRender(parentNode, results);
            }
        });
        //newNodes = JSON.parse();

    };

    function httpGet(requestUrl) {
        var d = $q.defer();
        $http({
            method: 'GET',
            url: requestUrl
        })
            .success(function(data, status, headers, config) {
                console.log('[GRAPH] Get Data successful', data, status);
                d.resolve(data, status);
            })
            .error(function(data, status, headers, config) {
                d.reject(data, status);
            });

        return d.promise;

        /*    var xmlHttp = null;

         xmlHttp = new XMLHttpRequest();
         xmlHttp.open( "GET", theUrl, false );
         xmlHttp.send( null );
         return xmlHttp.responseText;*/
    }




    // =====================================
    // Events
    // =====================================
    var fullScreenGraph = function() {
        w = jQuery(window).width();
        h = jQuery(window).height() - 60; //for header+ footer
        if (self.vis) {
            self.vis.attr("width", w)
                .attr("height", h);

        }

    }
    ///
    //
    self.tick = function() {
        console.log('[GRAPH] tick')

    }
    self.render = function(data) {
        self.update(); //?
    }
    self.onElementsRender = null;



    // =====================================
    // Plugins
    // =====================================

    function plugins() {
        d3.selection.prototype.moveToFront = function() {
            return this.each(function() {
                this.parentNode.appendChild(this);
            });
        };

    }


    return self;
};
