"""
* Copyright 2010 John Kozura
*
* Licensed under the Apache License, Version 2.0 (the "License"); you may not
* use this file except in compliance with the License. You may obtain a copy of
* the License at
*
* http:#www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
* License for the specific language governing permissions and limitations under
* the License.
"""

from pyjamas import DOM

"""*
* Returns the next adjacent text node in the given direction.  Will move
* down the hierarchy (if traversingUp is not set), then through siblings,
* then up (but not past topMostNode), looking for the first node
*
* This could be non-statically included in the Node class
*
* @param current An element to start the search from, can be any type
*                of node.
* @param topMostNode A node that this will traverse no higher than
* @param forward whether to search forward or backward
* @param traversingUp if True, will not look at the children of this element
* @return the next (previous) text node, or None if no more
*
* may also be called as getAdjacentTextElement(current, forward) with
* only 2 parameters.
"""
def getAdjacentTextElement(current, topMostNode, forward=None, traversingUp=False):
    if forward is None:
        forward = topMostNode
        topMostNode = None

    res = None

    #print "getAdjacentTextElement", current, topMostNode, forward, traversingUp

    # If traversingUp, then the children have already been processed
    if not traversingUp:
        if DOM.getChildCount(current) > 0:
            if forward:
                node = DOM.getFirstChild(current)
            else:
                node = DOM.getLastChild(current)

            if DOM.getNodeType(node) == DOM.TEXT_NODE:
                res = node
            else:
                # Depth first traversal, the recursive call deals with
                # siblings
                res = getAdjacentTextElement(node, topMostNode,
                                        forward, False)

    if res is None:
        if forward:
            node = current.nextSibling
        else:
            node = current.previousSibling
        # Traverse siblings
        if node is not None:
            if DOM.getNodeType(node) == DOM.TEXT_NODE:
                res = node
            else:
                #print node, DOM.getNodeType(node), node.innerHTML
                # Depth first traversal, the recursive call deals with
                # siblings
                res = getAdjacentTextElement(node, topMostNode,
                                        forward, False)

    # Go up and over if still not found
    if (res is None)  and  (not DOM.compare(current, topMostNode)):
        node = current.parentNode
        # Stop at document (technically could stop at "html" tag)
        if (node is not None)  and  \
                (DOM.getNodeType(node) != DOM.DOCUMENT_NODE):
            res = getAdjacentTextElement(node, topMostNode,
                                        forward, True)
    return res

