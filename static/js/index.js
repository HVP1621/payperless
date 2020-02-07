/**
 * Blah
 * @author odahcam
 * @version 0.0.1?
 **/



(function(window, document, undefined) {
    "use strict";
    
    var $ = {
        extend: Object.assign,
        remove: x => x.parentNode.removeChild(x),
    };

    /**
     * Store the plugin name in a variable. It helps you if later decide to change the plugin's name
     * @type {string} pluginName
     **/
    var pluginName = "dragOn";

    /*
     * The plugin constructor.
     */
    function Plugin(elem, options) {

        this.elem = elem;

        
        // Variables default
        this.settings = $.extend({}, this.defaults, options);

        this.metrics = {
            width: null,
            height: null,
            left: null,
            top: null,
            distanceFrom: {
                document: {
                    left: null,
                    top: null,
                }
            },
            whiteSpace: {
                left: null,
                top: null,
            },
            viewBox: {
				scale: null,
                rendered: {
                    width: null,
                    height: null,
                },
                attr: {
                    x: null,
                    y: null,
                    width: null,
                    height: null,
                }
            }
        };
        this.vars = [];
        this.count = 0;
        this.vars[0] = document.getElementById('Id');
        this.vars[1] = document.getElementById('left');
        this.vars[2] = document.getElementById('top')
        this.vars[3] = document.getElementById('height')
        this.vars[4] = document.getElementById('width')

        return this.init();
    }

    // Public Methods
    Object.assign(Plugin.prototype, {
        /*
         * Default options
         * @type {Object} defaults
         */
        defaults: {
            listenTO: "img", // {string} : selector for matching valid elements
            namespace: {
				svg: "http://www.w3.org/2000/svg", // SVG 2 namespace
				xlink: "http://www.w3.org/1999/xlink"
			}
		},
        /**
         *
         */
        init: function() {
            // set event listenners, put elem to do something usefull.
            
            console.log(this.elem);

            
            this.elem.classList.add(pluginName + '-dropzone')
            
            
            this.drawArea = this.createElementSVG('g', {
                class: pluginName + '-drawArea',
                width: '100%',
                height: '100%',
            });
            
            // adds drawArea to SVG
            this.elem.appendChild(this.drawArea);
            

            // enable draggables to be dropped into this
            interact(this.elem)
                .dropzone(interactBasicOptions.dropzone)
                .on('drop', this.ondrop.bind(this));
            console.log(this.elem)
            var svg_drop = document.getElementById("svg-dropzone")
            var iFrame = document.getElementById( 'embed1' );
            // var height = getDocHeight(iFrame.src)
            svg_drop.setAttribute("width", iFrame.width)
            svg_drop.setAttribute("height", iFrame.height)

            // target elements with the "draggable" class
            interact(this.settings.listenTo)
                .draggable($.extend({ manualStart: true }), interactBasicOptions.draggable)
                .on('move', function (event) {
                    var interaction = event.interaction;

                    // if the pointer was moved while being held down
                    // and an interaction hasn't started yet
                    if (interaction.pointerIsDown && !interaction.interacting()) {
                      var target = event.currentTarget;
                        // create a clone of the currentTarget element
                      var clone = event.currentTarget.cloneNode(true);
                        
                        console.log(event.currentTarget);
                        
                        var targetBounding = target.getBoundingClientRect();

                        // add dragging class
                        clone.classList.add("drag-dragging");
                        clone.classList.remove("drag-dropped");
                        
                        // translate the element
                        clone.style.transform = "translate(0px, 0px)";
                        clone.style.position = "absolute";        
                        clone.style.top = (targetBounding.top + window.scrollY) + "px";
                        clone.style.left = (targetBounding.left + window.scrollX) + "px";

                        // update the posiion attributes
                        clone.setAttribute("data-x", 0);
                        clone.setAttribute("data-y", 0);

                        // insert the clone to the page
                        document.body.appendChild(clone);

                        // start a drag interaction targeting the clone
                        interaction.start({ name: 'drag' }, event.interactable, clone);
                    }              
                })
                .on('dragmove', function(event) {

                    var target = event.target;
                    // keep the dragged position in the data-x/data-y attribute;
                    var x = (parseFloat(target.getAttribute("data-x")) || 0) + event.dx;
                    var y = (parseFloat(target.getAttribute("data-y")) || 0) + event.dy;
                
                    var targetBounding = target.getBoundingClientRect();

                    // translate the element
                    target.style.webkitTransform = target.style.transform = "translate(" + x + "px, " + y + "px)";        
                    

                    // update the posiion attributes
                    target.setAttribute("data-x", x);
                    target.setAttribute("data-y", y);
                })
                .on('dragend', function(event) {
                    event.target.parentNode.removeChild(event.target);
                });
            
            return this;
        },
        /**
         * @param {string} tag
         * @param {object} attrs
         */
        createElementSVG: function(tag, attrs) {
            
            var el = document.createElementNS(this.settings.namespace.svg, tag);
            
            for (var k in attrs) {
                el.setAttribute(k, attrs[k]);
            }
            
            return el;
        },
        /**
         * Updates the metrics property.
         */
        updateMetrics: function() {
            // base coordinates
            // position of base elem relative to the client window
            var elemBounding = this.elem.getBoundingClientRect();

            
            console.log(elemBounding);
            
            Object.assign(this.metrics, elemBounding);
            
            console.log(this.metrics);
            
            this.metrics.width = elemBounding.width;
            this.metrics.height = elemBounding.height;
            this.metrics.top = elemBounding.top;
            this.metrics.right = elemBounding.right;
            this.metrics.bottom = elemBounding.bottom;
            this.metrics.left = elemBounding.left;
            
            console.log(this.metrics);

            // position of base elem relative to the document
            this.metrics.distanceFrom.document = {
                left: this.metrics.left + window.scrollX,
                top: this.metrics.top + window.scrollY
            };

            console.group("Finding rendered viewBox size");

            // gets viewBox attr as array
            var elemViewBoxAttrArray = this.elem
                .getAttribute("viewBox")
                .split(" "); // x, y, width, height

            // maps viewBox
            this.metrics.viewBox.attr = {
                x: elemViewBoxAttrArray[0],
                y: elemViewBoxAttrArray[1],
                width: elemViewBoxAttrArray[2],
                height: elemViewBoxAttrArray[3]
            };

            // creates a clone of viewBox object
            this.metrics.viewBox.rendered = Object.assign({}, this.metrics.viewBox.attr);

            console.group("Proporções");

            // gets the SVG scale relative to the initial viewBox size
            this.metrics.viewBox.scale = Math.min(
                this.metrics.width / this.metrics.viewBox.attr.width,
                this.metrics.height / this.metrics.viewBox.attr.height
            );

            // gets the scale used to scale new elements and its coordinates

            console.log("Proporção viewBox / SVG: " + this.metrics.viewBox.scale);

            console.groupEnd();

            // scales the element
            this.metrics.viewBox.rendered.width *= this.metrics.viewBox.scale;
            this.metrics.viewBox.rendered.height *= this.metrics.viewBox.scale;



            console.group("ViewBox setted vs. rendered");

            console.log(this.metrics.viewBox.attr);
            console.log(this.metrics.viewBox.rendered);

            console.groupEnd();
            
            console.groupEnd();

            console.group("Dimensões dos elementos");

            console.info("The SVG rendered size is " + this.metrics.width + " x " + this.metrics.height + " px.");

            console.info("The viewBox attribute size is " + this.metrics.viewBox.attr.width + " x " + this.metrics.viewBox.attr.height + " px.");
            console.info("The viewBox rendered size is " + this.metrics.viewBox.rendered.width + " x " + this.metrics.viewBox.rendered.height + " px.");

            console.groupEnd();

            console.group("Verificação de espaçamento entre SVG e viewBox");

            this.metrics.whiteSpace.left = (this.metrics.width - this.metrics.viewBox.rendered.width) / 2;
            this.metrics.whiteSpace.top = (this.metrics.height - this.metrics.viewBox.rendered.height) / 2;

            console.log("Há um espaço de " + this.metrics.whiteSpace.left + "px à esquerda da viewBox.");
            console.log("Há um espaço de " + this.metrics.whiteSpace.top + "px acima da viewBox.");


            console.log("Há um espaço de " + this.metrics.whiteSpace.left + "px à esquerda da viewBox.");
            console.log("Há um espaço de " + this.metrics.whiteSpace.top + "px acima da viewBox.");

            
            

            console.groupEnd();
            
            console.log(this.metrics);
        },
        /** 
         *
         */
        ondrop: function(event) {
            console.group("interac.js onDrop");

            var elemDropped = event.relatedTarget;

            console.log(event.relatedTarget);
            console.log(event.target);
            console.log(this.elem);

            if (this.elem === event.target && elemDropped.tagName === "IMG") {

                this.updateMetrics();

                console.group("Dropped elem");

                // dropped cordinates
                var elemDroppedBounding = elemDropped.getBoundingClientRect();

                var elemDroppedDistanceFrom = {};

                // position of dropped element relative to the document
                elemDroppedDistanceFrom.document = {
                    left: elemDroppedBounding.left + window.scrollX,
                    top: elemDroppedBounding.top + window.scrollY
                };

                // position of dropped element relative to SVG boundings
                elemDroppedDistanceFrom.svg = {
                    left: elemDroppedDistanceFrom.document.left - this.metrics.distanceFrom.document.left,
                    top: elemDroppedDistanceFrom.document.top - this.metrics.distanceFrom.document.top
                };
                
                console.log(elemDroppedDistanceFrom);

                console.info("O elemento foi solto à " + elemDroppedDistanceFrom.svg.left + "px da margem esquerda e " + elemDroppedDistanceFrom.svg.top + "px da margem superior do SVG.");

                console.groupEnd();

                console.group("Cáculos de escalonamento");

                elemDroppedDistanceFrom.svg.left =
                    elemDroppedDistanceFrom.svg.left / this.metrics.viewBox.scale -
                    this.metrics.whiteSpace.left / this.metrics.viewBox.scale;
                elemDroppedDistanceFrom.svg.top =
                    elemDroppedDistanceFrom.svg.top / this.metrics.viewBox.scale -
                    this.metrics.whiteSpace.top / this.metrics.viewBox.scale;

                console.groupEnd();

                var elemImage = this.createElementSVG('image');
                
                elemImage.setAttributeNS(
                    this.settings.namespace.xlink,
                    "xlink:href",
                    elemDropped.src
                );

                elemImage.setAttribute('x', elemDroppedDistanceFrom.svg.left);
                elemImage.setAttribute('y', elemDroppedDistanceFrom.svg.top);
                elemImage.setAttribute('width', elemDroppedBounding.width / this.metrics.viewBox.scale);
                elemImage.setAttribute('height', elemDroppedBounding.height / this.metrics.viewBox.scale);
                elemImage.setAttribute('preserveAspectRatio', "none");

                var svgns = "http://www.w3.org/2000/svg"

                var rect = document.createElementNS(svgns, 'rect');
                rect.setAttribute("fill", "none");
                // rect.setAttribute("fill-opacity", "0.1")
                rect.setAttribute("stroke","black");
                rect.setAttribute("stroke-width","0.01");
                
                // var left = document.getElementById('left')
                // var top = document.getElementById('top')
                // var height = document.getElementById('height')
                // var width = document.getElementById('width')
                // var id = document.getElementById('Id')

                if (this.drawArea.appendChild(elemImage)) {
                    console.info("New image successful added to SVG!");

                    var that = this;
                    rect.setAttributeNS(null, 'x', elemDroppedDistanceFrom.svg.left);
                    rect.setAttributeNS(null, 'y', elemDroppedDistanceFrom.svg.top);
                    rect.setAttributeNS(null, 'height', elemDroppedBounding.height / this.metrics.viewBox.scale);
                    rect.setAttributeNS(null, 'width', elemDroppedBounding.width / this.metrics.viewBox.scale);
                    document.getElementById('svg-dropzone').appendChild(rect);

                    that.vars[that.count].setAttribute("value", elemDropped.getAttribute("id")+' '+elemDroppedDistanceFrom.svg.left+' '+
                                                        elemDroppedDistanceFrom.svg.top+' '+elemDroppedBounding.height / this.metrics.viewBox.scale
                                                        +' '+elemDroppedBounding.width/this.metrics.viewBox.scale)
                    that.count = that.count + 1;

                    // id.setAttribute("value", elemDropped.getAttribute("id")+' '+elemDroppedDistanceFrom.svg.left)
                    // left.setAttribute("value", (elemDroppedDistanceFrom.svg.left))
                    // top.setAttribute("value", (elemDroppedDistanceFrom.svg.top))
                    // height.setAttribute("value", elemDroppedBounding.height / this.metrics.viewBox.scale)
                    // width.setAttribute("value", elemDroppedBounding.width/this.metrics.viewBox.scale )

                    
                    console.log(elemDropped.getAttribute("id"));
                    // console.log(elemDroppedDistanceFrom.svg.top);
                    // console.log(elemDroppedBounding.height / this.metrics.viewBox.scale);
                    // console.log(elemDroppedBounding.width / this.metrics.viewBox.scale);
                    // console.log(this.metrics.whiteSpace.top);              
                    interact(elemImage)
                        .draggable(interactBasicOptions.draggable)
                        .on("dragmove", function(event) {
                            var target = event.target,
                                // keep the dragged position in the data-x/data-y attributes
                                x = (parseFloat(target.getAttribute("x")) || 0) + event.dx / that.metrics.viewBox.scale,
                                y = (parseFloat(target.getAttribute("y")) || 0) + event.dy / that.metrics.viewBox.scale;

                            // add dragging class
                            target.classList.add("drag-dragging");
                            target.classList.remove("drag-dropped");

                            // update the posiion attributes
                            target.setAttribute("x", x);
                            target.setAttribute("y", y);
                            var index;
                            for(index = 0; index<that.vars.length; index++){
                                if(that.vars[index].getAttribute("value").split(" ")[0] == elemDropped.getAttribute("id")){
                                    that.vars[index].setAttribute("value", elemDropped.getAttribute("id")+' '+x+' '+y+' '+elemImage.getAttribute("height")+' '+elemImage.getAttribute("width"))
                                    break;
                                }
                            }
                            // var index = vars.indexOf(elemDropped.getAttribute("id"));
                            console.log(index)

                            rect.setAttributeNS(null, 'x', x);
                            rect.setAttributeNS(null, 'y', y);
                            rect.setAttributeNS(null, 'height', elemImage.getAttribute("height"));
                            rect.setAttributeNS(null, 'width', elemImage.getAttribute("width"));
                            document.getElementById('svg-dropzone').appendChild(rect);

                            // vars[index].setAttribute("value", elemDropped.getAttribute("id")+' '+x+' '+y+' '+elemImage.getAttribute("height")+' '+elemImage.getAttribute("width"))
                            
                            // console.log(event)
                            // left.setAttribute("value", (x))
                            // id.setAttribute("value", elemDropped.getAttribute("id"))
                            // top.setAttribute("value", (y))
                            // height.setAttribute("value", elemImage.getAttribute("height"))
                            // width.setAttribute("value", elemImage.getAttribute("width"))
                            // console.log(event)

                            console.log("Inside dragmove")
                            console.log(elemDropped.getAttribute("id"))
                            // console.log(x);
                            // console.log(y);
                            // console.log(elemDropped.getAttribute("height"));
                            // console.log(elemImage.getAttribute("width"));
                            // console.log(that.metrics.viewBox.scale)
                            // console.log(that.metrics.whiteSpace.top)
                        })
                        .resizable(interactBasicOptions.resizable)
                        .on("resizemove", function(event) {
                            var target = event.target;
                            var x = parseFloat(target.getAttribute("x")) || 0;
                            var y = parseFloat(target.getAttribute("y")) || 0;
                            
                            console.log(event)
                        
                            if (event.rect.width > 19) {
                                // update the element's size
                                target.setAttribute("width", event.rect.width / that.metrics.viewBox.scale);

                                // translate when resizing from top or left edges
                                x += event.deltaRect.left / that.metrics.viewBox.scale;
                                target.setAttribute("x", x);
                            }

                            if (event.rect.height > 19) {
                                // update the element's size
                                target.setAttribute("height", event.rect.height / that.metrics.viewBox.scale);

                                // translate when resizing from top or left edges
                                y += event.deltaRect.top / that.metrics.viewBox.scale;
                                target.setAttribute("y", y);
                            }

                            // var index = that.vars.indexOf(elemDropped.getAttribute("id"));
                            rect.setAttributeNS(null, 'x', x);
                            rect.setAttributeNS(null, 'y', y);
                            rect.setAttributeNS(null, 'height', event.rect.height / that.metrics.viewBox.scale);
                            rect.setAttributeNS(null, 'width', event.rect.width / that.metrics.viewBox.scale);
                            
                            document.getElementById('svg-dropzone').appendChild(rect);
                            var index;
                            for(index = 0; index<that.vars.length; index++){
                                if(that.vars[index].getAttribute("value").split(" ")[0] == elemDropped.getAttribute("id")){
                                    that.vars[index].setAttribute("value", elemDropped.getAttribute("id")+' '+x+' '+y+' '+elemImage.getAttribute("height")+' '+elemImage.getAttribute("width"))
                                    break;
                                }
                            }

                            // that.vars[index].setAttribute("value", elemDropped.getAttribute("id")+' '+x+' '+y
                            //                                     +' '+event.rect.height/ that.metrics.viewBox.scale
                            //                                     +' '+event.rect.width/ that.metrics.viewBox.scale)

                            console.log(elemDropped.getAttribute("id"))

                            // id.setAttribute("value", elemDropped.getAttribute("id"))
                            // left.setAttribute("value", (x))
                            // top.setAttribute("value", (y))
                            // height.setAttribute("value", event.rect.height/ that.metrics.viewBox.scale)
                            // width.setAttribute("value", event.rect.width/ that.metrics.viewBox.scale)
                            // console.log(x);
                            // console.log(y);
                            // console.log(event.rect.height/ that.metrics.viewBox.scale);// / that.metrics.viewBox.scale);
                            // console.log(event.rect.width/ that.metrics.viewBox.scale);
                            // console.log(that.metrics.whiteSpace.top)
                            
                        });


                }
            }
            

            console.groupEnd();
        },
        /**
         *
         */
        cleanHTML: function(selector) {
            document
                .querySelectorAll(selector)
                .forEach(elem => (elem.innerHTML = ""));
        },
        /**
         *
         */
        cleanDrawArea: function(selector) {
            this.drawArea.innerHTML = "";
        }
    });

    window[pluginName] = function(elem, options) {
        var response = [];

        if (typeof elem !== "object") {
            for (var i = 0; i < elem.length; ++i)
                response.push(new Plugin(elem[i], options));
        } else {
            response = new Plugin(elem, options);
        }

        return response;
    };


    // Private Functions
    var interactBasicOptions = {
        dropzone: {
            // only accept elements matching this CSS selector
            accept: ".draggable-droppable",
            // Require a 75% element overlap for a drop to be possible
            overlap: 0.75,

            // listen for drop related events:

            ondropactivate: function(event) {
                // add active dropzone feedback
                event.target.classList.add("drop-active");
            },
            ondragenter: function(event) {
                var draggableElement = event.relatedTarget,
                    dropzoneElement = event.target;

                // feedback the possibility of a drop
                dropzoneElement.classList.add("drop-target");
                draggableElement.classList.add("drag-can-drop");
                draggableElement.textContent = "Dragged in";
            },
            ondragleave: function(event) {
                // remove the drop feedback style
                event.target.classList.remove("drop-target");
                event.relatedTarget.classList.remove("drag-can-drop");
                event.relatedTarget.textContent = "Dragged out";
            },
            ondropdeactivate: function(event) {
                // remove active dropzone feedback
                event.target.classList.remove("drop-active");
                event.target.classList.remove("drop-target");
            }
        },
        draggable: {
            // enable inertial throwing
            inertia: true,
            // keep the element within the area of it's parent
            restrict: {
                restriction: "parent",
                endOnly: true,
                elementRect: {
                    top: 0,
                    left: 0,
                    bottom: 1,
                    right: 1
                }
            },
            // enable autoScroll
            autoScroll: true,
            // call this function on every dragmove event
            // onmove: {},
            // call this function on every dragend event
            onend: function(event) {
                // remove dragging class
                event.target.classList.remove("drag-dragging");
                event.target.classList.add("drag-dropped");

                console.log(
                    "moved a distance of " +
                    (Math.sqrt(event.dx * event.dx + event.dy * event.dy) | 0) + "px"
                );
                // console.log(
                //     "Current position " +
                //     (event.x) + "    " + (event.y) + "px"
                // );
            }
        },
        resizable: {
            // preserveAspectRatio: true,
            edges: {
                left: true,
                right: true,
                bottom: true,
                top: true
            }
        }
    };

})(window, document);


var svgDrawer = dragOn(document.querySelector("#svg-dropzone"), {
    listenTo: '.draggable'
});


 // target elements with the "resizable" class
interact('.resizable')
    .resizable({
        // preserveAspectRatio: true,
        edges: {
            left: true,
            right: true,
            bottom: true,
            top: true
        }
    })
    .on('resizemove', function(event) {

        svgDrawer.updateMetrics();

        var target = event.target,
            x = (parseFloat(target.getAttribute('data-x')) || 0),
            y = (parseFloat(target.getAttribute('data-y')) || 0);

        // update the element's style
        target.style.width  = event.rect.width + 'px';
        target.style.height = event.rect.height + 'px';

        // translate when resizing from top or left edges
        x += event.deltaRect.left;
        y += event.deltaRect.top;

        target.style.webkitTransform = target.style.transform =
            'translate(' + x + 'px,' + y + 'px)';

        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);
    });