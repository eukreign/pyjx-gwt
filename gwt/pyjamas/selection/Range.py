"""
Generic implementation of the Range object, using the W3C standard
implemented by Firefox, Safari, and Opera.

@author John Kozura

Copyright 2010 John Kozura

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at

http:#www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""


from pyjamas import DOM

from RangeEndPoint import RangeEndPoint
import RangeUtil

import random

# For use in compareBoundaryPoint, which end points to compare
START_TO_START	= 0
START_TO_END	= 1
END_TO_END	= 2
END_TO_START	= 3

BOUNDARY_STRINGS = [ "StartToStart", "StartToEnd", "EndToEnd", "EndToStart"]
# Used for deleting/replacing values of a range
REPLACING_STRING = "DeL3EteTh1s"


m_lastDocument = None # used in ie6
m_testElement = None # used in ie6




def getIntProp(obj, propertyName):
    """
    Reads an object's property as an integer value.

    @param object The object
    @param propertyName The name of the property being read
    @return The value
    """
    DOM.getIntAttribute(obj, propertyName)


def getProperty(obj, propertyName):
    """
    Reads an object given a property and returns it as a JavaScriptObject

    @param object
    @param propertyName
    @return the object
    """
    DOM.getAttribute(obj, propertyName)


def cloneRange(rng):
    """
    Make a copy of the given js range; the JS range is decoupled from any
    changes.

    @param range a js range to copy
    @return a full copy of the range
    """
    return rng.cloneRange()


def collapse(rng, start):
    """
    Collapse a JS range object to the start or end point

    @param range js range to collapse
    @param start if True, collapse to start, otherwise to end
    """
    rng.collapse(start)


def compareBoundaryPoint(rng, compare, how):
    """
    Compare endpoints of 2 ranges, returning -1, 0, or 1 depending on whether
    the compare endpoint comes before, at, or after the range endpoint.

    @param range range to compare against
    @param compare range to compare
    @param how a constant to choose which endpoint of each range to compare,
           i.e. Range.START_TO_END
    @return -1, 0, or 1 depending on order of the 2 ranges
    """
    return rng.compareBoundaryPoints(compare, how)


def copyContents(rng, copyInto):
    """
    Copy the contents of the range into the given element, including any
    tags needed to make it complete.  The DOM is not changed.

    @param range js range to copy contents out of.
    @param copyInto an element to copy these contents into
    """
    copyInto.appendChild(rng.cloneContents())


def createFromDocument(doc):
    """
    Create an empty JS range from a document

    @param doc DOM document
    @return a empty JS range
    """
    return doc.createRange()


def createRange(doc, startPoint, startOffset, endPoint, endOffset):
    """
    Create a JS range with the given endpoints

    @param startPoint Start text of the selection
    @param startOffset offset into start text
    @param endPoint End text of the selection
    @param endOffset offset into end text
    @return A javascript object of this range
    """
    rng = doc.createRange()
    rng.setStart(startPoint, startOffset)
    rng.setEnd(endPoint, endOffset)

    return rng;


def deleteContents(rng):
    """
    Remove the contents of the js range from the DOM

    @param range js range to remove
    """
    rng.deleteContents()


def extractContents(rng, copyInto):
    """
    Extract the contents of the range into the given element, removing them
    from the DOM.  Any tags needed to make the contents complete are included.
    Element object ids are not maintained.

    @param range js range to extract contents from
    @param copyInto an element to extract these contents into
    """
    copyInto.appendChild(rng.extractContents())


def fillRangePoints(fillRange):
    """
    Fill the start and end point of a Range object, using the javascript
    range.

    @param fillRange range object to set the endpoints of
    """
    jsRange = fillRange._getJSRange()

    startNode = jsRange.startContainer
    startOffset = jsRange.startOffset
    #print "jsRange", jsRange
    #print "startNode", startNode
    #print "startOffset", startOffset
    #print dir(jsRange)
    startPoint = findTextPoint(startNode, startOffset)

    endNode = jsRange.endContainer
    endOffset = jsRange.endOffset
    endPoint = findTextPoint(endNode, endOffset)

    fillRange._setRange(startPoint, endPoint)


def getCommonAncestor(rng):
    """
    Get lowest common ancestor element of the given js range

    @param range js range to get ancestor element of
    @return the lowest element that completely encompasses the range
    """
    return rng.commonAncestorContainer


def getHtmlText(rng):
    """
    Get the complete html fragment enclosed by this range.  Ensures that all
    opening and closing tags are included.

    @param range js range to get the html of
    @return an html string of the range
    """
    parent = DOM.createElement("span")
    copyContents(rng, parent)
    return DOM.getInnerHTML(parent)

def getText(rng):
    """
    Get the pure text that is included in a js range

    @param range js range to get the text of
    @return string of the range's text
    """
    return rng.toString()


def surroundContents(rng, copyInto):
    """
    Surround the contents of the range with the given element, and put the
    element in their place.  Any tags needed to make the contents complete
    are included.  Element object ids are not maintained.

    @param range js range to surround with this element
    @param copyInto element to surround the range's contents with
    """
    DOM.appendChild(copyInto, rng.extractContents())
    rng.insertNode(copyInto)


def findTextPoint(node, offset):
    """
    If the found range is not on a text node, this finds the cooresponding
    text node to where the selection is.  If it is on a text node, just
    directly creates the endpoint from it.

    @param node node returned as an endpoint of a range
    @param offset offset returned to the endpoint of a range
    @return A range end point with a proper (or None) text node
    """
    if DOM.getNodeType(node) == DOM.TEXT_NODE:
        res = RangeEndPoint(node, offset)
    else:
        # search backwards unless this is after the last node
        dirn = offset >= DOM.getChildCount(node)
        child = (DOM.getChildCount(node) == 0) and node or \
            DOM.getChild(node, dirn and (offset - 1) or offset)
        # Get the previous/next text node
        text = RangeUtil.getAdjacentTextElement(child, dirn)
        if text is None:
            # If we didn't find a text node in the preferred direction,
            # try the other direction
            dirn = not dirn
            text = RangeUtil.getAdjacentTextElement(child, dirn)

        res = RangeEndPoint(text, dirn)

    return res


"""
Implements a text range in a Document, everything between two RangeEndPoints.
Works with both a (browser dependent) javascript range object, and with
the java RangeEndPoint objects, building one or the other as needed on
demand.

