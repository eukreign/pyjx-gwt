#
# Copyright (C) 2012 Rich Newpol <rich.newpol@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyjamas import DOM

from pyjamas.ui.Widget import Widget
from pyjamas.ui.FocusWidget import FocusWidget
from pyjamas.ui import Focus
from pyjamas.Canvas.Color import Color
import math
from __pyjamas__ import doc

# define compositing values - normal stacking
SOURCE_OVER = "source-over"
# reverse stacking
DESTINATION_OVER = "destination-over"

# define line-endcap types
BUTT = "butt"
ROUND = "round"
SQUARE = "square"

# define linejoin types
MITER = "miter"
ROUND = "round"
BEVEL = "bevel"


"""
SVGCanvas gradient implementation.
"""
class SVGCanvasGradient:
    # the 'factory' argument must have a _createElementSVG method
    # to create the gradient SVG element
    def __init__(self, defs_elem, elem_type, width, height):
        # save defs
        self.defs_elem = defs_elem
        # save dimensions of canvas as floats
        self.canvas_width = float(width)
        self.canvas_height = float(height)
        # create the gradient element
        self.elem = self._createElementSVG(elem_type)
        # make a unique id
        self.id = "grad"+str(DOM.getChildCount(defs_elem) + 1)
        # set the element's id
        DOM.setElemAttribute(self.elem, "id", self.id)
        # set for canvas-based coordinates
        DOM.setElemAttribute(self.elem, "gradientUnits", "userSpaceOnUse")
        # add the new element to defs
        DOM.appendChild(defs_elem, self.elem)

    # handy method to convert coordinate to canvas percentage
    def _get_svg_coord_percent(self, coordXY):
        # convert gradient coordinate to percentage
        newX = int((coordXY[0]/self.canvas_width) * 100.0)
        newY = int((coordXY[1]/self.canvas_height) * 100.0)
        # return result
        return (newX, newY)

    # add a color stop element as a child
    def addColorStop(self, offset, color):
        # create a color stop element
        stop = self._createElementSVG("stop")
        stop.setAttributeNS(None, "stop-color", color);
        # offset is specified as a float, but it should be percent
        offset = int(offset*100)
        # and it's a string
        offset = str(offset)+"%"
        stop.setAttributeNS(None, "offset", offset);
        # now add the color stop as child
        DOM.appendChild(self.elem, stop)

    # private helper to create SVG elements
    def _createElementSVG(self, name):
        return doc().createElementNS("http://www.w3.org/2000/svg", name)

    # get the 'color' specifier
    def getColor(self):
        return "url(#"+self.id+")"

# LinearGradient subclass
class SVGCanvasLinearGradient(SVGCanvasGradient):
    def __init__(self, defs_elem, width, height, x1,y1,x2,y2):
        SVGCanvasGradient.__init__(self, defs_elem, "linearGradient", width, height)
        # get coordinates in percent
        startXY = self._get_svg_coord_percent((x1,y1))
        endXY = self._get_svg_coord_percent((x2,y2))
        # set coordinates in percent
        DOM.setElemAttribute(self.elem, "x1", str(startXY[0])+"%")
        DOM.setElemAttribute(self.elem, "y1", str(startXY[1])+"%")
        DOM.setElemAttribute(self.elem, "x2", str(endXY[0])+"%")
        DOM.setElemAttribute(self.elem, "y2", str(endXY[1])+"%")

# RadialGradient subclass
class SVGCanvasRadialGradient(SVGCanvasGradient):
    def __init__(self, defs_elem, width, height, x1,y1,r1, x2,y2,r2):
        SVGCanvasGradient.__init__(self, defs_elem, "radialGradient", width, height)
        # we save the radii
        self.radii = (r1,r2)
        # convert the coordinates to SVG
        innerXY = self._get_svg_coord_percent((x1,y1))
        outerXY = self._get_svg_coord_percent((x2,y2))
        radii = self._get_svg_coord_percent((r1,r2))
        # outer circle center
        DOM.setElemAttribute(self.elem, "cx", str(outerXY[0])+"%")
        DOM.setElemAttribute(self.elem, "cy", str(outerXY[1])+"%")
        # outer circle radius
        DOM.setElemAttribute(self.elem, "r", str(radii[1])+"%")
        # inner circle center
        DOM.setElemAttribute(self.elem, "fx", str(innerXY[0])+"%")
        DOM.setElemAttribute(self.elem, "fy", str(innerXY[1])+"%")

    # add a color stop element as a child
    def addColorStop(self, offset, color):
        # 2D Canvas RadialGradient uses inner and outer circle coordinates
        # but SVG uses outer circle only. In order to simulate the inner circle,
        # we will offset the color stops according to the inner circle diameter
        # So given inner radius r, outer radius R and color stop offset s, we can
        # compute SVG color stop  P =  s(R - r) + r   /  R
        P = (offset*(self.radii[1] - self.radii[0]) + self.radii[0]) / self.radii[1]
        # pass to base to be converted to percent and added in
        SVGCanvasGradient.addColorStop(self, P, color)


