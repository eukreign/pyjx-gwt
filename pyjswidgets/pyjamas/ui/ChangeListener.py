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


def fireChangeEvent(listeners, sender, event):
    etype = DOM.eventGetType(event)
    if etype != "change":
        return
    for listener in listeners:
        if hasattr(listener, 'onChange'):
            listener.onChange(sender)
        else:
            listener(sender)


class ChangeHandler(object):

    def __init__(self):

        self._changeListeners = []
        self.sinkEvents(Event.ONCHANGE)

    def onBrowserEvent(self, event):
        etype = DOM.eventGetType(event)
        if etype == 'change':
            fireChangeEvent(self._changeListeners, self, event)

    def addChangeListener(self, listener):
        self._changeListeners.append(listener)

    def removeChangeListener(self, listener):
        self._changeListeners.remove(listener)

    def onChange(self, sender):
        pass

