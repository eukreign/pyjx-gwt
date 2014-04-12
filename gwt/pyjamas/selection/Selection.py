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

from __pyjamas__ import wnd

import SelectionImpl
from Range import Range

START_NODE	= "startContainer"
START_OFFSET	= "startOffset"
END_NODE		= "endContainer"
END_OFFSET	= "endOffset"
IS_COLLAPSED 	= "isCollapsed"


"""*
* A selection within a particular document.  Holds the singleton for a
* particlar document/window for getting and setting the selection.
*
* @author John Kozura
"""

m_selection = None
m_document = None

"""*
* Clears or removes any current text selection.
"""
def clearAnySelectedText():
    getSelection()
    clear()

"""*
* Convenience for getting the range for the current browser selection
*
* @return A range object representing the browser window's selection
"""
def getBrowserRange():
    getSelection()
    return getRange()


"""*
* Returns the selection for a given window, for instance an iframe
*
* @return The singleton instance
"""
def getSelection(window=None):
    global m_selection
    global m_document
    if window is None:
        window = getWindow()
    m_selection = SelectionImpl.getSelection(window)
    m_document = getDocument(window)


def getWindow():
    return wnd()


"""*
* Clears any current selection.
"""
def clear():
    SelectionImpl.clear(m_selection)

"""*
* Gets the parent document associated with this selection.  Could be
* different from the browser document if, for example this is the selection
* within an iframe.
*
* @return parent document of this selection
"""
def getDocument(window=None):
    if window:
        #print "getDocument", window, window.document
        return window.document
    #print "getDocument", m_document
    return m_document

"""*
* Get the javascript object representing the selection.  Since this is
* browser dependent object, should probably not use self.
*
* @return a JavaScriptObject representing this selection
"""
def getJSSelection():
    return m_selection

"""*
* Gets the range associated with the given selection.  The endpoints are
* captured immediately, so any changes to the selection will not affect
* the returned range.  In some browsers (IE) this can return NULL if
* nothing is selected in the document.
*
* @return A range object capturing the current selection
"""
def getRange():
    jsRange = SelectionImpl.getJSRange(m_document, m_selection)
    if jsRange is None:
        return None
    res = Range(m_document, jsRange)
    res.ensureEndPoints()

    return res


"""*
* Tests if anything is currently being selected
*
* @return True if empty False otherwise
"""
def isEmpty():
    return Selection.getImpl().isEmpty(m_selection)


"""*
* Takes a range object and pushes it to be the selection.  The range
* must be parented by the same window/document as the selection.  The range
* remains separate from the selection after this operation; any changes to
* the range are not reflected in the selection, and vice versa.
*
* @param newSelection What the selection should be
"""
def setRange(newSelection):
    if newSelection.getDocument() == m_document:
        SelectionImpl.setJSRange(m_selection, newSelection.getJSRange())