"""
SVG-based canvas to mimic the capabilities available in the 2D Canvas.
API tries to be as similar as possible to the one found in GWTCanvas

NOTE: As of this writing, some browsers, notable IE may not support
rendering with this widget class. It primarily exists to workaround
canvas size limits of the 2D Canvas implementation of Windows Firefox
"""
class SVGCanvas(FocusWidget):

    def __init__(self, coordX=None, coordY=None, pixelX=None, pixelY=None,
                       **kwargs):
        """
        Creates an SVGCanvas element. Element type is 'svg'

        @param coordX the size of the coordinate space in the x direction
        @param coordY the size of the coordinate space in the y direction
        @param pixelX the CSS width in pixels of the canvas element
        @param pixelY the CSS height in pixels of the canvas element
        """

        # init default coordinates/size
        self.pixelHeight = 150
        self.pixelWidth = 300
        self.coordHeight = self.pixelHeight
        self.coordWidth = self.pixelWidth
        focusable = Focus.createFocusable()
        self.canvas = self._createElementSVG("svg")

        # create an empty defs element
        self.defs = self._createElementSVG("defs")
        # and add it to the canvas
        DOM.appendChild(self.canvas, self.defs)
        # now add canvas to container
        DOM.appendChild(focusable, self.canvas)

        # init base widget (invokes settables)
        FocusWidget.__init__(self, focusable, **kwargs)

        # since the Applier class provides settable access,
        # we only override the dimensions if user actually
        # provided them as keyword args
        if pixelX is not None:
            self.setPixelWidth(pixelX)
        if pixelY is not None:
            self.setPixelHeight(pixelY)
        if coordX is not None:
            self.setCoordWidth(coordX)
        if coordY is not None:
            self.setCoordHeight(coordY)

        # init styles context stack
        self.ctx_stack = []
        # init current context
        self._init_context()

        # insure we clear/init the canvas
        self.clear()

    # internal helper to create SVG elements
    def _createElementSVG(self, name):
        return doc().createElementNS("http://www.w3.org/2000/svg", name)

    # internal helper to add a new element to current transform group
    def _addElementSVG(self, elem):
        # if composite is layer under
        if self.ctx["composite"] == DESTINATION_OVER:
            DOM.insertChild(self.ctx["transform_group"], elem, 0)
        else:   # otherwise default (layer over)
            DOM.appendChild(self.ctx["transform_group"], elem)

    def _init_context(self):
        # initialize the default context
        self.ctx = {
                    # current graphic styles
                    "fill":"black",
                    "alpha":1.0,
                    "composite": SOURCE_OVER,
                    "stroke":"black",
                    "stroke-width":1,
                    "linecap":BUTT,
                    "linejoin":MITER,
                    "miterlimit":4,
                    "font":"12px sans-serif",
                    # current transform group
                    "transform_group":self.canvas,
                    # current transformation values
                    "matrix":[1,0,0,1,0,0]}

    # just integerize a pair of coordinates
    def _integerize(self, x,y):
        # we use int coords only
        x=int(x)
        y=int(y)
        # tuple it
        return (x,y)

    # internal method to update the current point
    # returns the int points
    def _setPoint(self, x, y):
        self.last_point = self._integerize(x,y)
        # if first move, save as first point too
        if self.first_point is None:
            self.first_point = self.last_point
        # return result
        return self.last_point

    def getCanvasElement(self):
        return self.canvas

    ###################################
    ##
    ## Canvas drawing methods
    ##
    ###################################

    def beginPath(self):
        """
        Erases the current path and prepares it for a path.
        """
        # init a new path
        self.path_string = ""
        self.first_point = None
        self.last_point = None

    def moveTo(self, x, y):
        """
        Makes the last point in the current path be <b>(x,y)</b>.

        @param x x coord of point
        @param y y coord of point
        """
        # set new current point
        self._setPoint(x,y)
        # add move to current path
        self.path_string += "M "+str(self.last_point[0])+" "+str(self.last_point[1])+" "


    def lineTo(self, x, y):
        """*
        Adds a line from the last point in the current path to the point defined by
        x and y.

        @param x x coord of point
        @param y y coord of point
        """
        # set new current point
        self._setPoint(x,y)
        # if first move, save as first point too
        if self.first_point is None:
            self.first_point = self.last_point
        self.path_string += "L "+str(self.last_point[0])+" "+str(self.last_point[1])+" "


    def clear(self):
        """
        Clears the entire canvas.
        Also deletes the context stack and current path
        TODO: NEED TO RESET STYLES?
        TODO: NEED TO RESET STYLES?
        """
        # as long as the canvas has children other than our <defs> element
        while DOM.getChildCount(self.canvas) > 1:
            # remove the second one (skip defs)
            DOM.removeChild(self.canvas, DOM.getChild(self.canvas, 1))
        # # init styles context stack
        # self.ctx_stack = []
        # # init current context
        # self._init_context()
        # also reset path
        self.beginPath()

    def cubicCurveTo(self, cp1x, cp1y, cp2x, cp2y, x, y):
        """
        Does nothing if the context's path is empty. Otherwise, it connects the
        last point in the path to the given point <b>(x, y)</b> using a cubic
        Bezier curve with control points <b>(cp1x, cp1y)</b> and <b>(cp2x,
        cp2y)</b>. Then, it must add the point <b>(x, y)</b> to the path.

        This function corresponds to the
        <code>bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y)</code> method in canvas
        element Javascript API.

        @param cp1x x coord of first Control Point
        @param cp1y y coord of first Control Point
        @param cp2x x coord of second Control Point
        @param cp2y y coord of second Control Point
        @param x x coord of point
        @param y x coord of point
        """
        # if path is empty do nothing
        if self.last_point is None: return
        # int coords only
        cp1 = self._integerize(cp1x,cp1y)
        cp2 = self._integerize(cp2x,cp2y)
        # set new current point
        self._setPoint(x,y)
        # add C to path with cntr1X cntr1Y cntr2X cntr2Y endX endY
        self.path_string += "C "+str(cp1[0])+" "+str(cp1[1])+" "+str(cp2[0])+" "+str(cp2[1])+" "+str(self.last_point[0])+" "+str(self.last_point[1])+" "

    def quadraticCurveTo(self, cpx, cpy, x, y):
        """
        Does nothing if the context has an empty path. Otherwise it connects the
        last point in the path to the given point <b>(x, y)</b> using a quadratic
        Bezier curve with control point <b>(cpx, cpy)</b>, and then adds the given
        point <b>(x, y)</b> to the path.

        @param cpx x coord of the control point
        @param cpy y coord of the control point
        @param x x coord of the point
        @param y y coord of the point
        """
        # if path is empty do nothing
        if self.last_point is None: return
        # int coords only
        cp = self._integerize(cpx,cpy)
        # set new current point
        self._setPoint(x,y)
        # add Q to path with cntlX cntrY endX endY
        self.path_string += "Q "+str(cp[0])+" "+str(cp[1])+" "+str(self.last_point[0])+" "+str(self.last_point[1])+" "

    def closePath(self):
        """
        Add the closepath command to the current path string
        """
        # if path is empty or has only one point or is already closed, do nothing
        if self.last_point is None or self.last_point == self.first_point: return
        # otherwise, add the close directive to the current path
        self.path_string += "Z "
        # and close the points
        self.last_point = self.first_point


    def fill(self):
        """
        Fills the current path according to the current fillstyle.
        """
        # if the path is empty or open we don't do anything
        if self.last_point is None or self.last_point != self.first_point: return
        # if fill style is None we don't do anything
        if self.ctx["fill"] is None: return
        # create a path element
        path = self._createElementSVG("path")
        # add the current path draw string
        DOM.setElemAttribute(path, "d", self.path_string)
        # add the current fill style attribute
        DOM.setElemAttribute(path, "fill", str(self.ctx["fill"]))
        # set fill opacity
        if self.ctx["alpha"] < 1.0:
            DOM.setElemAttribute(path, "fill-opacity", str(self.ctx["alpha"]))
        # no stroke
        DOM.setElemAttribute(path, "stroke", "transparent")
        # add the path element to the canvas
        self._addElementSVG(path)


    # helper to apply current stroke styles
    def _apply_stroke_styles(self, elem):
        # add the current stroke style attribute
        DOM.setElemAttribute(elem, "stroke", str(self.ctx["stroke"]))
        # add the current stroke width attribute
        DOM.setElemAttribute(elem, "stroke-width", str(self.ctx["stroke-width"]))
        # add the current stroke linecap attribute
        DOM.setElemAttribute(elem, "stroke-linecap", str(self.ctx["linecap"]))
        # add the current stroke linejoin attribute
        DOM.setElemAttribute(elem, "stroke-linejoin", str(self.ctx["linejoin"]))
        # if using MITER
        if self.ctx["linejoin"] == MITER:
            # add the current stroke miterlimit attribute
            DOM.setElemAttribute(elem, "stroke-miterlimit", str(self.ctx["miterlimit"]))
        # add the current stroke opacity attribute
        if self.ctx["alpha"] < 1.0:
            DOM.setElemAttribute(elem, "stroke-opacity", str(self.ctx["alpha"]))

    def stroke(self):
        """
        Strokes the current path according to the current stroke style.
        """
        # if the path is empty we don't do anything
        if self.last_point is None: return
        # if stroke style is None or width is 0 we don't do anything
        if self.ctx["stroke"] is None or self.ctx["stroke-width"] == 0: return
        # create a path element
        path = self._createElementSVG("path")
        # add the current path draw string
        DOM.setElemAttribute(path, "d", self.path_string)
        # apply stroke styles
        self._apply_stroke_styles(path)
        # no fill
        DOM.setElemAttribute(path, "fill", "transparent")
        # add the path element to the canvas
        self._addElementSVG(path)

    # helper to normalize an angle to be 0 <= a <= 2pi
    def _posAngle(self, angle):
        twoPi = math.pi * 2
        while angle < 0: angle += twoPi
        # now that it's positive, make sure it's in range 0 - 2pi
        while angle > twoPi: angle -= twoPi
        # done
        return angle

    def arc(self, centerX, centerY, radius, startAngle, endAngle, antiClockwise):
        """
        Draws an arc (circle segment).

        @param x center X coordinate
        @param y center Y coordinate
        @param radius radius of drawn arc
        @param startAngle angle measured from positive X axis to start of arc CW
        @param endAngle angle measured from positive X axis to end of arc CW
        @param antiClockwise direction that the arc line is drawn
        """
        # SVG Path A parms: A(rx ry x-axis-rotation large-arc-flag sweep-flag x y)
        # draw an elliptical arc from current point to x,y where:
        #   rx = ry = radius of circle
        #   x-axis-rotation = 0 (for a circle, not an ellipse)
        #   large-arc-flag is 1 if arc sweep is > 180 degrees
        #   sweep-flag is 1 if we are drawing antiClockwise

        # first we need the start point
        startX = int(centerX + (radius * math.cos(startAngle)))
        startY = int(centerY + (radius * math.sin(startAngle)))
        # and the end point
        endX = int(centerX + (radius * math.cos(endAngle)))
        endY = int(centerY + (radius * math.sin(endAngle)))
        # compute the sweep angle
        sweepAngle = self._posAngle(endAngle - startAngle)

        # SPECIAL CASE: if this is a circle (or almost one)
        if sweepAngle < 0.01 or sweepAngle > 6.27:
