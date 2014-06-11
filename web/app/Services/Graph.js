function Graph(d3, el) {
    var self = this;
    var force; // forces
    this.vis = null; // svg canvas
    var nodes;
    var links;
    var h = 100;
    var w = 100;
    var tooltip;
    var popover = jQuery('#graphPopover');




    // init
    function initGraph() {
        // get window dimensions
        fullScreenGraph();
        force = d3.layout.force()
            .gravity(.01)
            .distance(150)
            .charge(-200)
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
    }



    // =====================================
    // Add and remove Data interface
    // =====================================


    this.clearNodes = function() {

        nodes = force.nodes();
        links = force.links();

        //nodes = [];
        //links = [];

    }
    // Add and remove elements on the graph object
    this.addNode = function(node) {
        nodes.push(node);
    }

    var findNode = function(id) {
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === id)
                return nodes[i]
        };
    }

    var findNodeIndex = function(id) {
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === id)
                return i
        };
    }


    this.removeNode = function(id) {
        var i = 0;
        var n = findNode(id);
        while (i < links.length) {
            if ((links[i]['source'] === n) || (links[i]['target'] == n))
                links.splice(i, 1);
            else i++;
        }
        var index = findNodeIndex(id);
        if (index !== undefined) {
            nodes.splice(index, 1);
            self.update();
        }
    }

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
            .call(force.drag);

        nodeEnter.append("circle")
            .attr("r", function(d) {
                return 30 * Math.random(); // @todo: change to d.weight if it has sensible values
            })
            .attr("id", function(d) {
                return d.id
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
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text(function(d) {
                return d.title
            });

        nodeEnter.append("id").attr("id", function(d) {
            return d.id;
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


    var expand = function() {
        var clickedObject = d3.select(this).select("id")[0][0]
        if (!clickedObject)
            return console.log('could not find clicked object', d3.select(this).select("id"));


        var clickedId = clickedObject.getAttribute("id");

        var clickedNode = nodes[clickedId];
        var docs = clickedNode.documents;
        var argstring = "?";
        docs.forEach(function(doc) {
            argstring = argstring + "document=" + doc.id + "&"
        });
        newNodes = JSON.parse(httpGet("/retrieve_documents" + argstring));
    }
    var mouseout = function() {

        popover.css("visibility", "hidden");

        d3.select(this).select("circle").transition()
            .duration(750)
            .attr("r", 15);
    }
    var mouseover = function() {
        var target = d3.select(this);
        var targetId = target[0][0].getAttribute('id');

        popover
            .css('visibility', "visible")
            .css('left', d3.event.pageX + 10 + "px")
            .css('top', d3.event.pageY - 10 + "px");
        var targetNode = findNode(targetId);

        popover.find('p').html(targetNode.title);

        // @does not work.
        /*target.select("circle").transition()
            .duration(750)
            .attr("r", 30);*/
        return;
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

    plugins();
    initGraph();
    return this;
};
