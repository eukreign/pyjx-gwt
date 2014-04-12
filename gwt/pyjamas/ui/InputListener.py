# Copyright (C) 2009, 2012 Luke Kenneth Casson Leighton <lkcl@lkcl.net>
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
from pyjamas.ui import Event


def fireInputEvent(listeners, sender, event):
    etype = DOM.eventGetType(event)
    if etype != "input":
        return
    for listener in listeners:
        if hasattr(listener, 'onInput'):
            listener.onInput(sender)
        else:
            listener(sender)


class InputHandler(object):

    def __init__(self):

        self._inputListeners = []
        self.sinkEvents(Event.ONINPUT)

    def onBrowserEvent(self, event):
        etype = DOM.eventGetType(event)
        if etype == 'input':
            fireInputEvent(self._inputListeners, self, event)

    def addInputListener(self, listener):
        self._inputListeners.append(listener)

    def removeInputListener(self, listener):
        self._inputListeners.remove(listener)

    def onInput(self, sender):
        pass