#            print "CIRCLE at:",centerX,centerY
            # we split this into two path Arcs
            self.arc(centerX, centerY, radius, 0, math.pi, antiClockwise)
            self.arc(centerX, centerY, radius, math.pi, 0, antiClockwise)
            # close the circle
            self.moveTo(startX,startY)
            # and close it
            self.closePath()
            return
        # otherwise it's a partial circle so we continue here
        self.moveTo(startX,startY)
        # determine whether large or small sweep assuming clockwise sweep
        largeSweep = sweepAngle > math.pi
        # flip it if CCW
        if antiClockwise:   # counter clockwise sweep
            largeSweep = not largeSweep
        # now draw
#        print "ARC from:",startX,startY,"to",endX,endY,"through",sweepAngle,"CCW:",antiClockwise,"Large:",largeSweep
        self.path_string += "A"+str(radius)+","+str(radius)+" 0 "+ str(int(largeSweep))+","+str(int(not antiClockwise))+" "+str(endX)+","+str(endY)+" "

    # helper for creating SVG rect elements
    def _make_rect(self, startX, startY, width, height):
        # create a rect element
        rect = self._createElementSVG("rect")
        # integerize the coordinates
        xy = self._integerize(startX, startY)
        wh = self._integerize(width, height)
        # add the size and position
        DOM.setElemAttribute(rect, "x", str(xy[0]))
        DOM.setElemAttribute(rect, "y", str(xy[1]))
        DOM.setElemAttribute(rect, "width", str(wh[0]))
        DOM.setElemAttribute(rect, "height", str(wh[1]))
        # return the element
        return rect

    def fillRect(self, startX, startY, width, height):
        """
        Fills a rectangle of the specified dimensions, at the specified start
        coords, according to the current fillstyle.

        @param startX x coord of the top left corner in the destination space
        @param startY y coord of the top left corner in the destination space
        @param width destination width of image
        @param height destination height of image
        """
        # if fill style is None we don't do anything
        if self.ctx["fill"] is None: return
        # create a rect element
        rect = self._make_rect(startX, startY, width, height)
        # add the current fill style attribute
        DOM.setElemAttribute(rect, "fill", str(self.ctx["fill"]))
        # set fill opacity
        if self.ctx["alpha"] < 1.0:
            DOM.setElemAttribute(rect, "fill-opacity", str(self.ctx["alpha"]))
        # no stroke
        DOM.setElemAttribute(rect, "stroke", "transparent")
        # add the rect element to the canvas
        self._addElementSVG(rect)

    def strokeRect(self, startX, startY, width, height):
        """
        Strokes a rectangle defined by the supplied arguments.

        @param startX x coord of the top left corner
        @param startY y coord of the top left corner
        @param width width of the rectangle
        @param height height of the rectangle
        """
        # if stroke style is None or width is 0 we don't do anything
        if self.ctx["stroke"] is None or self.ctx["stroke-width"] == 0: return
        # create a rect element
        rect = self._make_rect(startX, startY, width, height)
        # apply stroke styles
        self._apply_stroke_styles(rect)
        # no fill
        DOM.setElemAttribute(rect, "fill", "transparent")
        # add the rect element to the canvas
        self._addElementSVG(rect)

    def rect(self, startX, startY, width, height):
        """*
        Adds an unfilled/stroked rectangle to the current path, and closes the path.

        @param startX x coord of the top left corner of the rectangle
        @param startY y coord of the top left corner of the rectangle
        @param width the width of the rectangle
        @param height the height of the rectangle
        """
        # add a rectangle to the current path
        self.moveTo(startX, startY)
        self.lineTo(startX+width, startY)
        self.lineTo(startX+width, startY+height)
        self.lineTo(startX, startY+height)
        self.closePath()


    def fillText(self, text, startX, startY, maxWidth=None):
        """
        Places text, at the specified start
        coords, according to the current fillstyle.

        @param startX x coord of the top left corner in the destination space
        @param startY y coord of the top left corner in the destination space
        @param maxWidth maximum width of text
        """
        # create an SVG text element
        text_elem = self._createElementSVG("text")
        # integerize the coordinates
        xy = self._integerize(startX, startY)
        # add the size and position
        DOM.setElemAttribute(text_elem, "x", str(xy[0]))
        DOM.setElemAttribute(text_elem, "y", str(xy[1]))
        if maxWidth is not None:
            DOM.setElemAttribute(text_elem, "textLength", str(maxWidth))
        # add the fill styles
        style = "font:"+self.ctx["font"]+";fill:"+str(self.ctx["fill"])
        DOM.setElemAttribute(text_elem, "style", style)
        # now add the text
        DOM.setInnerText(text_elem, text)
        # add the rect element to the canvas
        self._addElementSVG(text_elem)


    def createLinearGradient(self, x0, y0, x1, y1):
        """
        Creates a LinearGradient Object for use as a fill or stroke style.

        @param x0 x coord of start point of gradient
        @param y0 y coord of start point of gradient
        @param x1 x coord of end point of gradient
        @param y1 y coord of end point of gradient
        @return returns the CanvasGradient
        """
        # create a LinearGradient element
        return SVGCanvasLinearGradient(self.defs, self.pixelWidth, self.pixelHeight,
                                        int(x0),int(y0),
                                        int(x1),int(y1))


    def createRadialGradient(self, x0, y0, r0, x1, y1, r1):
        """
        Creates a RadialGradient Object for use as a fill or stroke style.

        @param x0 x coord of origin of start circle
        @param y0 y coord of origin of start circle
        @param r0 radius of start circle
        @param x1 x coord of origin of end circle
        @param y1 y coord of origin of end circle
        @param r1 radius of the end circle
        @return returns the CanvasGradient
        """
        # create a RadiualGradient element
        return SVGCanvasRadialGradient(self.defs, self.pixelWidth, self.pixelHeight,
                                        int(x0),int(y0),int(r0),
                                        int(x1),int(y1),int(r1))


    def drawImage(self, img, *args):
        """
        Draws an input image at a given position on the canvas. Resizes image
        according to specified width and height and samples from the specified
        sourceY and sourceX.

        We recommend that the pixel and coordinate spaces be the same to provide
        consistent positioning and scaling results

        option 1:
        @param img the image to be drawn
        @param destX x coord of the top left corner in the destination space
        @param destY y coord of the top left corner in the destination space

        option 2:
        @param img The image to be drawn
        @param destX x coord of the top left corner in the destination space
        @param destY y coord of the top left corner in the destination space
        @param destWidth the width of drawn image in the destination
        @param destHeight the height of the drawn image in the destination

        option 3:
        @param img the image to be drawn
        @param sourceX the start X position in the source image
        @param sourceY the start Y position in the source image
        @param sourceWidth the width in the source image you want to sample
        @param sourceHeight the height in the source image you want to sample
        @param destX x coord of the top left corner in the destination space
        @param destY y coord of the top left corner in the destination space
        @param destWidth the width of drawn image in the destination
        @param destHeight the height of the drawn image in the destination
        """
        # create an image element:
        # <image xlink:href="firefox.jpg" x="0" y="0" height="50px" width="50px"/>
        # The way to do this is to create a clipping container and place the image inside that,
        # using scaling and positioning to approximate some of the effect of sourceXY and destXY
        # for now, we ignore all this
        #
        # get the image size and URL - image may be a Image Widget or an <img> Element
        if isinstance(img, Widget):     # Image widget
            img_elem = img.getElement()
            url = img.getUrl()
        else:   # <img> element
            img_elem = img
            url = DOM.getAttribute(img, "src")
        # determine all parms
        sourceXY = None
        sourceWH = None
        destXY = None
        destWH = None
        # get the parms that are specified
        if len(args) == 8:  # all parms specified
            sourceXY = (args[0], args[1])
            sourceWH = (args[2], args[3])
            destXY = (args[4], args[5])
            destWH = (args[6], args[7])
        elif len(args) == 4:    # only destXY and destWH are specified
            destXY = (args[0], args[1])
            destWH = (args[2], args[3])
        elif len(args) == 2:    # we just get destXY
            destXY = (args[0], args[1])
            # by default we keep the same size
            destWH = (img_elem.width, img_elem.height)
        else:
            raise TypeError("Wrong number of arguments for SVGCanvas.drawImage")

        # sourceWH and destWH determine the scaling
        # sourceXY and scaling determine where to place the image inside the clipping container
        # destXY determines where to place the clipping container

        # for now just create an SVG image element:
        # <image xlink:href="firefox.jpg" x="0" y="0" height="50px" width="50px"/>
