#""
# Copyright 2010 John Kozura
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#""





#""*
# IE implementation of selection, which emulates the methods of the W3C
# standard.
#
# @author John Kozura
#""

def clear(selection):
    selection.empty()


def getJSRange(doc, selection):
    """*
    * Get the range, and double check that it is actually parented by this
    * document.  If not, then return None.  Also uses duplicate to ensure that
    * the range is decoupled from the selection.
    *
    * @see SelectionImpl#getJSRange
    """
    res = selection.createRange()

    parent = res.parentElement()
    if parent.ownerDocument == doc:
        return res.duplicate()

    return None


def getSelection(window):
    return window.document.selection


def isEmpty(selection):
    return selection.type == "None"


def setJSRange(selection, rng):
    rng.select()