@author John Kozura
"""
class Range:
    def getSelectedTextElements(self, startNode=None, endNode=None):
        """
        Returns all text nodes between (and including) two arbitrary text nodes.
        Caller must ensure startNode comes before endNode.

        @param startNode start node to traverse
        @param endNode end node to finish traversal
        @return A list of all text nodes between these two text nodes
        """
        if startNode is None and endNode is None:
            startNode = self.m_startPoint.getTextNode()
            endNode = self.m_endPoint.getTextNode()

        res = []

        #print "getSelectedTextElements", startNode, endNode

        current = startNode
        while (current is not None) and (not DOM.compare(current, endNode)):
            res.append(current)

            current = RangeUtil.getAdjacentTextElement(current, None, True, False)

        if current is None:
            # With the old way this could have been backwards, but should not
            # happen now, so this is an error
            res = None
        else:
            res.append(current)

        return res


    def __init__(self, arg1, arg2=None):
        """
        Creates an empty range on this document

        @param doc Document to create an empty range in

        Creates a range that encompasses the given element

        @param element Element to create a range around

        Creates a range that is a cursor at the given location

        @param cursorPoint a single point to make a cursor range

        Create a range that extends between the given points.  Caller must
        ensure that end comes after start

        @param startPoint start point of the range
        @param endPoint end point of the range

        Internal method for creating a range from a JS object

        @param document
        @param rangeObj
        """
        #print "range", arg1, arg2
        #print dir(arg1)
        self.m_startPoint = None
        self.m_endPoint = None
        self.m_range = None
        if isinstance(arg1, RangeEndPoint):
            if arg2 and isinstance(arg2, RangeEndPoint):
                self.setRange(arg1, arg2)
            else:
                self.setCursor(arg1)
        elif arg2 is not None:
            self.m_document = arg1
            self.m_range = arg2
        else:
            if hasattr(arg1, "nodeType") and \
                    arg1.nodeType == DOM.DOCUMENT_NODE:
                self.setDocument(arg1)
            else:
                self.setRange(arg1)

    def _getJSRange(self):
        """
        Internal function for retrieving the range, external callers should NOT
        USE THIS

        @return
        """
        return self.m_range


    def _setRange(self, startPoint, endPoint):
        """
        Internal call to set the range, which skips some checks and settings
        this SHOULD NOT be used externally.

        @param startPoint
        @param endPoint
        """
        self.m_document = startPoint and startPoint.getNode().ownerDocument
        self.m_startPoint = startPoint
        self.m_endPoint = endPoint


    def collapse(self, start):
        """
        Collapses the range into a cursor, either to the start or end point

        @param start if True, cursor is the start point, otherwise the end point
        """
        if self.m_range is not None:
            collapse(self.m_range, start)
            self.m_startPoint = None

        elif start:
            self.m_endPoint = self.m_startPoint
        else:
            self.m_startPoint = self.m_endPoint



    def compareBoundaryPoint(self, compare, how):
        """
        Compares an endpoint of this range with an endpoint in another range,
        returning -1, 0, or 1 depending whether the comparison endpoint comes
        before, at, or after this endpoint.  how is a constant determining which
        endpoints to compare, for example Range.START_TO_START.

        @param compare Range to compare against this one.
        @param how constant indicating which endpoints to compare
        @return -1, 0, or 1 indicating relative order of the endpoints
        """
        self.ensureRange()
        self.compare.ensureRange()

        return compareBoundaryPoint(self.m_range, self.getJSRange(), how)


    def copyContents(self, copyInto):
        """
        Make a copy of the contents of this range, into the given element.  All
        tags required to make the range complete will be included

        @param copyInto an element to copy the contents into, ie
                        DOM.createSpanElement()
        """
        self.ensureRange()
        copyContents(self.m_range, copyInto)


    def deleteContents(self):
        """
        Remove the contents of this range from the DOM.
        """
        self.ensureRange()
        deleteContents(self.m_range)


    def equals(self, obj):
        res = False

        try:
            cm = obj

            ensureEndPoints()
            cm.ensureEndPoints()
            res = (cm == this)  or  \
                        (self.m_startPoint.equals(cm.getStartPoint())  and  \
                        self.m_endPoint.equals(cm.getEndPoint()))
        except:
            pass

        return res


    def extractContents(self):
        """
        Place the contents of this range into a SPAN element, removing them
        from the DOM.  All tags required to make the range complete will be
        included.  This does not preserve the element object ids of the contents.

        @return a SPAN element unattached to the DOM, containing the range
                contents.
        """
        res = self.m_document.createSpanElement()
        self.extractContents(res)
        return res


    def extractContents(self, copyInto):
        """
        Place the contents of this range into the given element, removing them
        from the DOM.  All tags required to make the range complete will be
        included.  This does not preserve the element object ids of the contents.

        @param copyInto an element to extract the contents into, ie
                        DOM.createSpanElement()
        """
        self.ensureRange()
        extractContents(self.m_range, copyInto)


    def getCommonAncestor(self):
        """*
        Get the element that is the lowest common ancestor of both ends of the
        range.  In other words, the smallest element that includes the range.

        @return the element that completely encompasses this range
        """
        self.ensureRange()
        return getCommonAncestor(self.m_range)


    def getCursor(self):
        """
        Gets a single point of the cursor location if this is a cursor, otherwise
        returns None.

        @return the single point if this is a cursor and not a selection
        """
        return self.isCursor() and self.m_startPoint or None


    def getDocument(self):
        """
        Get the DOM Document this range is within

        @return document this range is in
        """
        return self.m_document


    def getEndPoint(self):
        """
        Get the end point of the range.  Not a copy, so changing this alters
        the range.

        @return the end point object
        """
        self.ensureEndPoints()
        return self.m_endPoint


    def getHtmlText(self):
        """
        Gets an HTML string represnting all elements enclosed by this range.

        @return An html string of this range
        """
        self.ensureRange()
        return getHtmlText(self.m_range)


    def getJSRange(self):
        """
        Get the JS object representing this range.  Since it is highly browser
        dependent, it is not recommended to operate on this

        @return JavaScriptObject representing this range
        """
        self.ensureRange()
        return self.m_range


    def getStartPoint(self):
        """
        Get the start point of the range.  Not a copy, so changing this alters
        the range.

        @return the start point object
        """
        self.ensureEndPoints()
        return self.m_startPoint


    def getText(self):
        """
        Gets the plain text that is enclosed by this range

        @return A string of the text in this range
        """
        self.ensureRange()
        return getText(self.m_range)


    def isCursor(self):
        """
        Returns whether this is a cursor, ie the start and end point are equal

        @return True if start == end
        """
        self.ensureEndPoints()
        return self.m_startPoint.equals(self.m_endPoint)


    def minimizeTextNodes(self):
        """
        Minimize the number of text nodes included in this range.  If the start
        point is at the end of a text node, move it to the beginning of the
        next text node; vice versa for the end point.  The result should ensure
        no text nodes with 0 included characters.
        """
        self.ensureEndPoints()
        self.m_startPoint.minimizeBoundaryTextNodes(True)
        self.m_endPoint.minimizeBoundaryTextNodes(False)


    def moveToBoundary(self, topMostNode, type):
        """
        TODO NOT IMPLEMENTED YET
        Move the end points to encompass a boundary type, such as a word.

        @param topMostNode a Node not to traverse above, or None
        @param type unit to move boundary by, such as RangeEndPoint.MOVE_WORD
        """
        self.ensureEndPoints()
        self.m_startPoint.move(False, topMostNode, None, type, 1)
        self.m_endPoint.move(True, topMostNode, None, type, 1)


    def setCursor(self, cursorPoint):
        """
        Sets the range to a point cursor.

        @param cursorPoint A single endpoint to create a cursor range at
        """
        self.setRange(cursorPoint, cursorPoint)


    def setEndPoint(self, endPoint):
        """
        Sets just the end point of the range.  New endPoint must reside within
        the same document as the current startpoint, and must occur after it.

        @param startPoint New start point for this range
        """
        assert ((self.m_startPoint is not None)  or
        (endPoint.getNode().getOwnerDocument() == self.m_document))
        self.m_endPoint = endPoint
        self.m_range = None


    def setRange(self, arg1, arg2=None):
        """
        Sets the range to encompass the given element.  May not work around
        non-text containing elements.

        @param element Element to surround by this range
        @return whether a range can be placed around this element.

        Set the range to be between the two given points.  Both points must be
        within the same document, and end must come after start.

        @param startPoint Start point to set the range to
        @param endPoint End point to set the range to
        """
        if arg2 is None:
            firstText = RangeUtil.getAdjacentTextElement(arg1, arg1, True, False)
            lastText = RangeUtil.getAdjacentTextElement(arg1, arg1, False, False)

            if (firstText is None)  or  (lastText is None):
                return False

            startPoint = RangeEndPoint(firstText, 0)
            endPoint = RangeEndPoint(lastText, lastText.length)

        else:
            startPoint = arg1
            endPoint = arg2

        assert (startPoint.getNode().ownerDocument ==
                    endPoint.getNode().ownerDocument)

        self._setRange(startPoint, endPoint)
        self.m_range = None

    def setStartPoint(self, startPoint):
        """
        Sets just the start point of the range.  New startPoint must reside within
        the same document as the current endpoint, and must occur before it.

        @param startPoint New start point for this range
        """
        assert ((self.m_endPoint is not None)  and
                (startPoint.getNode().getOwnerDocument() == self.m_document))

        self.m_startPoint = startPoint
        self.m_range = None


    def surroundContents(self, copyInto=None):
        """
        Surround all of the contents of the range with the given element, which
        replaces the content in the DOM.  All tags required to make the range
        complete are included in the child content.  This does not preserve the
        element object ids of the contents.  The range will surround this
        element after this operation.

        @param copyInto an element to place the contents into, which will replace
                        them in the DOM after this operation
        """

        if copyInto is None:
            copyInto = self.m_document.createElement("span")
        self.ensureRange()
        surroundContents(self.m_range, copyInto)
        self.setRange(copyInto)


    def ensureEndPoints(self):
        """
        Ensure the end points exists and are consisent with the javascript range
        """
        if (self.m_startPoint is None)  or  (self.m_endPoint is None):
            fillRangePoints(self)
            self.setupLastEndpoints()



    def ensureRange(self):
        """
        Ensure the javascript range exists and is consistent with the end points
        """
        if self.rangeNeedsUpdate():
            self.m_range = createRange(self.m_document,
                                                self.m_startPoint.getTextNode(),
                                                self.m_startPoint.getOffset(),
                                                self.m_endPoint.getTextNode(),
                                                self.m_endPoint.getOffset())
            self.setupLastEndpoints()



    def rangeNeedsUpdate(self):
        return (self.m_range is None)  or  \
        ((self.m_startPoint is not None)  and  \
        ((self.m_lastStartPoint is None)  or  \
        not self.m_lastStartPoint.equals(self.m_startPoint)  or  \
        (self.m_lastEndPoint is None)  or  \
        not self.m_lastEndPoint.equals(self.m_endPoint)))


    def setupLastEndpoints(self):
        self.m_lastStartPoint = RangeEndPoint(self.m_startPoint)
        self.m_lastEndPoint = RangeEndPoint(self.m_endPoint)
        #print "setupLastEndpoints:", self.m_lastStartPoint, self.m_lastEndPoint


    def setDocument(self, doc):
        """
        Set the document this range is contained within

        @param doc document to set
        """
        if self.m_document != doc:
            self.m_document = doc
            self.m_range = createFromDocument(doc)



def canonicalize(start, end):
    pass

def collapseRange(rng, start):
    pass

def createRangeOnFirst(parent):
    pass

def createRangeOnText(setText, offset):
    pass

def getRangeEndPoint(rng, selRange, start):
    pass

def getTestElement(document):
    pass

def moveCharacter(rng, chars):
    pass

def moveEndCharacter(rng, chars):
    pass

def moveRangePoint(rng, moveTo, how):
    pass

def moveToElementText(rng, element):
    pass

def placeholdPaste(rng, str):
    pass

def placeholdRange(rng):
    pass