#        print 'Create: <image xlink:href="'+url+'" x="'+str(destXY[0])+'" y="'+str(destXY[1])+'" height="'+str(destWH[1])+'px" width="'+str(destWH[0])+'px"/>'
        image = self._createElementSVG("image")
        # set the URL
        image.setAttributeNS("http://www.w3.org/1999/xlink", "xlink:href", url);
        # set the pos/dimensions
        DOM.setElemAttribute(image, "x", str(int(destXY[0])))
        DOM.setElemAttribute(image, "y", str(int(destXY[1])))
        DOM.setElemAttribute(image, "width", str(int(destWH[0])))
        DOM.setElemAttribute(image, "height", str(int(destWH[1])))
        # add the element to the canvas
        self._addElementSVG(image)


    def saveContext(self):
        """
        Saves the current context to the context stack.
        """
        # just copy the current context and save it
        self.ctx_stack.append(dict(self.ctx))
#        print "SAVED:",self.ctx


    def restoreContext(self):
        """
        Restores the last saved context from the context stack.
        """
        # if context stack is empty, NOP
        if len(self.ctx_stack) == 0:
#            print "Empty RESTORE"
            return
        # otherwise, pop a dict of styles
        self.ctx = self.ctx_stack.pop()
#        print "RESTORED:",self.ctx


    ###################################
    ##
    ## Canvas drawing styles
    ##
    ###################################

    def getLineCap(self):
        """
        See self.setter method for a fully detailed description.

        @return
        @see GWTCanvas#setLineCap(String)
        """
        return self.ctx["linecap"]

    def setLineCap(self, lineCap):
        """
        A string value that determines the end style used when drawing a line.
        Specify the string <code>GWTCanvas.BUTT</code> for a flat edge that is
        perpendicular to the line itself, <code>GWTCanvas.ROUND</code> for round
        endpoints, or <code>GWTCanvas.SQUARE</code> for square endpoints. If you do
        not self.set this value explicitly, the canvas uses the
        <code>GWTCanvas.BUTT</code> line cap style.

        @param lineCap
        """
        self.ctx["linecap"] = lineCap


    def getLineJoin(self):
        """
        See self.setter method for a fully detailed description.

        @return
        @see GWTCanvas#setLineJoin(String)
        """
        return self.ctx["linejoin"]


    def setLineJoin(self, lineJoin):
        """
        A string value that determines the join style between lines. Specify the
        string <code>GWTCanvas.ROUND</code> for round joins,
        <code>GWTCanvas.BEVEL</code> for beveled joins, or
        <code>GWTCanvas.MITER</code> for miter joins. If you do not self.set this value
        explicitly, the canvas uses the <code>GWTCanvas.MITER</code> line join
        style.

        @param lineJoin
        """
        self.ctx["linejoin"] = lineJoin


    def getLineWidth(self):
        """
        See self.setter method for a fully detailed description.

        @return
        @see GWTCanvas#setLineWidth(double)
        """
        return self.ctx["stroke-width"]


    def setLineWidth(self, width):
        """
        Sets the current context's linewidth. Line width is the thickness of a
        stroked line.

        @param width the width of the canvas
        """
        self.ctx["stroke-width"] = int(width)


    def getMiterLimit(self):
        """
        See self.setter method for a fully detailed description.

        @return
        @see GWTCanvas#setMiterLimit(double)
        """
        return self.ctx["miterlimit"]

    def setMiterLimit(self, miterLimit):
        """
        A double value with the miter limit. You use this property to specify
        how the canvas draws the juncture between connected line segments. If the
        line join is self.set to <code>GWTCanvas.MITER</code>, the canvas uses the miter
        limit to determine whether the lines should be joined with a bevel instead
        of a miter. The canvas divides the length of the miter by the line width.
        If the result is greater than the miter limit, the style is converted to a
        bevel.

        @param miterLimit
        """
        self.ctx["miterlimit"] = miterLimit


    def setStrokeStyle(self, grad):
        """
        Set the current Stroke Style to the specified color gradient.

        @param grad {@link CanvasGradient}
        """
        # if this is an actual Gradient
        if isinstance(grad, SVGCanvasGradient):
            # get the ref sting to use for the fill attribute value
            grad = grad.getColor()
        # now save the value
        self.ctx["stroke"] = grad


    def setBackgroundColor(self, color):
        """
        Sets the background color of the canvas element.

        @param color the background color.
        """
        # set style value
        style="background-color: "+str(color)+";"
        # set the canvas background color with the style attribute
        DOM.setElemAttribute(self.canvas, "style", style)


    def getGlobalAlpha(self):
        """
        See self.setter method for a fully detailed description.
        """
        return self.ctx["alpha"]

    def setGlobalAlpha(self, alpha):
        """
        Set the global transparency to the specified alpha.

        @param alpha alpha value
        """
        self.ctx["alpha"] = alpha


    def getGlobalCompositeOperation(self):
        """
        See self.setter method for a fully detailed description.

        @return
        @see GWTCanvas#setGlobalCompositeOperation(String)
        """
        return self.ctx["composite"]


    def setGlobalCompositeOperation(self, globalCompositeOperation):
        """
        Determines how the canvas is displayed relative to any background content.
        The string identifies the desired compositing mode. If you do not self.set this
        value explicitly, the canvas uses the <code>GWTCanvas.SOURCE_OVER</code>
        compositing mode.
        <p>
        The valid compositing operators are:
        <ul>
        <li><code>GWTCanvas.SOURCE_OVER</code>
        <li><code>GWTCanvas.DESTINATION_OVER</code>
        </ul>
        <p>

        @param globalCompositeOperation is False for SOURCE_OVER (default) and True for SOURCE_UNDER
        """
        self.ctx["composite"] = globalCompositeOperation


    def setFillStyle(self, grad):
        """
        Set the current Fill Style to the specified color/gradient.

        @param grad {@link CanvasGradient}
        """
        # if this is an actual Gradient
        if isinstance(grad, SVGCanvasGradient):
            # get the ref string to use for the fill attribute value
            grad = grad.getColor()
        # now save the value
        self.ctx["fill"] = grad

    # set the font to use for fillText
    # argument is the CSS font specification
    def setFont(self, font):
        self.ctx["font"] = font

    ###################################
    ##
    ## Canvas Coordinate space
    ##
    ###################################

    def setWidth(self, width):
        self.setPixelWidth(width)

    def setHeight(self, height):
        self.setPixelHeight(height)

    def resize(self, width, height):
        """
        Convenience function for resizing the canvas with consistent coordinate and
        screen pixel spaces. Equivalent to doing:

        <pre><code>
        canvas.setCoordSize(width, height)
        canvas.setPixelHeight(height)
        canvas.setPixelWidth(width)
        </code></pre>

        @param width
        @param height
        """
        self.setCoordSize(width, height)
        self.setPixelHeight(height)
        self.setPixelWidth(width)


    def setCoordSize(self, width, height):
        """
        Sets the coordinate space of the Canvas.

        @param width the size of the x component of the coordinate space
        @param height the size of the y component of the coordinate space
        """
        self.setCoordWidth(width)
        self.setCoordHeight(height)


    def getCoordHeight(self):
        """
        Returns the height in pixels of the canvas.

        @return returns the height in pixels of the canvas
        """
        return self.coordHeight


    def setCoordHeight(self, height):
        """
        Sets the coordinate height of the Canvas.
        <p>
        This will erase the canvas contents!
        </p>

        @param height the size of the y component of the coordinate space
        """
        self.coordHeight = int(height)
        self._set_base_transform()

    def getCoordWidth(self):
        """
        Returns the width in pixels of the canvas.

        @return returns the width in pixels of the canvas
        """
        return self.coordWidth

    def setCoordWidth(self, width):
        """
        Sets the coordinate width of the Canvas.
        <p>
        This will erase the canvas contents!
        </p>

        @param width the size of the x component of the coordinate space
        """
        self.coordWidth = int(width)
        self._set_base_transform()


    def setPixelHeight(self, height):
        """
        Sets the CSS height of the canvas in pixels.

        @param height the height of the canvas in pixels
        """
        height = int(height)
        self.pixelHeight = height
        FocusWidget.setHeight(self, height)
        DOM.setElemAttribute(self.canvas, "height", str(height))
        self._set_base_transform()


    def setPixelWidth(self, width):
        """
        Sets the CSS width in pixels for the canvas.

        @param width width of the canvas in pixels
        """
        width = int(width)
        self.pixelWidth = width
        FocusWidget.setWidth(self, width)
        DOM.setElemAttribute(self.canvas, "width", str(width))
        self._set_base_transform()


    # internal routine to set the current scaling transform
    def _set_base_transform(self):
        # clear any content
        self.clear()
        # set viewBox
        DOM.setElemAttribute(self.canvas, "viewBox", "0 0 "+str(self.coordWidth)+" "+str(self.coordHeight))

    ###################################
    ##
    ## Transformations
    ##
    ## Invoking any of the transformation methods, updates/creates the transformation group
    ## which acts as the parent element for any SVG graphic elements added to the canvas
    ##
    ###################################

    # does a 3x3 matrix multiply [t] x [m] assuming last row 0,0,1
    # and returns the result vector, where any matrix:
    #       a c e
    #       b d f
    #       0 0 1
    # is specified as [a,b,c,d,e,f]
    #
    def _matrix_mult(self, t, m):
        # compute product [x11,x21,x12,x22,x13,x23]
        # x11 = t[0]*m[0] + t[2]*m[1] + t[4]*m[6]
        # x21 = t[1]*m[0] + t[3]*m[1] + t[5]*m[6]
        # x12 = t[0]*m[2] + t[2]*m[3] + t[4]*m[7]
        # x22 = t[1]*m[2] + t[3]*m[3] + t[5]*m[7]
        # x13 = t[0]*m[4] + t[2]*m[5] + t[4]*m[8]
        # x23 = t[1]*m[4] + t[3]*m[5] + t[5]*m[8]
        # which reduces (since last row is always 0,0,1) to:
        x11 = t[0]*m[0] + t[2]*m[1]
        x21 = t[1]*m[0] + t[3]*m[1]
        x12 = t[0]*m[2] + t[2]*m[3]
        x22 = t[1]*m[2] + t[3]*m[3]
        x13 = t[0]*m[4] + t[2]*m[5] + t[4]
        x23 = t[1]*m[4] + t[3]*m[5] + t[5]
        # so return the resulting transform
        return [x11,x21,x12,x22,x13,x23]

    # this helper applies the current set of transforms, either by
    # rewriting the transformation attribute of the current (empty) group,
    # or by creating a new group with the current transforms
    def _apply_current_transforms(self):
        # if the current transform group already has elements
        if DOM.getChildCount(self.ctx["transform_group"]) > 0:
            # we create a new one
            group = self._createElementSVG("g")
            # add a new transform group to the canvas
            DOM.appendChild(self.canvas, group)
            # and make it the current tranform group
            self.ctx["transform_group"] = group
        # build the transform spec
        # just to make the next line shorter
        mx = self.ctx["matrix"]
        transform = "matrix("+str(mx[0])+","+str(mx[1])+","+str(mx[2])+","+str(mx[3])+","+str(mx[4])+","+str(mx[5])+") "
        # we need to update the transform attribute of the current group
#        print "Apply transform:",transform
        DOM.setElemAttribute(self.ctx["transform_group"], "transform", transform)


    def transform(self, m11, m12, m21, m22, dx, dy):
        """
        <code>The transform(m11, m12, m21, m22, dx, dy)</code> method must multiply
        the current transformation matrix with the input matrix. Input described
        by:

        m11   m21   dx
        m12   m22   dy
        0      0     1

        @param m11 top left cell of 2x2 rotation matrix
        @param m12 top right cell of 2x2 rotation matrix
        @param m21 bottom left cell of 2x2 rotation matrix
        @param m22 bottom right cell of 2x2 rotation matrix
        @param dx Translation in X direction
        @param dy Translation in Y direction
        """
        # TODO: multiply the transform with the current transform
        print "transform NOT IMPLEMENTED YET"

    def rotate(self, angle):
        """
        Adds a rotation of the specified angle to the current transform.

        @param angle the angle to rotate by, <b>in radians</b>
        """
        # first get current transform (leave off last row 0,0,1)
        t = self.ctx["matrix"]
        # get trig
        s = math.sin(angle)
        c = math.cos(angle)
        # build rotation transform (leave off last row 0,0,1)
        m = [c,s,-s,c,0,0]
        self.ctx["matrix"] = self._matrix_mult(t,m)
        # apply the current transforms
        self._apply_current_transforms()


    def scale(self, x, y):
        """
        Adds a scale transformation to the current transformation matrix.

        @param x ratio that we must scale in the X direction
        @param y ratio that we must scale in the Y direction
        """
        # first get current transform (leave off last row 0,0,1)
        t = self.ctx["matrix"]
        # build scaling transform (leave off last row 0,0,1)
        m = [x,0,0,y,0,0]
        self.ctx["matrix"] = self._matrix_mult(t,m)
        # apply the current transforms
        self._apply_current_transforms()


    def translate(self, x, y):
        """
        Applies a translation (linear shift) by x in the horizontal and by y in the
        vertical.

        @param x amount to shift in the x direction
        @param y amount to shift in the y direction
        """
        xy = self._integerize(x,y)
#        print "Translating:",self.ctx["matrix"],"(",x,",",y,")"
        # since last two elements in transform matrix are the x,y translation
        # all we have to do is add the new translation ot the existing values
        # first get current transform (leave off last row 0,0,1)
        t = self.ctx["matrix"]
        # build translate transform (leave off last row 0,0,1)
        m = [1,0,0,1,xy[0],xy[1]]
        self.ctx["matrix"] = self._matrix_mult(t,m)
#        print "Translated:",self.ctx["matrix"]
        # apply the current transforms
        self._apply_current_transforms()
